#!/usr/bin/env python3
"""Private, read-only LuHm art intake: receipts without publishing donor media.

One-pass SHA256 verification, ZIP safety checks, catalog reconciliation, GLB/BLEND
headers. No extraction, script execution, network access, key access or promotion.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import io
import json
import re
import stat
import struct
from pathlib import Path
from zipfile import ZipFile, ZIP_STORED, ZipInfo

MAX_FILES = 4000
MAX_ENTRY = 128 * 1024 * 1024
MAX_TOTAL = 512 * 1024 * 1024
MAX_RATIO = 1000
PRIVATE_REVIEW = {".rar", ".blend", ".glb", ".fbx", ".psd", ".kra", ".aseprite"}
SOURCE_REVIEW = {".py", ".js", ".gd", ".html", ".sh", ".bat", ".exe"}
FONT_HOLD = {".ttf", ".otf", ".woff", ".woff2"}
HEX64 = re.compile(r"[a-f0-9]{64}\Z")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def whole_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def safe_name(name: str) -> bool:
    parts = name.split("/")
    return (bool(name) and len(name) <= 350 and not name.startswith("/")
            and "\\" not in name and "\0" not in name
            and not re.search(r"[\x00-\x1f\x7f]", name)
            and all(p not in ("", ".", "..") for p in parts)
            and all(":" not in p for p in parts))


def entry_error(record: ZipInfo) -> list[str]:
    errors = []
    name = record.filename
    if not safe_name(name.rstrip("/") if record.is_dir() else name):
        errors.append("UNSAFE_PATH")
    mode = (record.external_attr >> 16) & 0o170000
    if mode not in (0, stat.S_IFREG, stat.S_IFDIR):
        errors.append("SPECIAL_FILE_OR_SYMLINK")
    if record.flag_bits & 0x1:
        errors.append("ENCRYPTED_ARCHIVE_ENTRY")
    if record.file_size > MAX_ENTRY:
        errors.append("OVERSIZE_ARCHIVE_ENTRY")
    if record.file_size > 1024 * 1024 and record.file_size > max(record.compress_size, 1) * MAX_RATIO:
        errors.append("SUSPICIOUS_COMPRESSION_RATIO")
    return errors


def compare_catalog(z: ZipFile, names: set[str], catalog: dict) -> dict:
    issues = []
    entries = catalog.get("files")
    if not isinstance(entries, list) or len(entries) > MAX_FILES:
        return {"matches": False, "errors": ["INVALID_CATALOG_FILES"], "expectedAssets": 0}
    expected = {}
    for item in entries:
        if not isinstance(item, dict):
            issues.append("INVALID_CATALOG_RECORD")
            continue
        name = item.get("path", "")
        if not isinstance(name, str) or not safe_name(name) or name in expected:
            issues.append("INVALID_OR_DUPLICATE_CATALOG_NAME")
            continue
        expected[name] = item
    if names - set(expected) - {"assetCatalog.json"}:
        issues.append("ARCHIVE_CONTAINS_UNCATALOGED_FILES")
    if set(expected) - names:
        issues.append("CATALOG_FILES_MISSING")
    for name, item in expected.items():
        if name not in names:
            continue
        expected_digest = item.get("sha256", "")
        expected_size = item.get("bytes")
        if not isinstance(expected_digest, str) or not HEX64.fullmatch(expected_digest):
            issues.append("INVALID_DIGEST_IN_CATALOG")
            continue
        if not isinstance(expected_size, int) or isinstance(expected_size, bool):
            issues.append("INVALID_SIZE_IN_CATALOG")
            continue
        raw = z.read(name)
        if digest(raw) != expected_digest or len(raw) != expected_size:
            issues.append("BYTE_OR_SHA256_MISMATCH")
    return {
        "matches": not issues, "errors": sorted(set(issues)),
        "expectedAssets": len(expected),
        "checkedFiles": len(set(expected) & names),
        "approvedForPublic": sum(item.get("publicApproved") is True for item in expected.values()),
    }


def inspect_zip(path: Path, catalog: dict | None = None) -> dict:
    errors: list[str] = []
    categories = Counter()
    files = 0
    unpacked = 0
    private_review = 0
    scripts = 0
    fonts = 0
    license_signal = "NOT_VERIFIED"
    manifest = None
    with ZipFile(path) as z:
        entries = [p for p in z.infolist() if not p.is_dir()]
        names = set()
        normalized = set()
        if len(entries) > MAX_FILES:
            errors.append("TOO_MANY_FILES")
        for entry in z.infolist():
            errors.extend(entry_error(entry))
            if entry.is_dir():
                continue
            files += 1
            unpacked += entry.file_size
            name = entry.filename
            folded = name.casefold()
            if name in names or folded in normalized:
                errors.append("DUPLICATE_OR_CASE_COLLIDING_PATH")
            names.add(name)
            normalized.add(folded)
            ext = Path(name).suffix.lower()
            categories[ext or "(none)"] += 1
            private_review += int(ext in PRIVATE_REVIEW)
            scripts += int(ext in SOURCE_REVIEW)
            fonts += int(ext in FONT_HOLD)
        if unpacked > MAX_TOTAL:
            errors.append("EXCESSIVE_UNCOMPRESSED_TOTAL")
        if not errors:
            bad_crc = z.testzip()
            if bad_crc is not None:
                errors.append("CRC_VERIFICATION_FAILED")
            if catalog is not None:
                manifest = compare_catalog(z, names, catalog)
                errors.extend(manifest["errors"])
            licenses = [n for n in names if n.lower().endswith("license.txt")]
            if len(licenses) == 1:
                blob = z.read(licenses[0])[:16384].decode("utf8", errors="replace")
                if "CC0" in blob and "creativecommons.org/publicdomain/zero/1.0" in blob:
                    license_signal = "ARCHIVE_DECLARATION_CC0_1_0_UNVERIFIED_PROVENANCE"
    errors = sorted(set(errors))
    return {
        "kind": "ZIP",
        "entries": files,
        "uncompressedBytes": unpacked,
        "extensions": dict(sorted(categories.items())),
        "privateModelOrArchiveEntries": private_review,
        "sourceScriptsForReview": scripts,
        "fontFilesOnHold": fonts,
        "licenseSignal": license_signal,
        "catalog": manifest,
        "errors": errors,
        "integrity": "PASS" if not errors else "FAIL_QUARANTINE",
        "publicApproved": False,
    }


def inspect_binary(path: Path) -> dict:
    size = path.stat().st_size
    with path.open("rb") as h:
        top = h.read(24)
        if path.suffix.lower() == ".blend":
            assert top.startswith(b"BLENDER"), "INVALID_BLENDER_HEADER"
            return {"kind": "BLEND", "version": top[9:12].decode("ascii", "replace"),
                    "integrity": "HEADER_ONLY", "rigEvaluated": False, "externalTexturesVerified": False,
                    "godotImportVerified": False, "publicApproved": False}
        if path.suffix.lower() == ".rar":
            assert top.startswith(b"Rar!\x1a\x07\x01\x00"), "INVALID_RAR5_HEADER"
            return {"kind": "RAR5", "archiveEntriesInspected": False,
                    "extractionPerformed": False, "integrity": "HEADER_ONLY", "publicApproved": False}
        if path.suffix.lower() != ".glb":
            raise ValueError("UNSUPPORTED_PRIVATE_BINARY")
        magic, version, declared = struct.unpack_from("<4sII", top)
        assert magic == b"glTF" and version == 2 and declared == size, "INVALID_GLB_HEADER"
        first_len, first_type = struct.unpack_from("<II", top, 12)
        assert first_type == 0x4E4F534A and 0 < first_len <= 16 * 1024 * 1024, "INVALID_GLB_JSON_CHUNK"
        h.seek(20)
        gltf = json.loads(h.read(first_len).rstrip(b" \n\r\t\x00"))
        meshes = gltf.get("meshes", [])
        attrs = gltf.get("accessors", [])
        external = []
        for group in ("images", "buffers"):
            for node in gltf.get(group, []):
                uri = node.get("uri")
                if uri is not None and not str(uri).startswith("data:"):
                    external.append(str(uri)[:160])
        return {"kind": "GLB2", "meshes": len(meshes), "materials": len(gltf.get("materials", [])),
                "skins": len(gltf.get("skins", [])), "animations": len(gltf.get("animations", [])),
                "nodes": len(gltf.get("nodes", [])), "accessors": len(attrs),
                "externalUris": external, "integrity": "HEADER_ONLY", "runtimeImportVerified": False,
                "licenseVerified": False, "publicApproved": False}


def inspect(path: Path, catalog: dict | None = None) -> dict:
    record = {
        "sourceLabel": path.name,
        "sourceBytes": path.stat().st_size,
        "sha256": whole_hash(path),
        "rights": "REVIEW_REQUIRED",
        "canon": "UNAPPROVED",
        "authorityEffect": "NONE",
    }
    try:
        details = inspect_zip(path, catalog) if path.suffix.lower() == ".zip" else inspect_binary(path)
    except (AssertionError, ValueError, OSError, EOFError, RuntimeError) as exc:
        details = {"kind": "UNKNOWN", "integrity": "FAIL_QUARANTINE",
                   "errors": [type(exc).__name__ + ":" + str(exc)[:140]],
                   "publicApproved": False}
    return {**record, **details}


def self_test() -> None:
    from tempfile import TemporaryDirectory
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        png = b"\x89PNG\r\n\x1a\n" + b"A" * 24
        base = {"schema": "localTest", "files": [{"path": "ui/panel.png",
                "sha256": digest(png), "bytes": len(png), "publicApproved": False}]}
        archive = root / "valid.zip"
        with ZipFile(archive, "w") as z:
            z.writestr("ui/panel.png", png)
            z.writestr("assetCatalog.json", json.dumps(base))
        assert inspect_zip(archive, base)["integrity"] == "PASS"
        failures = [
            ("../escape.png", png, "UNSAFE_PATH"),
            ("/abs.png", png, "UNSAFE_PATH"),
            ("ui\\bad.png", png, "UNSAFE_PATH"),
            ("ui//bad.png", png, "UNSAFE_PATH"),
            ("ui/panel.png", b"tampered", "BYTE_OR_SHA256_MISMATCH"),
        ]
        for name, value, expected in failures:
            with ZipFile(archive, "w") as z:
                z.writestr(name, value)
                z.writestr("assetCatalog.json", json.dumps(base))
            assert expected in inspect_zip(archive, base)["errors"], expected
        with ZipFile(archive, "w") as z:
            z.writestr("ui/panel.png", png)
            z.writestr("ui/PANEL.PNG", png)
        assert "DUPLICATE_OR_CASE_COLLIDING_PATH" in inspect_zip(archive)["errors"]
        with ZipFile(archive, "w") as z:
            entry = ZipInfo("symlink.png")
            entry.create_system = 3
            entry.external_attr = (stat.S_IFLNK | 0o777) << 16
            z.writestr(entry, "private")
        assert "SPECIAL_FILE_OR_SYMLINK" in inspect_zip(archive)["errors"]
        with ZipFile(archive, "w") as z:
            z.writestr("ui/panel.png", png)
        assert "CATALOG_FILES_MISSING" not in inspect_zip(archive, base)["errors"]
        assert "BYTE_OR_SHA256_MISMATCH" not in inspect_zip(archive, base)["errors"]
        assert "ARCHIVE_CONTAINS_UNCATALOGED_FILES" not in inspect_zip(archive, base)["errors"]
        with ZipFile(archive, "w") as z:
            z.writestr("secret.glb", b"glTF")
        r = inspect_zip(archive)
        assert r["privateModelOrArchiveEntries"] == 1 and not r["publicApproved"]
    print("GREEN_ART_INTAKE_9_NEGATIVE_AND_POSITIVE_TESTS")
    print("NO_EXTRACTION_NO_EXECUTION_NO_PUBLIC_PROMOTION")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--archive", type=Path, action="append", default=[])
    p.add_argument("--file", type=Path, action="append", default=[])
    p.add_argument("--catalog", type=Path)
    p.add_argument("--output", type=Path)
    p.add_argument("--source-ref", default="UNKNOWN")
    args = p.parse_args()
    if args.self_test:
        self_test()
    if not args.archive and not args.file:
        return
    catalog = json.loads(args.catalog.read_text(encoding="utf8")) if args.catalog else None
    items = [inspect(path, catalog if i == 0 else None)
             for i, path in enumerate(args.archive)]
    items += [inspect(path) for path in args.file]
    output = {
        "schema": "luhmOs.privateArtIntegrityCheckpoint.v1",
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sourceRef": args.source_ref,
        "scope": "SELECTED_LOCAL_AND_AUTHORIZED_PRIVATE_ASSETS_ONLY",
        "publicPromotion": False,
        "workerDeployment": False,
        "licensingIsNotConferredByHashVerification": True,
        "assets": items,
        "archivesVerified": sum(x.get("integrity") == "PASS" for x in items),
        "headerOnlyFiles": sum(x.get("integrity") == "HEADER_ONLY" for x in items),
        "checksFailed": sum(x.get("integrity") not in {"PASS", "HEADER_ONLY"} for x in items),
        "crownStatus": "STOP"
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf8")
    print(json.dumps(output, indent=2))
    if output["checksFailed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""Unpack verified artwork ZIPs to a PRIVATE review folder, never a public repo.

No archive scripts are executed. No originals are deleted, no canon/public
approval is created, and no archive entry may escape its designated folder.
RAR/7z require separate reviewed tooling; they are not silently extracted.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
from tempfile import TemporaryDirectory
from zipfile import ZipFile, ZipInfo

LANES = {"audio", "backdrops", "docs", "godot", "models", "sprites", "ui", "vfx", "web"}
EXECUTABLE = {".py", ".js", ".mjs", ".sh", ".bat", ".ps1", ".exe", ".dll", ".gd"}
MAX_FILES = 4000
MAX_ENTRY = 128 * 1024 * 1024
MAX_TOTAL = 512 * 1024 * 1024

def checksum(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def safe_path(name: str) -> bool:
    p = PurePosixPath(name)
    return bool(name) and not name.startswith("/") and len(name) < 350 and not any(
        c in name for c in ("\x00", "\\", "\r", "\n", ":")
    ) and all(part not in ("", ".", "..") for part in name.split("/")) and not p.is_absolute()

def validate(z: ZipFile) -> list[ZipInfo]:
    items = [x for x in z.infolist() if not x.is_dir()]
    if not items or len(items) > MAX_FILES or sum(x.file_size for x in items) > MAX_TOTAL:
        raise ValueError("ARCHIVE_COUNT_OR_TOTAL_LIMIT")
    exact = set()
    folded = set()
    for item in z.infolist():
        name = item.filename.rstrip("/") if item.is_dir() else item.filename
        mode = (item.external_attr >> 16) & 0o170000
        if not safe_path(name) or mode not in (0, stat.S_IFREG, stat.S_IFDIR):
            raise ValueError("UNSAFE_PATH_OR_FILE_TYPE")
        if item.flag_bits & 1 or item.file_size > MAX_ENTRY:
            raise ValueError("ENCRYPTED_OR_LARGE_ENTRY")
        if item.file_size > 1024 * 1024 and item.file_size > max(item.compress_size, 1) * 1000:
            raise ValueError("SUSPICIOUS_COMPRESSION_RATIO")
        if not item.is_dir():
            if name in exact or name.casefold() in folded:
                raise ValueError("DUPLICATE_OR_CASE_COLLISION")
            exact.add(name)
            folded.add(name.casefold())
    if z.testzip() is not None:
        raise ValueError("CRC_MISMATCH")
    return items

def verify_catalog(z: ZipFile, items: list[ZipInfo]) -> dict:
    names = {x.filename for x in items}
    if "assetCatalog.json" not in names:
        return {"state": "NO_CATALOG_REVIEW_REQUIRED", "matched": 0}
    doc = json.loads(z.read("assetCatalog.json"))
    records = doc.get("files")
    if not isinstance(records, list) or len(records) > MAX_FILES:
        raise ValueError("INVALID_CATALOG")
    expected = {}
    for row in records:
        if not isinstance(row, dict) or row.get("path") in expected:
            raise ValueError("DUPLICATE_CATALOG_RECORD")
        expected[row["path"]] = row
    if names != set(expected) | {"assetCatalog.json"}:
        raise ValueError("CATALOG_ARCHIVE_SET_MISMATCH")
    for path, row in expected.items():
        content = z.read(path)
        if len(content) != row.get("bytes") or checksum(content) != row.get("sha256"):
            raise ValueError("CATALOG_HASH_OR_SIZE_MISMATCH")
        if row.get("publicApproved") is True:
            raise ValueError("REQUIRES_SEPARATE_HUMAN_PUBLIC_APPROVAL")
    return {"state": "PRIVATE_SHA256_CATALOG_PASS", "matched": len(expected)}

def category(name: str) -> str:
    suffix = Path(name).suffix.lower()
    if suffix in EXECUTABLE:
        return "quarantineScripts"
    first = name.split("/")[0]
    if first in LANES:
        return first
    if suffix in {".glb", ".gltf", ".fbx", ".obj", ".blend"}:
        return "models"
    if suffix in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".ase", ".aseprite"}:
        return "sprites"
    if suffix in {".wav", ".ogg", ".mp3", ".flac"}:
        return "audio"
    return "unclassified"

def unpack(src: Path, private_root: Path) -> dict:
    if not src.is_file() or src.suffix.lower() != ".zip":
        raise ValueError("ONLY_ZIP_SUPPORTED")
    resolved = private_root.resolve()
    repo = Path(__file__).resolve().parents[1]
    if resolved == repo or repo in resolved.parents:
        raise ValueError("PUBLIC_REPOSITORY_DESTINATION_FORBIDDEN")
    private_root.mkdir(parents=True, exist_ok=True)
    archive_digest = checksum(src.read_bytes())
    # The archive hash keeps re-imports idempotent without overwriting prior reviews.
    release_folder = private_root / ("zip_" + archive_digest[:16])
    if release_folder.exists():
        raise ValueError("DESTINATION_EXISTS_NO_SILENT_OVERWRITE")
    with ZipFile(src) as z:
        entries = validate(z)
        catalog = verify_catalog(z, entries)
        generated = []
        counts = Counter()
        for entry in entries:
            name = entry.filename
            lane = "manifests" if name == "assetCatalog.json" else category(name)
            out = release_folder / lane / name
            out.parent.mkdir(parents=True, exist_ok=True)
            raw = z.read(entry)
            if len(raw) != entry.file_size:
                raise ValueError("ARCHIVE_READ_TRUNCATED")
            out.write_bytes(raw)
            counts[lane] += 1
            generated.append({"sourcePath": name, "storedPath": str(out.relative_to(release_folder)),
                              "bytes": len(raw), "sha256": checksum(raw),
                              "lane": lane, "publicApproved": False, "canon": "UNREVIEWED"})
    receipt = {"schema": "luhmOs.privateZipExtraction.v1", "originalName": src.name,
               "sourceSha256": archive_digest, "catalog": catalog,
               "counts": dict(sorted(counts.items())), "files": generated,
               "publicApproved": False, "deployed": False,
               "autonomousAgents": False, "humanApproval": "PENDING"}
    (release_folder / "privateExtractionReceipt.json").write_text(
        json.dumps(receipt, indent=2) + "\n", encoding="utf8")
    return receipt

def self_test() -> None:
    from zipfile import ZipInfo
    with TemporaryDirectory() as td:
        root = Path(td)
        src = root / "source.zip"
        data = b"ART"
        catalog = {"files": [{"path": "sprites/lum.png", "bytes": 3,
                              "sha256": checksum(data), "publicApproved": False}]}
        with ZipFile(src, "w") as z:
            z.writestr("sprites/lum.png", data)
            z.writestr("assetCatalog.json", json.dumps(catalog))
        result = unpack(src, root / "private")
        assert result["catalog"]["matched"] == 1
        assert result["counts"]["sprites"] == 1
        try:
            unpack(src, root / "private")
            raise AssertionError("existing folder overwritten")
        except ValueError as e:
            assert "DESTINATION_EXISTS" in str(e)
        for name in ("../escape", "/absolute", "ui\\escape", "sprites//bad", "A:evil"):
            with ZipFile(src, "w") as z:
                z.writestr(name, data)
            try:
                unpack(src, root / "private" / name.replace("/", "_").replace("\\", "_"))
                raise AssertionError("unsafe name accepted " + name)
            except ValueError:
                pass
        with ZipFile(src, "w") as z:
            item = ZipInfo("symbols.png")
            item.create_system = 3
            item.external_attr = (stat.S_IFLNK | 0o777) << 16
            z.writestr(item, b"link")
        try:
            unpack(src, root / "private" / "symlink")
            raise AssertionError("symlink accepted")
        except ValueError:
            pass
    print("GREEN_PRIVATE_ZIP_SORTER_8_NEGATIVE_AND_POSITIVE_CONTROLS")

def main() -> None:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--self-test", action="store_true")
    cli.add_argument("--archive", action="append", type=Path, default=[])
    cli.add_argument("--private-root", type=Path)
    args = cli.parse_args()
    if args.self_test:
        self_test()
    if args.archive:
        if args.private_root is None:
            cli.error("--private-root is required; do not extract into the GitHub repo")
        for archive in args.archive:
            x = unpack(archive, args.private_root)
            print(json.dumps({"source": x["originalName"], "entries": len(x["files"]),
                              "counts": x["counts"], "canon": "UNREVIEWED"}))

if __name__ == "__main__":
    main()

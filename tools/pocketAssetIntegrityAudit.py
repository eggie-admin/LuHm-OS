#!/usr/bin/env python3
"""Pocket Art Studio: exact manifest/catalog gate and optional actual ZIP verification.

CI uses the source-only checks. Run --archive path/to/pack.zip on the complete
private bundle to validate CRC, SHA-256, file signatures and package contents.
This is neither a Godot device smoke nor provider/plugin execution proof.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
from pathlib import Path, PurePosixPath
import json
import re
import struct
import sys
import wave
import zipfile
import io
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "plugins/luhm-os/assets/pocketArtPackV1.json"
CATALOG = ROOT / "plugins/luhm-os/assets/assetCatalog.json"
HEX = re.compile(r"^[0-9a-f]{64}$")
ALLOWED = {
    "ui": {".svg"},
    "backdrops": {".webp"},
    "vfx": {".png"},
    "sprites": {".png"},
    "audio": {".wav"},
    "models": {".glb"},
    "godot": {".gd", ".godot", ".tscn", ".png"},
    "docs": {".md", ".json"},
    "web": {".html"},
}

def inspect(archive: Path | None) -> dict:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    approved_receipt = json.loads((ROOT / "plugins/luhm-os/assets/pocketAssetIntegrityReceipt.json").read_text(encoding="utf-8"))
    checks = 0
    errors = []

    def require(name: str, expression: bool):
        nonlocal checks
        checks += 1
        if not expression:
            errors.append(name)

    rows = catalog.get("files")
    require("manifestSchema", manifest.get("schema") == "luhmOs.pocketArtAssetPack.v1")
    require("catalogSchema", catalog.get("schema") == "luhmOs.assetStudioCatalog.v1")
    require("noCanonPromotion", catalog.get("canonStatus") == "NOT_FINAL_CANON")
    require("noRuntimeClaim", catalog.get("runtimeProof") == "NOT_TESTED")
    require("noAgentExecution", catalog.get("autonomousAgents") == "NOT_EXECUTED")
    require("noExternalAssetsClaim", catalog.get("rights") == "no third-party binaries included")
    require("privateSourceBoundary", manifest.get("sourceOfTruth") == "Google Drive owner-only Rebel production vault")
    require("manifestCount", manifest.get("assetCount") == 110)
    require("catalogCount", isinstance(rows, list) and len(rows) == 110)
    require("zipHashSyntax", isinstance(manifest.get("sourcePackSha256"), str)
            and bool(HEX.fullmatch(manifest["sourcePackSha256"])))
    require("manifestCounts", manifest.get("counts") == catalog.get("categories"))
    require("categorySum", sum(catalog.get("categories", {}).values()) == 110)
    require("publicReleaseNotApproved", manifest.get("safety", {}).get("autoRelease") is False)
    require("privateRebelNotPackaged", manifest.get("safety", {}).get("privateRebelMedia") is False)
    require("noRemoteModels", manifest.get("safety", {}).get("liveModelCalls") is False)
    require("noCredentialClaim", manifest.get("safety", {}).get("secrets") is False)
    require("onlyOriginalDrafts", catalog.get("files") is not None)
    require("targetPrivatePluginVersion", manifest.get("targetPluginVersion") == "1.0.5")
    require("privatePluginReadback", manifest.get("privatePluginReleaseState") == "UPDATED_AND_READBACK_VERIFIED")
    require("receiptSourceLink", manifest.get("localIntegrityReceipt") == "plugins/luhm-os/assets/pocketAssetIntegrityReceipt.json")
    require("receiptStatus", approved_receipt.get("status") == "PASS")
    require("receiptByteChecks", approved_receipt.get("checksTotal") == approved_receipt.get("checksPassed") == 557)
    require("receiptCount", approved_receipt.get("assetCount") == 110)
    require("receiptArchiveHash", approved_receipt.get("archiveSha256") == manifest.get("sourcePackSha256"))
    require("receiptNoPublicAuthority", approved_receipt.get("publicApproval") is False)
    require("receiptRuntimeNotClaimed", approved_receipt.get("runtimeProof") == {"godot": False, "android": False, "inChat": False, "autonomousAgents": False})


    counts = Counter()
    paths = set()
    if not isinstance(rows, list):
        rows = []
    for index, item in enumerate(rows):
        if not isinstance(item, dict):
            require("rowObject:" + str(index), False)
            continue
        path = item.get("path")
        # Simple conservative, cross-platform path checks.
        valid_path = (
            isinstance(path, str)
            and path != ""
            and not path.startswith("/")
            and not path.startswith("./")
            and not any(p in ("", ".", "..") for p in path.split("/"))
            and "\\" not in path
            and "\x00" not in path
            and not re.match(r"^[A-Za-z]:", path)
        )
        require("safePath:"+str(index), valid_path)
        require("uniquePath:"+str(index), valid_path and path not in paths)
        if valid_path:
            paths.add(path)
            group = path.split("/")[0]
            counts[group] += 1
            require("allowedType:"+str(index),
                    group in ALLOWED and PurePosixPath(path).suffix.lower() in ALLOWED[group])
        else:
            require("allowedType:"+str(index), False)
        size = item.get("bytes")
        require("boundedSize:"+str(index), type(size) is int and 1 <= size <= 25_000_000)
        digest = item.get("sha256")
        require("validDigest:"+str(index), isinstance(digest, str) and bool(HEX.fullmatch(digest)))
        require("draftStatus:"+str(index), item.get("status") == "originalDraftCandidate")
        require("sourceOwnership:"+str(index), item.get("licenseReview") == "projectGenerated")
        require("publicationHeld:"+str(index), item.get("publicApproved") is False)
    for kind, expected in manifest.get("counts", {}).items():
        require("categoryCount:"+kind, counts[kind] == expected)
    require("exactDeclaredCategories", set(counts) == set(ALLOWED))
    require("noCatalogPartial", len(paths) == 110)
    require("sampleStarterPaths", all(x in paths for x in (
       "models/lum-orb-PROXY-not-canon.glb",
       "godot/project.godot", "godot/Main.tscn", "godot/Main.gd",
       "web/index.html")))

    if archive is not None:
        require("bundleExists", archive.is_file())
        if archive.is_file():
            require("bundleDigest", sha256(archive.read_bytes()).hexdigest() == manifest["sourcePackSha256"])
            try:
                with zipfile.ZipFile(archive) as z:
                    members = z.namelist()
                    require("zipNoDuplicateNames", len(set(members)) == len(members))
                    require("zipExactContents", set(members) == paths | {"assetCatalog.json"})
                    require("zipCRC", z.testzip() is None)
                    require("embeddedCatalogMatches", json.loads(z.read("assetCatalog.json")) == catalog)
                    for row in rows:
                        name = row.get("path")
                        if name not in members:
                            require("bundleEntry:"+str(name), False)
                            continue
                        data = z.read(name)
                        require("bundleBytes:"+name, len(data) == row["bytes"])
                        require("bundleSHA:"+name, sha256(data).hexdigest() == row["sha256"])
                        ext = PurePosixPath(name).suffix.lower()
                        valid = True
                        if ext == ".png":
                            valid = data.startswith(b"\x89PNG\r\n\x1a\n")
                        elif ext == ".webp":
                            valid = data[:4] == b"RIFF" and data[8:12] == b"WEBP"
                        elif ext == ".wav":
                            try:
                                with wave.open(io.BytesIO(data)) as w:
                                    valid = w.getnframes() > 0 and w.getframerate() >= 8000
                            except (wave.Error, EOFError):
                                valid = False
                        elif ext == ".glb":
                            valid = (len(data) >= 20 and data[:4] == b"glTF"
                                     and struct.unpack_from("<II", data, 4) == (2, len(data)))
                        elif ext == ".svg":
                            try:
                                valid = ET.fromstring(data).tag.endswith("svg")
                            except ET.ParseError:
                                valid = False
                        elif ext in (".json", ".gd", ".tscn", ".godot", ".html", ".md"):
                            try:
                                text = data.decode("utf-8")
                                if ext == ".json":
                                    json.loads(text)
                                valid = bool(text.strip())
                            except (UnicodeError, ValueError):
                                valid = False
                        require("signature:"+name, valid)
            except (OSError, zipfile.BadZipFile, KeyError, ValueError, TypeError) as exc:
                errors.append("archiveUnreadable:" + type(exc).__name__)

    result = {
      "schema": "luhmOs.pocketAssetIntegrityReceipt.v1",
      "status": "PASS" if not errors else "FAIL",
      "checksPassed": checks-len(errors),
      "checksTotal": checks,
      "items": len(rows),
      "archiveVerified": archive is not None and archive.is_file() and not errors,
      "assetPromotionAuthority": False,
      "godotRuntimeProven": False,
      "browserProven": False,
      "agentsExecuted": False,
      "errors": errors[:30],
    }
    return result

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--archive", type=Path, help="Optional private ZIP to verify exact content")
    a = p.parse_args()
    receipt = inspect(a.archive)
    print(json.dumps(receipt, indent=2))
    return 0 if receipt["status"] == "PASS" and receipt["checksTotal"] >= 750 else 1

if __name__ == "__main__":
    sys.exit(main())

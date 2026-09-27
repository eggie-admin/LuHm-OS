#!/usr/bin/env python3
"""Stage Professor-owned Nexus assets into a local, ignored Godot sidecar.

This tool NEVER downloads from Nexus. It copies only files already present in a
user-supplied local directory, validates hashes/rights metadata, accepts GLB v2
for Godot runtime, and writes a provenance receipt. Unknown rights fail closed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "assets" / "nexus" / "runtime"
BUILD = ROOT / "build" / "nexus-assets"
ALLOWED_RIGHTS = {"PRIVATE_PERSONAL_REFERENCE", "REDISTRIBUTABLE_WITH_EVIDENCE"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_glb(path: Path) -> None:
    data = path.read_bytes()
    if len(data) < 12:
        raise RuntimeError(f"{path.name}: GLB too small")
    magic, version, length = struct.unpack_from("<4sII", data, 0)
    if magic != b"glTF" or version != 2 or length != len(data):
        raise RuntimeError(f"{path.name}: invalid GLB v2 envelope")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--source-dir", required=True, type=Path)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    if manifest.get("policy") != "LOCAL_PERMISSION_GATED_NO_AUTODOWNLOAD":
        raise RuntimeError("manifest policy mismatch")
    if manifest.get("runtime_network") is not False:
        raise RuntimeError("runtime_network must be false")

    source_dir = args.source_dir.resolve()
    if not source_dir.is_dir():
        raise RuntimeError("source directory does not exist")

    shutil.rmtree(RUNTIME, ignore_errors=True)
    RUNTIME.mkdir(parents=True, exist_ok=True)
    BUILD.mkdir(parents=True, exist_ok=True)

    receipt_assets = []
    for raw in manifest.get("items", []):
        if not isinstance(raw, dict):
            raise RuntimeError("asset row must be an object")
        source_name = str(raw.get("source_file", ""))
        if not source_name or Path(source_name).name != source_name:
            raise RuntimeError(f"unsafe source_file: {source_name!r}")
        if not source_name.lower().endswith(".glb"):
            raise RuntimeError(f"{source_name}: normalize to GLB before Godot staging")

        rights = raw.get("rights", {})
        mode = str(rights.get("mode", ""))
        if mode not in ALLOWED_RIGHTS:
            raise RuntimeError(f"{source_name}: unsupported rights mode")
        evidence = str(rights.get("permission_evidence", "")).strip()
        if not evidence:
            raise RuntimeError(f"{source_name}: permission evidence required")
        if rights.get("allow_git") is not False:
            raise RuntimeError(f"{source_name}: Nexus payloads may not enter Git through this lane")
        if mode == "PRIVATE_PERSONAL_REFERENCE" and rights.get("allow_shared_apk") is not False:
            raise RuntimeError(f"{source_name}: private reference cannot enter shared APK")

        source = (source_dir / source_name).resolve()
        if source.parent != source_dir or not source.is_file():
            raise RuntimeError(f"{source_name}: source file missing")
        actual_sha = sha256_file(source)
        expected_sha = str(raw.get("sha256", "")).lower()
        if not re_full_sha(expected_sha) or actual_sha != expected_sha:
            raise RuntimeError(f"{source_name}: SHA256 mismatch")
        validate_glb(source)

        target = RUNTIME / source_name
        shutil.copy2(source, target)
        placement = raw.get("placement", {})
        receipt_assets.append({
            "id": str(raw.get("id", source.stem)),
            "runtime_path": f"res://assets/nexus/runtime/{source_name}",
            "sha256": actual_sha,
            "rights_mode": mode,
            "permission_evidence": evidence,
            "nexus": raw.get("nexus", {}),
            "placement": placement if isinstance(placement, dict) else {},
        })

    receipt = {
        "schema": "luhm-os.nexus-private-build-receipt.v1",
        "runtime_network": False,
        "asset_count": len(receipt_assets),
        "assets": receipt_assets,
    }
    encoded = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    (RUNTIME / "PROVENANCE.json").write_text(encoded, encoding="utf-8")
    (BUILD / "receipt.json").write_text(encoded, encoding="utf-8")
    print(f"NEXUS_PRIVATE_STAGE=PASS count={len(receipt_assets)}")
    return 0


def re_full_sha(value: str) -> bool:
    return len(value) == 64 and all(ch in "0123456789abcdef" for ch in value)


if __name__ == "__main__":
    raise SystemExit(main())

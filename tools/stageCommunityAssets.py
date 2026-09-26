#!/usr/bin/env python3
"""Stage a pinned, CC0-only community asset subset for the Android candidate build.

This is a build-time fetcher. It never runs in the APK and never performs runtime downloads.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import struct
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "assets/community/selected-assets.json"
OUT = ROOT / "assets/community/runtime"
BUILD = ROOT / "build/community-assets"
USER_AGENT = "LuHmOS-CommunityAssetForge/1.0"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_glb(data: bytes, label: str) -> None:
    if len(data) < 12:
        raise RuntimeError(f"{label}: GLB too small")
    magic, version, length = struct.unpack_from("<4sII", data, 0)
    if magic != b"glTF" or version != 2 or length != len(data):
        raise RuntimeError(f"{label}: invalid GLB v2 envelope")


def fetch(url: str, attempts: int = 4) -> bytes:
    last = None
    for attempt in range(1, attempts + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=45) as response:
                if response.status != 200:
                    raise RuntimeError(f"HTTP {response.status}")
                return response.read()
        except Exception as exc:  # deterministic retry envelope around transient network failures
            last = exc
            if attempt < attempts:
                time.sleep(attempt * 1.5)
    raise RuntimeError(f"fetch failed: {url}: {last}")


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    source = manifest["source"]
    if source["repository"] != "shorepine/kenney":
        raise RuntimeError("unapproved source repository")
    commit = source["commit"]
    if len(commit) != 40 or any(c not in "0123456789abcdef" for c in commit):
        raise RuntimeError("source commit must be immutable full SHA")
    if source["license"] != "CC0" or source["runtime_network"] is not False:
        raise RuntimeError("license/runtime-network contract failed")

    selected = []
    for kit, names in manifest["groups"].items():
        for name in names:
            if not name.endswith(".glb") or "/" in name or "\\" in name:
                raise RuntimeError(f"unsafe asset name: {name}")
            selected.append((kit, name))

    budget = manifest["budget"]
    if len(selected) > int(budget["max_assets"]):
        raise RuntimeError("asset count exceeds Android budget")

    shutil.rmtree(OUT, ignore_errors=True)
    OUT.mkdir(parents=True, exist_ok=True)
    BUILD.mkdir(parents=True, exist_ok=True)

    base = f"https://raw.githubusercontent.com/{source['repository']}/{commit}"
    receipts = []
    total = 0
    for kit, name in selected:
        source_path = f"3d/{kit}/{name}"
        url = f"{base}/{source_path}"
        data = fetch(url)
        validate_glb(data, source_path)
        total += len(data)
        if total > int(budget["max_total_bytes"]):
            raise RuntimeError("asset bytes exceed Android budget")
        target_dir = OUT / kit
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / name
        target.write_bytes(data)
        receipts.append({
            "kit": kit,
            "name": name,
            "source_path": source_path,
            "source_url": url,
            "runtime_path": f"res://assets/community/runtime/{kit}/{name}",
            "bytes": len(data),
            "sha256": sha256(data),
        })
        print(f"STAGED {kit}/{name} {len(data)} {receipts[-1]['sha256'][:12]}")

    license_url = f"{base}/{source['license_path']}"
    license_bytes = fetch(license_url)
    (OUT / "KENNEY_LICENSE.txt").write_bytes(license_bytes)

    receipt = {
        "schema": "luhm-os.community-asset-build-receipt.v1",
        "source_repository": source["repository"],
        "source_commit": commit,
        "license": source["license"],
        "license_url": license_url,
        "asset_count": len(receipts),
        "total_asset_bytes": total,
        "runtime_network": False,
        "assets": receipts,
    }
    encoded = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    (OUT / "PROVENANCE.json").write_text(encoded, encoding="utf-8")
    (BUILD / "receipt.json").write_text(encoded, encoding="utf-8")
    print(f"COMMUNITY_ASSET_STAGE=PASS count={len(receipts)} bytes={total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

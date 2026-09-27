#!/usr/bin/env python3
"""Stage LuHm OS full-game donor art from the private Drive donor vault.

KAI9000 is a donor inventory only. It has no runtime or doctrine authority here.
Only explicitly rights-gated, hash-pinned derivative assets in the manifest are fetched.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "assets/donor/luhm-game-donors.json"
OUT = ROOT / "assets/donor/runtime"
BUILD = ROOT / "build/luhm-game-donors"
USER_AGENT = "LuHmOS-FullGameDonorForge/1.0"
MAX_TOTAL_BYTES = 2 * 1024 * 1024


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch_drive(file_id: str, attempts: int = 4) -> bytes:
    urls = [
        f"https://drive.usercontent.google.com/download?id={file_id}&export=download&confirm=t",
        f"https://drive.google.com/uc?export=download&id={file_id}&confirm=t",
    ]
    last: Exception | None = None
    for url in urls:
        for attempt in range(1, attempts + 1):
            try:
                request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
                with urllib.request.urlopen(request, timeout=60) as response:
                    data = response.read()
                if data:
                    return data
                raise RuntimeError("empty response")
            except Exception as exc:
                last = exc
                if attempt < attempts:
                    time.sleep(float(attempt))
    raise RuntimeError(f"Drive donor fetch failed: {file_id}: {last}")


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("product_scope") != "LUHM_OS_FULL_GAME_ONLY":
        raise RuntimeError("RED_DONOR_SCOPE_DRIFT")
    if manifest.get("donor_authority") is not False:
        raise RuntimeError("RED_KAI_DONOR_AUTHORITY_DRIFT")
    if manifest.get("runtime_network") is not False or manifest.get("build_time_fetch_only") is not True:
        raise RuntimeError("RED_DONOR_NETWORK_POLICY_DRIFT")

    assets = manifest.get("assets", [])
    if len(assets) != 2:
        raise RuntimeError("RED_DONOR_ASSET_COUNT_DRIFT")

    shutil.rmtree(OUT, ignore_errors=True)
    OUT.mkdir(parents=True, exist_ok=True)
    BUILD.mkdir(parents=True, exist_ok=True)

    total = 0
    receipt_assets = []
    for asset in assets:
        rights = str(asset.get("source_rights", ""))
        if rights not in {"USER_SUPPLIED_OR_GENERATED", "PERMISSIVE"}:
            raise RuntimeError(f"RED_DONOR_RIGHTS:{asset.get('id')}")
        runtime_path = str(asset["runtime_path"])
        prefix = "res://assets/donor/runtime/"
        if not runtime_path.startswith(prefix):
            raise RuntimeError("RED_DONOR_RUNTIME_PATH")
        filename = runtime_path.removeprefix(prefix)
        if not filename or "/" in filename or "\\" in filename:
            raise RuntimeError("RED_DONOR_FILENAME")

        data = fetch_drive(str(asset["drive_file_id"]))
        observed = sha256(data)
        if observed != asset["sha256"]:
            raise RuntimeError(f"RED_DONOR_HASH:{asset['id']}:{observed}")
        if len(data) != int(asset["bytes"]):
            raise RuntimeError(f"RED_DONOR_SIZE:{asset['id']}")
        total += len(data)
        if total > MAX_TOTAL_BYTES:
            raise RuntimeError("RED_DONOR_ANDROID_BUDGET")

        target = OUT / filename
        target.write_bytes(data)
        receipt_assets.append({
            "id": asset["id"],
            "runtime_path": runtime_path,
            "drive_file_id": asset["drive_file_id"],
            "bytes": len(data),
            "sha256": observed,
            "source_rights": rights,
        })
        print(f"LUHM_GAME_DONOR_STAGED {asset['id']} bytes={len(data)} sha={observed[:12]}")

    receipt = {
        "schema": "luhm-os.game-donor-build-receipt.v1",
        "status": "LUHM_GAME_DONORS_GREEN",
        "product_scope": "LUHM_OS_FULL_GAME_ONLY",
        "donor": manifest["donor"],
        "donor_authority": False,
        "runtime_network": False,
        "asset_count": len(receipt_assets),
        "total_bytes": total,
        "assets": receipt_assets,
    }
    encoded = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    (OUT / "PROVENANCE.json").write_text(encoded, encoding="utf-8")
    (BUILD / "receipt.json").write_text(encoded, encoding="utf-8")
    print(f"LUHM_GAME_DONOR_STAGE=PASS count={len(receipt_assets)} bytes={total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

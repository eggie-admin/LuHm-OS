#!/usr/bin/env python3
"""Verify rights-cleared LuHm OS full-game donor derivatives.

Full-resolution donor sources remain private in Drive as provenance/source authority.
CI uses only tiny vendored derivatives whose exact bytes are pinned in the manifest,
so builds need no Drive credential and never weaken private sharing.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "assets/donor/luhm-game-donors.json"
BUILD = ROOT / "build/luhm-game-donors"
MAX_TOTAL_BYTES = 2 * 1024 * 1024


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("product_scope") != "LUHM_OS_FULL_GAME_ONLY":
        raise RuntimeError("RED_DONOR_SCOPE_DRIFT")
    if manifest.get("donor_authority") is not False:
        raise RuntimeError("RED_KAI_DONOR_AUTHORITY_DRIFT")
    if manifest.get("runtime_network") is not False:
        raise RuntimeError("RED_DONOR_NETWORK_POLICY_DRIFT")
    if manifest.get("runtime_delivery") != "GIT_VENDORED_RIGHTS_CLEARED_DERIVATIVES":
        raise RuntimeError("RED_DONOR_DELIVERY_POLICY_DRIFT")
    vault = manifest.get("source_vault", {})
    if vault.get("privacy") != "PRIVATE_SOURCE_AND_PROVENANCE_VAULT" or vault.get("ci_fetch") is not False:
        raise RuntimeError("RED_DONOR_PRIVATE_VAULT_POLICY_DRIFT")

    assets = manifest.get("assets", [])
    if len(assets) != 2:
        raise RuntimeError("RED_DONOR_ASSET_COUNT_DRIFT")

    BUILD.mkdir(parents=True, exist_ok=True)
    receipts = []
    total = 0
    for asset in assets:
        rights = str(asset.get("source_rights", ""))
        if rights not in {"USER_SUPPLIED_OR_GENERATED", "PERMISSIVE"}:
            raise RuntimeError(f"RED_DONOR_RIGHTS:{asset.get('id')}")
        runtime_path = str(asset["runtime_path"])
        prefix = "res://assets/donor/runtime/"
        if not runtime_path.startswith(prefix):
            raise RuntimeError("RED_DONOR_RUNTIME_PATH")
        target = ROOT / runtime_path.removeprefix("res://")
        if not target.is_file():
            raise RuntimeError(f"RED_DONOR_RUNTIME_MISSING:{asset['id']}")
        data = target.read_bytes()
        observed = sha256(data)
        if observed != asset["sha256"]:
            raise RuntimeError(f"RED_DONOR_HASH:{asset['id']}:{observed}")
        if len(data) != int(asset["bytes"]):
            raise RuntimeError(f"RED_DONOR_SIZE:{asset['id']}")
        total += len(data)
        if total > MAX_TOTAL_BYTES:
            raise RuntimeError("RED_DONOR_ANDROID_BUDGET")
        receipts.append({
            "id": asset["id"],
            "runtime_path": runtime_path,
            "source_drive_file_id": asset["drive_file_id"],
            "bytes": len(data),
            "sha256": observed,
            "source_rights": rights,
            "delivery": "vendored_rights_cleared_derivative"
        })
        print(f"LUHM_GAME_DONOR_VERIFIED {asset['id']} bytes={len(data)} sha={observed[:12]}")

    receipt = {
        "schema": "luhm-os.game-donor-build-receipt.v2",
        "status": "LUHM_GAME_DONORS_GREEN",
        "product_scope": "LUHM_OS_FULL_GAME_ONLY",
        "donor": manifest["donor"],
        "donor_authority": False,
        "runtime_network": False,
        "source_vault_private": True,
        "source_vault_ci_fetch": False,
        "runtime_delivery": manifest["runtime_delivery"],
        "asset_count": len(receipts),
        "total_bytes": total,
        "assets": receipts,
    }
    encoded = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    (BUILD / "receipt.json").write_text(encoded, encoding="utf-8")
    print(f"LUHM_GAME_DONOR_STAGE=PASS count={len(receipts)} bytes={total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

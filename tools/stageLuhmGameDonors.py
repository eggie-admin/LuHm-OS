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
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "assets/donor/luhm-game-donors.json"
BUILD = ROOT / "build/luhm-game-donors"
MAX_TOTAL_BYTES = 2 * 1024 * 1024
ALLOWED_RIGHTS = {"USER_SUPPLIED_OR_GENERATED", "PERMISSIVE"}
ALLOWED_RUNTIME_FORMATS = {"SVG_VECTOR_MOSAIC"}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha1(data: bytes) -> str:
    header = b"blob " + str(len(data)).encode("ascii") + b"\0"
    return hashlib.sha1(header + data).hexdigest()


def validate_svg(asset_id: str, data: bytes) -> None:
    try:
        text = data.decode("utf-8")
        root = ET.fromstring(text)
    except (UnicodeDecodeError, ET.ParseError) as exc:
        raise RuntimeError(f"RED_DONOR_FORMAT:{asset_id}:SVG_PARSE") from exc
    if not root.tag.endswith("svg"):
        raise RuntimeError(f"RED_DONOR_FORMAT:{asset_id}:SVG_ROOT")
    view_box = root.attrib.get("viewBox", "").split()
    if len(view_box) != 4:
        raise RuntimeError(f"RED_DONOR_FORMAT:{asset_id}:SVG_VIEWBOX")
    try:
        width = float(view_box[2])
        height = float(view_box[3])
    except ValueError as exc:
        raise RuntimeError(f"RED_DONOR_FORMAT:{asset_id}:SVG_DIMENSIONS") from exc
    if width <= 0 or height <= 0:
        raise RuntimeError(f"RED_DONOR_FORMAT:{asset_id}:SVG_DIMENSIONS")
    if "<script" in text.lower() or "javascript:" in text.lower() or "http://" in text.lower().replace("http://www.w3.org/2000/svg", "") or "https://" in text.lower():
        raise RuntimeError(f"RED_DONOR_FORMAT:{asset_id}:SVG_ACTIVE_OR_REMOTE_CONTENT")


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
        asset_id = str(asset.get("id", ""))
        role = str(asset.get("role", "")).lower()
        rights = str(asset.get("source_rights", ""))
        if rights not in ALLOWED_RIGHTS:
            raise RuntimeError(f"RED_DONOR_RIGHTS:{asset_id}")
        if "archive" not in role and "shrine" not in role:
            raise RuntimeError(f"RED_DONOR_ROLE_AUTHORITY_DRIFT:{asset_id}")
        source_sha = str(asset.get("source_sha256", ""))
        if len(source_sha) != 64:
            raise RuntimeError(f"RED_DONOR_SOURCE_HASH:{asset_id}")
        runtime_path = str(asset["runtime_path"])
        prefix = "res://assets/donor/runtime/"
        if not runtime_path.startswith(prefix):
            raise RuntimeError("RED_DONOR_RUNTIME_PATH")
        runtime_format = str(asset.get("runtime_format", ""))
        if runtime_format not in ALLOWED_RUNTIME_FORMATS or not runtime_path.endswith(".svg"):
            raise RuntimeError(f"RED_DONOR_RUNTIME_FORMAT:{asset_id}")
        target = ROOT / runtime_path.removeprefix("res://")
        if not target.is_file():
            raise RuntimeError(f"RED_DONOR_RUNTIME_MISSING:{asset_id}")
        data = target.read_bytes()
        observed = sha256(data)
        if observed != asset["sha256"]:
            raise RuntimeError(f"RED_DONOR_HASH:{asset_id}:{observed}")
        if len(data) != int(asset["bytes"]):
            raise RuntimeError(f"RED_DONOR_SIZE:{asset_id}")
        if source_sha == observed:
            raise RuntimeError(f"RED_DONOR_SOURCE_DERIVATIVE_COLLAPSE:{asset_id}")
        observed_blob = git_blob_sha1(data)
        if observed_blob != str(asset.get("git_blob_sha1", "")):
            raise RuntimeError(f"RED_DONOR_GIT_BLOB:{asset_id}:{observed_blob}")
        validate_svg(asset_id, data)
        total += len(data)
        if total > MAX_TOTAL_BYTES:
            raise RuntimeError("RED_DONOR_ANDROID_BUDGET")
        receipts.append({
            "id": asset_id,
            "role": asset["role"],
            "runtime_path": runtime_path,
            "runtime_format": runtime_format,
            "format_validation": "GREEN",
            "source_drive_file_id": asset["drive_file_id"],
            "source_sha256": source_sha,
            "bytes": len(data),
            "sha256": observed,
            "git_blob_sha1": observed_blob,
            "source_rights": rights,
            "delivery": "vendored_rights_cleared_derivative"
        })
        print(f"LUHM_GAME_DONOR_VERIFIED {asset_id} bytes={len(data)} sha={observed[:12]} format={runtime_format}")

    receipt = {
        "schema": "luhm-os.game-donor-build-receipt.v3",
        "status": "LUHM_GAME_DONORS_GREEN",
        "product_scope": "LUHM_OS_FULL_GAME_ONLY",
        "donor": manifest["donor"],
        "donor_authority": False,
        "runtime_network": False,
        "source_vault_private": True,
        "source_vault_ci_fetch": False,
        "runtime_delivery": manifest["runtime_delivery"],
        "format_gate": "GREEN",
        "asset_count": len(receipts),
        "total_bytes": total,
        "assets": receipts,
    }
    encoded = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    (BUILD / "receipt.json").write_text(encoded, encoding="utf-8")
    print(f"LUHM_GAME_DONOR_STAGE=PASS count={len(receipts)} bytes={total} format_gate=GREEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

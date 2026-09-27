#!/usr/bin/env python3
"""Fail-closed audit for the LuHm OS full-game candidate.

This prevents KAI9000 widget/project authority from bleeding into the LuHm game lane
while allowing explicitly rights-gated donor assets and implementation patterns.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCTRINE = ROOT / "doctrine/luhmFullGameDoctrine-20260927.json"
SOT = ROOT / "doctrine/luhmFullGameSourceTruth-20260927.json"
DONORS = ROOT / "assets/donor/luhm-game-donors.json"
DONOR_RECEIPT = ROOT / "build/luhm-game-donors/receipt.json"

REQUIRED_PATHS = [
    ROOT / "scenes/Main.tscn",
    ROOT / "scripts/game/crownCathedralSetDress.gd",
    ROOT / "scripts/game/coffeeHouseSetDress.gd",
    ROOT / "scripts/game/communitySetDress.gd",
    ROOT / "scripts/game/finalCoffeeHouseOverlay.gd",
    ROOT / "scripts/game/crownDonorGallery.gd",
    ROOT / "scripts/game/lumAvatar.gd",
    ROOT / "scripts/game/playerController.gd",
    ROOT / "native/kaiwebview/kaiwebview/src/main/java/art/eggiebagelface/luhmos/kaiwebview/KAIWebView.kt",
]


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, code: str) -> None:
    if not condition:
        raise SystemExit(code)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--with-donor-receipt", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    doctrine = load(DOCTRINE)
    sot = load(SOT)
    donors = load(DONORS)

    require(doctrine.get("product") == "LuHm OS" and doctrine.get("scope") == "FULL_GAME", "RED_GAME_DOCTRINE_SCOPE")
    require(sot.get("product") == "LuHm OS" and sot.get("scope") == "FULL_GAME", "RED_GAME_SOURCE_TRUTH_SCOPE")
    require(doctrine.get("donor_policy", {}).get("kai9000") == "DONOR_INVENTORY_ONLY_NOT_GAME_AUTHORITY", "RED_KAI_AUTHORITY_DRIFT")
    require(sot.get("donor_boundary", {}).get("kai9000_authority") is False, "RED_KAI_SOURCE_AUTHORITY_DRIFT")
    require(sot.get("donor_boundary", {}).get("widget_project_authority") is False, "RED_WIDGET_AUTHORITY_DRIFT")
    require(donors.get("product_scope") == "LUHM_OS_FULL_GAME_ONLY", "RED_DONOR_PRODUCT_SCOPE")
    require(donors.get("donor_authority") is False, "RED_DONOR_AUTHORITY")
    require(donors.get("runtime_network") is False, "RED_DONOR_RUNTIME_NETWORK")
    require(len(donors.get("assets", [])) == 2, "RED_DONOR_COUNT")

    for path in REQUIRED_PATHS:
        require(path.exists(), f"RED_REQUIRED_GAME_PATH:{path.relative_to(ROOT)}")

    forbidden_runtime_tokens = ("local-widget", "kai-widget", "DestinyChild", "legacy PCK")
    for asset in donors["assets"]:
        runtime_path = str(asset.get("runtime_path", ""))
        require(runtime_path.startswith("res://assets/donor/runtime/"), "RED_DONOR_RUNTIME_PATH")
        require(str(asset.get("source_rights", "")) in {"USER_SUPPLIED_OR_GENERATED", "PERMISSIVE"}, "RED_DONOR_RIGHTS")
        require(not any(token.lower() in runtime_path.lower() for token in forbidden_runtime_tokens), "RED_PRIVATE_OR_WIDGET_RUNTIME_PATH")
        require(len(str(asset.get("sha256", ""))) == 64, "RED_DONOR_HASH_PIN")
        require(bool(str(asset.get("drive_file_id", ""))), "RED_DONOR_DRIVE_PIN")

    webview = (ROOT / "native/kaiwebview/kaiwebview/src/main/java/art/eggiebagelface/luhmos/kaiwebview/KAIWebView.kt").read_text(encoding="utf-8")
    require("blockNetworkLoads = true" in webview, "RED_WEBGLASS_NETWORK_CAGE")
    require('private const val ORIGIN = "https://appassets.androidplatform.net"' in webview, "RED_WEBGLASS_ORIGIN_CAGE")

    export = (ROOT / "export_presets.cfg").read_text(encoding="utf-8")
    require('exclude_filter="host/**"' in export, "RED_HOST_EXPORT_BOUNDARY")
    require("permissions/internet=false" in export, "RED_APK_INTERNET_POLICY")

    receipt_green = False
    donor_bytes = 0
    if args.with_donor_receipt:
        require(DONOR_RECEIPT.exists(), "RED_DONOR_RECEIPT_MISSING")
        receipt = load(DONOR_RECEIPT)
        require(receipt.get("status") == "LUHM_GAME_DONORS_GREEN", "RED_DONOR_RECEIPT_STATUS")
        require(receipt.get("donor_authority") is False, "RED_DONOR_RECEIPT_AUTHORITY")
        require(receipt.get("runtime_network") is False, "RED_DONOR_RECEIPT_NETWORK")
        require(int(receipt.get("asset_count", 0)) == 2, "RED_DONOR_RECEIPT_COUNT")
        for item in receipt.get("assets", []):
            file_path = ROOT / str(item["runtime_path"]).removeprefix("res://")
            require(file_path.exists(), "RED_DONOR_RUNTIME_MISSING")
            require(sha256(file_path) == item["sha256"], "RED_DONOR_RUNTIME_HASH")
        receipt_green = True
        donor_bytes = int(receipt.get("total_bytes", 0))

    result = {
        "schema": "luhm-os.full-game-audit.v1",
        "status": "LUHM_FULL_GAME_SCOPE_GREEN",
        "product": "LuHm OS",
        "scope": "FULL_GAME",
        "kai9000_donor_only": True,
        "widget_authority": False,
        "private_relic_payload_authority": False,
        "donor_manifest_green": True,
        "donor_receipt_green": receipt_green,
        "donor_bytes": donor_bytes,
        "webglass_network_cage_green": True,
        "host_export_boundary_green": True,
        "apk_internet_policy_green": True,
        "canonical_main_promoted": False,
    }
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    print("LUHM_FULL_GAME_AUDIT=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

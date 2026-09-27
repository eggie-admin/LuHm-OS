#!/usr/bin/env python3
"""Fail-closed audit for the LuHm OS full-game Crown Cathedral candidate.

LuHm OS full game is authority. KAI9000 remains donor inventory only. Historical
kai_webview path names are Android binary-compatibility plumbing and never
runtime, product, doctrine, or source-of-truth authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCTRINE = ROOT / "doctrine/luhmFullGameDoctrine-20260927.json"
SOT = ROOT / "doctrine/luhmFullGameSourceTruth-20260927.json"
ROOT_SOT = ROOT / "doctrine/SOURCE_OF_TRUTH.json"
DEPLOYMENT = ROOT / "doctrine/crownCathedralDeployment-20260927.json"
BOUNDARY = ROOT / "doctrine/RELEASE_BOUNDARY.json"
DONORS = ROOT / "assets/donor/luhm-game-donors.json"
DONOR_RECEIPT = ROOT / "build/luhm-game-donors/receipt.json"
SIGNING_SCRIPT = ROOT / "scripts/buildCathedralReleaseCandidate.sh"
WEBVIEW_PATH = ROOT / "native/kaiwebview/kaiwebview/src/main/java/art/eggiebagelface/luhmos/kaiwebview/KAIWebView.kt"
CURRENT_BRANCH = "candidate/crown-cathedral-audit-hardening-20260927"
CANONICAL_MAIN = "506e486cb142f6c81f7df71d007fdf05e47e82ed"
BASELINE_GREEN_HEAD = "93bc11cbc1c09ecf6e18605985beebf4f9a4e8d5"

REQUIRED_PATHS = [
    ROOT / "scenes/Main.tscn",
    ROOT / "scripts/game/crownCathedralSetDress.gd",
    ROOT / "scripts/game/coffeeHouseSetDress.gd",
    ROOT / "scripts/game/communitySetDress.gd",
    ROOT / "scripts/game/finalCoffeeHouseOverlay.gd",
    ROOT / "scripts/game/crownDonorGallery.gd",
    ROOT / "scripts/game/lumAvatar.gd",
    ROOT / "scripts/game/playerController.gd",
    WEBVIEW_PATH,
]


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    header = b"blob " + str(len(data)).encode("ascii") + b"\0"
    return hashlib.sha1(header + data).hexdigest()


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
    root_sot = load(ROOT_SOT)
    deployment = load(DEPLOYMENT)
    boundary = load(BOUNDARY)
    donors = load(DONORS)

    require(doctrine.get("product") == "LuHm OS" and doctrine.get("scope") == "FULL_GAME", "RED_GAME_DOCTRINE_SCOPE")
    require(sot.get("product") == "LuHm OS" and sot.get("scope") == "FULL_GAME", "RED_GAME_SOURCE_TRUTH_SCOPE")
    require(root_sot.get("product") == "LuHm OS" and root_sot.get("scope") == "FULL_GAME", "RED_ROOT_SOURCE_TRUTH_SCOPE")
    require(deployment.get("product") == "LuHm OS" and deployment.get("product_scope") == "FULL_GAME", "RED_DEPLOYMENT_SCOPE")
    require(root_sot.get("canonical_repository") == "eggie-admin/LuHm-OS", "RED_ROOT_REPOSITORY_DRIFT")
    require(root_sot.get("canonicalMain", {}).get("sha") == CANONICAL_MAIN, "RED_CANONICAL_MAIN_POINTER_DRIFT")

    # One current LuHm full-game authority lane. Historical seals cannot override it.
    require(doctrine.get("candidate_branch") == CURRENT_BRANCH, "RED_DOCTRINE_GAME_BRANCH_DRIFT")
    require(sot.get("candidate_branch") == CURRENT_BRANCH, "RED_SOURCE_TRUTH_GAME_BRANCH_DRIFT")
    require(deployment.get("branch") == CURRENT_BRANCH, "RED_DEPLOYMENT_GAME_BRANCH_DRIFT")
    require(root_sot.get("currentFullGameCandidate", {}).get("branch") == CURRENT_BRANCH, "RED_ROOT_GAME_BRANCH_DRIFT")
    require(doctrine.get("baseline_proven_green_head") == BASELINE_GREEN_HEAD, "RED_DOCTRINE_BASELINE_PROOF_DRIFT")
    require(sot.get("baseline_proven_green_head") == BASELINE_GREEN_HEAD, "RED_SOURCE_TRUTH_BASELINE_PROOF_DRIFT")
    require(deployment.get("baseline_proven_green_head") == BASELINE_GREEN_HEAD, "RED_DEPLOYMENT_BASELINE_PROOF_DRIFT")
    require(root_sot.get("currentFullGameCandidate", {}).get("baselineProvenExactHead") == BASELINE_GREEN_HEAD, "RED_ROOT_BASELINE_PROOF_DRIFT")
    require(doctrine.get("current_candidate_head") == "DERIVED_AT_CI_RUNTIME", "RED_DOCTRINE_SELF_REFERENCE")
    require(sot.get("current_candidate_head") == "DERIVED_AT_CI_RUNTIME", "RED_SOURCE_TRUTH_SELF_REFERENCE")
    require(deployment.get("current_candidate_head") == "DERIVED_AT_CI_RUNTIME", "RED_DEPLOYMENT_SELF_REFERENCE")
    require(root_sot.get("currentFullGameCandidate", {}).get("currentExactHead") == "DERIVED_AT_CI_RUNTIME", "RED_ROOT_SELF_REFERENCE")
    require(doctrine.get("historical_seals_override_current_full_game") is False, "RED_HISTORICAL_SEAL_AUTHORITY")
    require(sot.get("historical_seals_override_current_full_game") is False, "RED_SOURCE_TRUTH_HISTORICAL_AUTHORITY")
    require(root_sot.get("historicalSealsOverrideCurrentFullGame") is False, "RED_ROOT_HISTORICAL_AUTHORITY")

    require(doctrine.get("donor_policy", {}).get("kai9000") == "DONOR_INVENTORY_ONLY_NOT_GAME_AUTHORITY", "RED_KAI_AUTHORITY_DRIFT")
    require(sot.get("donor_boundary", {}).get("kai9000_authority") is False, "RED_KAI_SOURCE_AUTHORITY_DRIFT")
    require(sot.get("donor_boundary", {}).get("widget_project_authority") is False, "RED_WIDGET_AUTHORITY_DRIFT")
    require(root_sot.get("donorPolicy", {}).get("kai9000WidgetAuthority") is False, "RED_ROOT_WIDGET_AUTHORITY_DRIFT")
    require(deployment.get("game_donors", {}).get("kai9000_authority") is False, "RED_DEPLOYMENT_KAI_AUTHORITY_DRIFT")
    require(deployment.get("game_donors", {}).get("widget_authority") is False, "RED_DEPLOYMENT_WIDGET_AUTHORITY_DRIFT")

    require(donors.get("schema") == "luhm-os.game-donor-manifest.v3", "RED_DONOR_MANIFEST_SCHEMA")
    require(donors.get("product_scope") == "LUHM_OS_FULL_GAME_ONLY", "RED_DONOR_PRODUCT_SCOPE")
    require(donors.get("donor_authority") is False, "RED_DONOR_AUTHORITY")
    require(donors.get("runtime_network") is False, "RED_DONOR_RUNTIME_NETWORK")
    require(donors.get("runtime_delivery") == "GIT_VENDORED_RIGHTS_CLEARED_DERIVATIVES", "RED_DONOR_DELIVERY")
    require(len(donors.get("assets", [])) == 2, "RED_DONOR_COUNT")

    compatibility_names = set(boundary.get("compatibility_names_not_authority", []))
    require("addons/kai_webview" in compatibility_names, "RED_COMPATIBILITY_ADDON_AUTHORITY_UNSEALED")
    require("native/kaiwebview" in compatibility_names, "RED_COMPATIBILITY_NATIVE_AUTHORITY_UNSEALED")
    require("KAI9000 widget authority" in set(boundary.get("deny", [])), "RED_WIDGET_RELEASE_BOUNDARY")
    require(doctrine.get("compatibility_policy", {}).get("runtime_identity") == "LUHM_WEBGLASS", "RED_DOCTRINE_WEBGLASS_IDENTITY")
    require(sot.get("compatibility_boundary", {}).get("runtime_identity") == "LUHM_WEBGLASS", "RED_SOURCE_TRUTH_WEBGLASS_IDENTITY")
    require(root_sot.get("compatibilityPolicy", {}).get("runtimeIdentity") == "LUHM_WEBGLASS", "RED_ROOT_WEBGLASS_IDENTITY")
    require(deployment.get("webglass", {}).get("runtime_identity") == "LUHM_WEBGLASS", "RED_DEPLOYMENT_WEBGLASS_IDENTITY")

    for path in REQUIRED_PATHS:
        require(path.exists(), f"RED_REQUIRED_GAME_PATH:{path.relative_to(ROOT)}")

    forbidden_runtime_tokens = ("local-widget", "kai-widget", "DestinyChild", "legacy PCK")
    for asset in donors["assets"]:
        runtime_path = str(asset.get("runtime_path", ""))
        require(runtime_path.startswith("res://assets/donor/runtime/"), "RED_DONOR_RUNTIME_PATH")
        require(runtime_path.endswith(".svg"), "RED_DONOR_RUNTIME_EXTENSION")
        require(asset.get("runtime_format") == "SVG_VECTOR_MOSAIC", "RED_DONOR_RUNTIME_FORMAT")
        require(str(asset.get("source_rights", "")) in {"USER_SUPPLIED_OR_GENERATED", "PERMISSIVE"}, "RED_DONOR_RIGHTS")
        require(not any(token.lower() in runtime_path.lower() for token in forbidden_runtime_tokens), "RED_PRIVATE_OR_WIDGET_RUNTIME_PATH")
        require(len(str(asset.get("source_sha256", ""))) == 64, "RED_DONOR_SOURCE_HASH_PIN")
        require(len(str(asset.get("sha256", ""))) == 64, "RED_DONOR_HASH_PIN")
        require(asset.get("source_sha256") != asset.get("sha256"), "RED_DONOR_SOURCE_DERIVATIVE_COLLAPSE")
        require(bool(str(asset.get("drive_file_id", ""))), "RED_DONOR_DRIVE_PIN")
        require(len(str(asset.get("git_blob_sha1", ""))) == 40, "RED_DONOR_GIT_BLOB_PIN")
        file_path = ROOT / runtime_path.removeprefix("res://")
        require(file_path.exists(), "RED_DONOR_RUNTIME_MISSING")
        require(sha256(file_path) == asset["sha256"], "RED_DONOR_RUNTIME_HASH")
        require(git_blob_sha1(file_path) == asset["git_blob_sha1"], "RED_DONOR_RUNTIME_GIT_BLOB")

    webview = WEBVIEW_PATH.read_text(encoding="utf-8")
    require("blockNetworkLoads = true" in webview, "RED_WEBGLASS_NETWORK_CAGE")
    require('private const val ORIGIN = "https://appassets.androidplatform.net"' in webview, "RED_WEBGLASS_ORIGIN_CAGE")
    require('.put("bridge", "luhm-webglass")' in webview, "RED_WEBGLASS_LUHM_IDENTITY")
    require('.put("aiHost", "external")' in webview, "RED_WEBGLASS_HOST_BOUNDARY")
    require('.put("kai",' not in webview.lower(), "RED_KAI_RUNTIME_STATUS_LEAK")
    require('.put("ollama",' not in webview.lower(), "RED_OLLAMA_RUNTIME_STATUS_LEAK")

    export = (ROOT / "export_presets.cfg").read_text(encoding="utf-8")
    require('exclude_filter="host/**"' in export, "RED_HOST_EXPORT_BOUNDARY")
    require("permissions/internet=false" in export, "RED_APK_INTERNET_POLICY")

    signing = SIGNING_SCRIPT.read_text(encoding="utf-8")
    for token in (
        "LUHM_CROWN_KEYSTORE_PATH",
        "LUHM_CROWN_KEY_ALIAS",
        "LUHM_CROWN_KEYSTORE_PASSWORD",
        "RED_CROWN_SIGNING_INPUTS_INCOMPLETE",
        "RED_CROWN_KEYSTORE_UNREADABLE",
        "crown_persistent_external",
        "ephemeral_ci_release_key",
    ):
        require(token in signing, f"RED_CROWN_SIGNING_PATH_MISSING:{token}")

    receipt_green = False
    donor_bytes = 0
    donor_format_green = False
    if args.with_donor_receipt:
        require(DONOR_RECEIPT.exists(), "RED_DONOR_RECEIPT_MISSING")
        receipt = load(DONOR_RECEIPT)
        require(receipt.get("schema") == "luhm-os.game-donor-build-receipt.v3", "RED_DONOR_RECEIPT_SCHEMA")
        require(receipt.get("status") == "LUHM_GAME_DONORS_GREEN", "RED_DONOR_RECEIPT_STATUS")
        require(receipt.get("format_gate") == "GREEN", "RED_DONOR_FORMAT_GATE")
        require(receipt.get("donor_authority") is False, "RED_DONOR_RECEIPT_AUTHORITY")
        require(receipt.get("runtime_network") is False, "RED_DONOR_RECEIPT_NETWORK")
        require(receipt.get("source_vault_private") is True and receipt.get("source_vault_ci_fetch") is False, "RED_DONOR_RECEIPT_VAULT_BOUNDARY")
        require(int(receipt.get("asset_count", 0)) == 2, "RED_DONOR_RECEIPT_COUNT")
        for item in receipt.get("assets", []):
            require(item.get("runtime_format") == "SVG_VECTOR_MOSAIC", "RED_DONOR_RECEIPT_RUNTIME_FORMAT")
            require(item.get("format_validation") == "GREEN", "RED_DONOR_RECEIPT_FORMAT_VALIDATION")
            file_path = ROOT / str(item["runtime_path"]).removeprefix("res://")
            require(file_path.exists(), "RED_DONOR_RUNTIME_MISSING")
            require(sha256(file_path) == item["sha256"], "RED_DONOR_RUNTIME_HASH")
            require(git_blob_sha1(file_path) == item["git_blob_sha1"], "RED_DONOR_RECEIPT_GIT_BLOB")
        receipt_green = True
        donor_format_green = True
        donor_bytes = int(receipt.get("total_bytes", 0))

    result = {
        "schema": "luhm-os.full-game-audit.v4",
        "status": "LUHM_FULL_GAME_SCOPE_GREEN",
        "product": "LuHm OS",
        "scope": "FULL_GAME",
        "current_candidate_branch": CURRENT_BRANCH,
        "baseline_proven_green_head": BASELINE_GREEN_HEAD,
        "root_source_truth_converged": True,
        "full_game_authority_converged": True,
        "historical_seals_override_current_full_game": False,
        "canonical_main_pointer_green": True,
        "kai9000_donor_only": True,
        "widget_authority": False,
        "compatibility_bridge_authority_limited": True,
        "webglass_luhm_identity_green": True,
        "private_relic_payload_authority": False,
        "donor_manifest_green": True,
        "donor_format_gate_green": donor_format_green,
        "donor_receipt_green": receipt_green,
        "donor_bytes": donor_bytes,
        "webglass_network_cage_green": True,
        "host_export_boundary_green": True,
        "apk_internet_policy_green": True,
        "persistent_crown_signing_path_green": True,
        "persistent_crown_signing_identity_present": False,
        "physical_device_current_exact_head_proof": False,
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

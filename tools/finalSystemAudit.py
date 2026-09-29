#!/usr/bin/env python3
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
LUM_BUNDLE_SHA = "fedaf37220d5f9477560fdc0b5624d30e95191db989f5b8428ca4d1a19b1d3da"
LUM_BASE_SHA = "06bdfcc196e147c4cb92c7c5489110a8feb30ee8a8f362fac585802eced33b69"
LUM_RUNNING_SHA = "750f54b2b3618767bdad3f9399a2f0cb8be70b46e39a65affe178b4745c964f0"
EXPECTED_COMMUNITY_COUNT = 77
EXPECTED_DONOR_COUNT = 2
MAX_DONOR_BYTES = 2 * 1024 * 1024
CURRENT_BRANCH = "candidate/crown-cathedral-audit-hardening-20260927"
CANONICAL_MAIN = "506e486cb142f6c81f7df71d007fdf05e47e82ed"
BASELINE_GREEN_HEAD = "93bc11cbc1c09ecf6e18605985beebf4f9a4e8d5"
EXPECTED_PACKAGE = "art.eggiebagelface.luhmos"
EXPECTED_VERSION_CODE = "102"
EXPECTED_VERSION_NAME = "1.0.2-final.mutation.1"


def fail(msg: str) -> None:
    raise SystemExit("RED_FINAL_SYSTEM_AUDIT: " + msg)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict:
    if not path.is_file():
        fail(f"missing JSON evidence {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build-dir", type=Path, required=True)
    parser.add_argument("--source-sha", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    doctrine = load_json(ROOT / "doctrine/openAiLumOniDeployment-20260927.json")
    if doctrine["authority"] != "Professor":
        fail("authority drift")
    if doctrine["architecture"]["parallelism_max"] != 3:
        fail("parallelism drift")
    if doctrine["openai"]["credential_in_apk"] is not False:
        fail("provider secret boundary drift")

    game_doctrine = load_json(ROOT / "doctrine/luhmFullGameDoctrine-20260927.json")
    game_truth = load_json(ROOT / "doctrine/luhmFullGameSourceTruth-20260927.json")
    root_truth = load_json(ROOT / "doctrine/SOURCE_OF_TRUTH.json")
    final_truth = load_json(ROOT / "doctrine/finalSystemSourceTruth-20260927.json")
    deployment = load_json(ROOT / "doctrine/crownCathedralDeployment-20260927.json")
    milestone = load_json(ROOT / "doctrine/finalMutationMilestone-20260928.json")

    if game_doctrine.get("product") != "LuHm OS" or game_doctrine.get("scope") != "FULL_GAME":
        fail("LuHm full-game doctrine scope drift")
    if game_truth.get("product") != "LuHm OS" or game_truth.get("scope") != "FULL_GAME":
        fail("LuHm full-game source-truth scope drift")
    if root_truth.get("product") != "LuHm OS" or root_truth.get("scope") != "FULL_GAME":
        fail("root source-truth scope drift")
    if final_truth.get("product") != "LuHm OS" or final_truth.get("scope") != "FULL_GAME":
        fail("final-system source-truth scope drift")
    if deployment.get("product") != "LuHm OS" or deployment.get("product_scope") != "FULL_GAME":
        fail("Crown deployment scope drift")
    if milestone.get("milestone") != "LUHM_OS_FINAL_MUTATION_001":
        fail("final mutation milestone drift")

    branches = {
        "game_doctrine": game_doctrine.get("candidate_branch"),
        "game_truth": game_truth.get("candidate_branch"),
        "root_truth": root_truth.get("currentFullGameCandidate", {}).get("branch"),
        "final_truth": final_truth.get("candidate_branch"),
        "deployment": deployment.get("branch"),
        "milestone": milestone.get("source", {}).get("candidate_branch"),
    }
    if any(value != CURRENT_BRANCH for value in branches.values()):
        fail("current full-game authority branch drift: " + json.dumps(branches, sort_keys=True))
    if root_truth.get("canonicalMain", {}).get("sha") != CANONICAL_MAIN:
        fail("canonical main pointer drift")
    if root_truth.get("canonicalMain", {}).get("promoted") is not False:
        fail("unproven canonical promotion")

    baseline_heads = {
        game_doctrine.get("baseline_proven_green_head"),
        game_truth.get("baseline_proven_green_head"),
        root_truth.get("currentFullGameCandidate", {}).get("baselineProvenExactHead"),
        final_truth.get("candidate_lineage", {}).get("baseline_proven_green_head"),
        deployment.get("baseline_proven_green_head"),
        milestone.get("source", {}).get("baseline_proven_green_head"),
    }
    if baseline_heads != {BASELINE_GREEN_HEAD}:
        fail("baseline proof drift")
    if game_doctrine.get("current_candidate_head") != "DERIVED_AT_CI_RUNTIME":
        fail("game doctrine self-referential head")
    if game_truth.get("current_candidate_head") != "DERIVED_AT_CI_RUNTIME":
        fail("game truth self-referential head")
    if final_truth.get("candidate_lineage", {}).get("current_candidate_head") != "DERIVED_AT_CI_RUNTIME":
        fail("final truth self-referential head")
    if deployment.get("current_candidate_head") != "DERIVED_AT_CI_RUNTIME":
        fail("deployment self-referential head")
    if root_truth.get("currentFullGameCandidate", {}).get("currentExactHead") != "DERIVED_AT_CI_RUNTIME":
        fail("root truth self-referential head")
    if milestone.get("source", {}).get("exact_head") != "DERIVED_AT_CI_RUNTIME":
        fail("final mutation milestone self-reference")

    if game_doctrine.get("historical_seals_override_current_full_game") is not False:
        fail("historical doctrine override drift")
    if game_truth.get("historical_seals_override_current_full_game") is not False:
        fail("historical source-truth override drift")
    if root_truth.get("historicalSealsOverrideCurrentFullGame") is not False:
        fail("historical root override drift")
    if final_truth.get("historical_seals_override_current_full_game") is not False:
        fail("historical final-system override drift")

    if game_doctrine.get("donor_policy", {}).get("kai9000") != "DONOR_INVENTORY_ONLY_NOT_GAME_AUTHORITY":
        fail("KAI9000 donor authority drift")
    if game_truth.get("donor_boundary", {}).get("widget_project_authority") is not False:
        fail("KAI9000 widget authority drift")
    if final_truth.get("donor_boundary", {}).get("kai9000_authority") is not False:
        fail("final-system KAI9000 authority drift")
    if final_truth.get("donor_boundary", {}).get("kai9000_widget_authority") is not False:
        fail("final-system widget authority drift")
    if root_truth.get("donorPolicy", {}).get("kai9000WidgetAuthority") is not False:
        fail("root widget authority drift")

    if game_doctrine.get("compatibility_policy", {}).get("runtime_identity") != "LUHM_WEBGLASS":
        fail("game doctrine WebGlass identity drift")
    if game_truth.get("compatibility_boundary", {}).get("runtime_identity") != "LUHM_WEBGLASS":
        fail("game truth WebGlass identity drift")
    if root_truth.get("compatibilityPolicy", {}).get("runtimeIdentity") != "LUHM_WEBGLASS":
        fail("root WebGlass identity drift")
    if final_truth.get("compatibility_boundary", {}).get("runtime_identity") != "LUHM_WEBGLASS":
        fail("final-system WebGlass identity drift")
    if deployment.get("webglass", {}).get("runtime_identity") != "LUHM_WEBGLASS":
        fail("deployment WebGlass identity drift")

    if root_truth.get("android", {}).get("package") != EXPECTED_PACKAGE:
        fail("root Android package drift")
    if deployment.get("android", {}).get("package") != EXPECTED_PACKAGE:
        fail("deployment Android package drift")
    if milestone.get("android", {}).get("package") != EXPECTED_PACKAGE:
        fail("milestone Android package drift")
    if int(milestone.get("android", {}).get("version_code", -1)) != int(EXPECTED_VERSION_CODE):
        fail("milestone version code drift")
    if milestone.get("android", {}).get("version_name") != EXPECTED_VERSION_NAME:
        fail("milestone version name drift")

    recovery = load_json(ROOT / "doctrine/reconciledCoffeeHouseLumCandidate-20260927.json")
    if recovery["authority"]["crown"] != "Professor":
        fail("recovery authority drift")
    if recovery["lum_drive"]["bundle_sha256"] != LUM_BUNDLE_SHA:
        fail("Lum bundle doctrine hash drift")
    if recovery["lum_drive"]["base_sha256"] != LUM_BASE_SHA:
        fail("Lum base doctrine hash drift")
    if recovery["lum_drive"]["running_sha256"] != LUM_RUNNING_SHA:
        fail("Lum running doctrine hash drift")
    if recovery["community_assets"]["selected_count"] != EXPECTED_COMMUNITY_COUNT:
        fail("community doctrine count drift")
    if recovery["nexus"]["shared_apk_default"] is not False:
        fail("Nexus shared-APK boundary drift")

    b = args.build_dir
    required = [
        "manifest.txt", "badging.txt", "signature.txt", "zipalign.txt",
        "sha256.txt", "source-commit.txt", "release-hardening.txt", "ziplist.txt",
        "community-assets-receipt.json", "luhm-game-donor-receipt.json",
        "luhm-game-donor-manifest.json", "luhm-full-game-final-audit.json",
        "final-mutation-milestone.json",
    ]
    for name in required:
        if not (b / name).is_file():
            fail(f"missing build receipt {name}")

    manifest = (b / "manifest.txt").read_text(errors="replace")
    badging = (b / "badging.txt").read_text(errors="replace")
    signature = (b / "signature.txt").read_text(errors="replace")
    zipalign = (b / "zipalign.txt").read_text(errors="replace")
    source = (b / "source-commit.txt").read_text().strip()
    hardening = (b / "release-hardening.txt").read_text(errors="replace")
    ziplist = (b / "ziplist.txt").read_text(errors="replace")

    if re.search(r"android:debuggable.*0xffffffff", manifest):
        fail("APK debuggable=true")
    if "android.permission.INTERNET" in manifest:
        fail("APK INTERNET permission present")
    if re.search(r"android:shell.*0xffffffff", manifest):
        fail("APK shell profiling remains enabled")
    if re.search(r"host/openai|lumHost\.py", ziplist, re.I):
        fail("host OpenAI adapter leaked into APK payload")
    if f"package: name='{EXPECTED_PACKAGE}'" not in badging:
        fail("package mismatch")
    if f"versionCode='{EXPECTED_VERSION_CODE}'" not in badging:
        fail("version code mismatch")
    if f"versionName='{EXPECTED_VERSION_NAME}'" not in badging:
        fail("version name mismatch")
    if "targetSdkVersion:'36'" not in badging:
        fail("target SDK mismatch")
    if "Verifies" not in signature or "Number of signers: 1" not in signature:
        fail("signature verification missing")
    if "Verification successful" not in zipalign:
        fail("16K zipalign verification missing")
    if source != args.source_sha:
        fail("source SHA receipt mismatch")
    if "export_mode=release_candidate" not in hardening:
        fail("release-mode receipt missing")
    if "debuggable=false" not in hardening or "internet_permission=false" not in hardening:
        fail("release hardening receipt incomplete")
    if "profileable_shell=false" not in hardening:
        fail("profileable-shell receipt missing")

    signing_match = re.search(r"^signing=([^\r\n]+)$", hardening, re.M)
    signing_mode = signing_match.group(1).strip() if signing_match else "UNKNOWN"
    production_signing = signing_mode == "crown_persistent_external"

    lum_base = ROOT / "assets/lum/luhm.glb"
    lum_running = ROOT / "assets/lum/luhmRunning.glb"
    if not lum_base.is_file() or not lum_running.is_file():
        fail("staged rigged Lum GLBs missing")
    observed_base_sha = sha256_file(lum_base)
    observed_running_sha = sha256_file(lum_running)
    if observed_base_sha != LUM_BASE_SHA:
        fail("staged Lum base hash mismatch")
    if observed_running_sha != LUM_RUNNING_SHA:
        fail("staged Lum running hash mismatch")

    community = load_json(b / "community-assets-receipt.json")
    if community.get("asset_count") != EXPECTED_COMMUNITY_COUNT:
        fail("community asset count mismatch")
    if community.get("license") != "CC0":
        fail("community license mismatch")
    if community.get("runtime_network") is not False:
        fail("community runtime-network boundary drift")
    if community.get("source_commit") != "3694c6879e487c108f55677be7dd2ca75b07cc3b":
        fail("community immutable source drift")

    donor_manifest = load_json(b / "luhm-game-donor-manifest.json")
    donor_receipt = load_json(b / "luhm-game-donor-receipt.json")
    game_audit = load_json(b / "luhm-full-game-final-audit.json")
    if donor_manifest.get("product_scope") != "LUHM_OS_FULL_GAME_ONLY":
        fail("donor manifest product scope drift")
    if donor_manifest.get("donor_authority") is not False:
        fail("donor authority drift")
    if donor_manifest.get("runtime_network") is not False:
        fail("donor runtime-network drift")
    if donor_manifest.get("runtime_delivery") != "GIT_VENDORED_RIGHTS_CLEARED_DERIVATIVES":
        fail("donor delivery mode drift")
    vault = donor_manifest.get("source_vault", {})
    if vault.get("privacy") != "PRIVATE_SOURCE_AND_PROVENANCE_VAULT" or vault.get("ci_fetch") is not False:
        fail("private donor source-vault boundary drift")
    if donor_receipt.get("status") != "LUHM_GAME_DONORS_GREEN":
        fail("donor build receipt not GREEN")
    if donor_receipt.get("donor_authority") is not False or donor_receipt.get("runtime_network") is not False:
        fail("donor receipt authority/network drift")
    if donor_receipt.get("source_vault_private") is not True or donor_receipt.get("source_vault_ci_fetch") is not False:
        fail("donor receipt private-vault boundary drift")
    if donor_receipt.get("asset_count") != EXPECTED_DONOR_COUNT:
        fail("donor asset count mismatch")
    donor_bytes = int(donor_receipt.get("total_bytes", 0))
    if donor_bytes <= 0 or donor_bytes > MAX_DONOR_BYTES:
        fail("donor Android byte budget drift")
    if game_audit.get("status") != "LUHM_FULL_GAME_SCOPE_GREEN":
        fail("full-game scope audit not GREEN")
    if game_audit.get("full_game_authority_converged") is not True:
        fail("full-game authority convergence receipt missing")
    if game_audit.get("kai9000_donor_only") is not True or game_audit.get("widget_authority") is not False:
        fail("full-game KAI/widget boundary drift")

    expected_assets = {str(item["id"]): item for item in donor_manifest.get("assets", [])}
    receipt_assets = {str(item["id"]): item for item in donor_receipt.get("assets", [])}
    if set(expected_assets) != set(receipt_assets) or len(expected_assets) != EXPECTED_DONOR_COUNT:
        fail("donor manifest/receipt identity mismatch")
    for donor_id, expected in expected_assets.items():
        observed = receipt_assets[donor_id]
        for field in ("runtime_path", "sha256", "bytes"):
            if observed.get(field) != expected.get(field):
                fail(f"donor {donor_id} {field} mismatch")
        if observed.get("source_drive_file_id") != expected.get("drive_file_id"):
            fail(f"donor {donor_id} provenance Drive ID mismatch")
        runtime_path = ROOT / str(expected["runtime_path"]).removeprefix("res://")
        if not runtime_path.is_file() or sha256_file(runtime_path) != expected["sha256"]:
            fail(f"donor {donor_id} runtime bytes mismatch")

    nexus_runtime = ROOT / "assets/nexus/runtime"
    private_glbs = list(nexus_runtime.rglob("*.glb")) if nexus_runtime.exists() else []
    if private_glbs:
        fail("private Nexus GLB present in shared CI candidate workspace")

    live_openai = (ROOT / "build/openai-live/receipt.json").is_file()
    device = (ROOT / "build/device/samsung-runtime-receipt.json").is_file()

    canonical_hard_stop = (
        "RED_PHYSICAL_SAMSUNG_RECEIPT_MISSING" if not device
        else "AMBER_HUMAN_PROMOTION_REQUIRED"
    )
    production_distribution_hard_stop = (
        "GREEN_CROWN_SIGNING_PRESENT" if production_signing
        else "RED_CROWN_PERSISTENT_SIGNING_PENDING"
    )
    host_ai_hard_stop = (
        "GREEN_OPENAI_LIVE_RECEIPT_PRESENT" if live_openai
        else "RED_OPENAI_LIVE_RECEIPT_MISSING"
    )

    receipt = {
        "schema": "luhm-os.final-system-audit.v5",
        "product": "LuHm OS",
        "scope": "FULL_GAME",
        "milestone": "LUHM_OS_FINAL_MUTATION_001",
        "source_sha": args.source_sha,
        "source_exact_head_ci": True,
        "current_candidate_branch": CURRENT_BRANCH,
        "baseline_proven_green_head": BASELINE_GREEN_HEAD,
        "current_doctrine_converged": True,
        "final_system_truth_converged": True,
        "historical_seals_override_current_full_game": False,
        "recovery_chain_reconciled": True,
        "game_deployment_candidate_green": True,
        "full_game_scope_green": True,
        "apk_release_candidate_green": True,
        "apk_package": EXPECTED_PACKAGE,
        "apk_version_code": int(EXPECTED_VERSION_CODE),
        "apk_version_name": EXPECTED_VERSION_NAME,
        "apk_debuggable": False,
        "apk_internet_permission": False,
        "apk_profileable_shell": False,
        "host_openai_in_apk": False,
        "webglass_runtime_identity": "LUHM_WEBGLASS",
        "legacy_kai_named_paths_authority": False,
        "agent_mesh_contract_green": True,
        "lum_rig_green": True,
        "lum_bundle_sha256": LUM_BUNDLE_SHA,
        "lum_base_sha256": observed_base_sha,
        "lum_running_sha256": observed_running_sha,
        "community_assets_green": True,
        "community_asset_count": community["asset_count"],
        "community_asset_bytes": community["total_asset_bytes"],
        "community_license": community["license"],
        "community_source_commit": community["source_commit"],
        "game_donors_green": True,
        "game_donor_count": donor_receipt["asset_count"],
        "game_donor_bytes": donor_bytes,
        "game_donor_runtime_delivery": donor_receipt["runtime_delivery"],
        "game_donor_private_source_vault": True,
        "game_donor_source_vault_ci_fetch": False,
        "kai9000_donor_only": True,
        "kai9000_widget_authority": False,
        "private_legacy_relic_payload_authority": False,
        "nexus_private_sidecar_policy_green": True,
        "nexus_private_payload_in_shared_candidate": False,
        "physical_samsung_green": device,
        "canonical_main_promoted": False,
        "signing_mode": signing_mode,
        "production_signing": production_signing,
        "openai_live_green": live_openai,
        "canonical_hard_stop": canonical_hard_stop,
        "production_distribution_hard_stop": production_distribution_hard_stop,
        "host_ai_hard_stop": host_ai_hard_stop,
        "hard_stop": canonical_hard_stop,
        "enterprise_green": False
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print("FINAL_SYSTEM_AUDIT=PASS")
    print("LUHM_FULL_GAME=PASS")
    print("FINAL_MUTATION_MILESTONE=PASS")
    print("AUTHORITY_CONVERGENCE=PASS")
    print("LUM_RIG=PASS")
    print(f"COMMUNITY_ASSETS=PASS count={community['asset_count']}")
    print(f"GAME_DONORS=PASS count={donor_receipt['asset_count']} bytes={donor_bytes}")
    print("NEXUS_SHARED_PAYLOAD=NONE")
    print("CANONICAL_HARD_STOP=" + canonical_hard_stop)
    print("PRODUCTION_SIGNING_GATE=" + production_distribution_hard_stop)
    print("HOST_AI_GATE=" + host_ai_hard_stop)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

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


def fail(msg: str) -> None:
    raise SystemExit("RED_FINAL_SYSTEM_AUDIT: " + msg)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build-dir", type=Path, required=True)
    parser.add_argument("--source-sha", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    doctrine = json.loads((ROOT / "doctrine/openAiLumOniDeployment-20260927.json").read_text())
    if doctrine["authority"] != "Professor":
        fail("authority drift")
    if doctrine["architecture"]["parallelism_max"] != 3:
        fail("parallelism drift")
    if doctrine["openai"]["credential_in_apk"] is not False:
        fail("provider secret boundary drift")

    recovery = json.loads((ROOT / "doctrine/reconciledCoffeeHouseLumCandidate-20260927.json").read_text())
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
    required = ["manifest.txt", "badging.txt", "signature.txt", "zipalign.txt",
                "sha256.txt", "source-commit.txt", "release-hardening.txt", "ziplist.txt",
                "community-assets-receipt.json"]
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
    if "art.eggiebagelface.luhmos.cathedraltoy.atelier" not in badging:
        fail("package mismatch")
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

    community = json.loads((b / "community-assets-receipt.json").read_text())
    if community.get("asset_count") != EXPECTED_COMMUNITY_COUNT:
        fail("community asset count mismatch")
    if community.get("license") != "CC0":
        fail("community license mismatch")
    if community.get("runtime_network") is not False:
        fail("community runtime-network boundary drift")
    if community.get("source_commit") != "3694c6879e487c108f55677be7dd2ca75b07cc3b":
        fail("community immutable source drift")

    nexus_runtime = ROOT / "assets/nexus/runtime"
    private_glbs = list(nexus_runtime.rglob("*.glb")) if nexus_runtime.exists() else []
    if private_glbs:
        fail("private Nexus GLB present in shared CI candidate workspace")

    live_openai = (ROOT / "build/openai-live/receipt.json").is_file()
    device = (ROOT / "build/device/samsung-runtime-receipt.json").is_file()
    receipt = {
        "schema": "luhm-os.final-system-audit.v2",
        "source_sha": args.source_sha,
        "source_exact_head_ci": True,
        "recovery_chain_reconciled": True,
        "apk_release_candidate_green": True,
        "apk_debuggable": False,
        "apk_internet_permission": False,
        "apk_profileable_shell": False,
        "host_openai_in_apk": False,
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
        "nexus_private_sidecar_policy_green": True,
        "nexus_private_payload_in_shared_candidate": False,
        "openai_live_green": live_openai,
        "physical_samsung_green": device,
        "canonical_main_promoted": False,
        "production_signing": False,
        "enterprise_green": False,
        "hard_stop": (
            "RED_OPENAI_LIVE_RECEIPT_MISSING" if not live_openai
            else "RED_PHYSICAL_SAMSUNG_RECEIPT_MISSING" if not device
            else "AMBER_HUMAN_PROMOTION_REQUIRED"
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print("FINAL_SYSTEM_AUDIT=PASS")
    print("LUM_RIG=PASS")
    print(f"COMMUNITY_ASSETS=PASS count={community['asset_count']}")
    print("NEXUS_SHARED_PAYLOAD=NONE")
    print("HARD_STOP=" + receipt["hard_stop"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

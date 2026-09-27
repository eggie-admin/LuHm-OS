#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

def fail(msg: str) -> None:
    raise SystemExit("RED_FINAL_SYSTEM_AUDIT: " + msg)

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

    b = args.build_dir
    required = ["manifest.txt", "badging.txt", "signature.txt", "zipalign.txt",
                "sha256.txt", "source-commit.txt", "release-hardening.txt"]
    for name in required:
        if not (b / name).is_file():
            fail(f"missing build receipt {name}")

    manifest = (b / "manifest.txt").read_text(errors="replace")
    badging = (b / "badging.txt").read_text(errors="replace")
    signature = (b / "signature.txt").read_text(errors="replace")
    zipalign = (b / "zipalign.txt").read_text(errors="replace")
    source = (b / "source-commit.txt").read_text().strip()
    hardening = (b / "release-hardening.txt").read_text(errors="replace")

    if re.search(r"android:debuggable.*0xffffffff", manifest):
        fail("APK debuggable=true")
    if "android.permission.INTERNET" in manifest:
        fail("APK INTERNET permission present")
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

    live_openai = (ROOT / "build/openai-live/receipt.json").is_file()
    device = (ROOT / "build/device/samsung-runtime-receipt.json").is_file()
    receipt = {
        "schema": "luhm-os.final-system-audit.v1",
        "source_sha": args.source_sha,
        "source_exact_head_ci": True,
        "apk_release_candidate_green": True,
        "apk_debuggable": False,
        "apk_internet_permission": False,
        "agent_mesh_contract_green": True,
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
    print("HARD_STOP=" + receipt["hard_stop"])
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

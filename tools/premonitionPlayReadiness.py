#!/usr/bin/env python3
"""Read-only Play release readiness checks. Never asserts a Play upload happened."""
import json
import re
from pathlib import Path

def main():
    preset = Path("export_presets.cfg").read_text(encoding="utf-8")
    project = Path("project.godot").read_text(encoding="utf-8")
    signed = Path(".github/workflows/samsung-lite-signed-beta.yml").read_text(encoding="utf-8")
    checks = {
        "godot_project_present": "[application]" in project,
        "android_preset_present": 'platform="Android"' in preset,
        "api36_configured": 'gradle_build/target_sdk="36"' in preset,
        "distinct_testing_package": 'art.eggiebagelface.luhmos.testing' in preset,
        "signing_gate_defined": "LUHM_BETA_SIGNING_P12_B64" in signed and "LUHM_BETA_SIGNER_SHA256" in signed,
        "play_aab_release_pipeline": False,
        "play_app_signing_verified": False,
        "play_console_listing_verified": False,
        "samsung_device_proof_verified": False,
        "play_internal_test_install_verified": False,
    }
    # The last five are external, end-to-end requirements; never infer proof from source code.
    receipt = {
        "schema": "luhm.premonition.playReadiness.v1",
        "status": "READY_FOR_SOURCE_AUDIT" if all(list(checks.values())[:5]) else "SOURCE_BLOCKED",
        "playPromotion": "STOP",
        "sourceChecks": checks,
        "nextMilestone": "produce versioned signed AAB in isolated CI with Play signing verification",
        "note": "An APK or F-Droid staging receipt is not Google Play installation proof.",
    }
    output = Path("build/premonition-play/readiness.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    if not all(list(checks.values())[:5]):
        raise SystemExit(1)

if __name__ == "__main__":
    main()

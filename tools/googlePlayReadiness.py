#!/usr/bin/env python3
"""Read-only, evidence-aware Google Play gate for the LuHm-OS Godot app.

An Android debug APK, API-level source setting, or Web export must never be
reported as a signed Google Play AAB. No secrets, uploads or builds here.
"""
from __future__ import annotations

import argparse
import configparser
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRESET = ROOT / "export_presets.cfg"
RELEASE_GATE = ROOT / "doctrine" / "finalFormPublicReleaseGateV1.json"
UPDATE_ID = ROOT / "doctrine" / "publicApkUpdateIdentityV1.json"


def parse_presets(data: str) -> list[dict]:
    cfg = configparser.RawConfigParser(interpolation=None, strict=True)
    cfg.optionxform = str
    cfg.read_string(data)
    presets: list[dict] = []
    for section in cfg.sections():
        if not re.fullmatch(r"preset\.\d+", section):
            continue
        index = section.split(".")[1]
        option_section = section + ".options"
        options = dict(cfg.items(option_section)) if cfg.has_section(option_section) else {}
        info = dict(cfg.items(section))
        presets.append({
            "name": info.get("name", "").strip('"'),
            "platform": info.get("platform", "").strip('"'),
            "exportPath": info.get("export_path", "").strip('"'),
            "options": {k: v.strip('"') for k, v in options.items()},
        })
    return presets


def audit(presets: list[dict], gate: dict, identity: dict) -> dict:
    android = [p for p in presets if p["platform"] == "Android"]
    debug = next((p for p in android if p["name"] == "Android Proposed"), None)
    release = [p for p in android if p["name"] == "Google Play Release"]
    opt = (debug or {}).get("options", {})
    configured_target = opt.get("gradle_build/target_sdk", "")
    try:
        target_sdk = int(configured_target)
    except (ValueError, TypeError):
        target_sdk = None

    icon_keys = (
        "launcher_icons/main_192x192",
        "launcher_icons/adaptive_foreground_432x432",
        "launcher_icons/adaptive_background_432x432",
    )
    icon_files = {key: opt.get(key, "") for key in icon_keys}
    icon_sources_valid = all(
        bool(value) and (ROOT / value.replace("res://", "")).is_file()
        for value in icon_files.values()
    )
    stable_identity = identity.get("reverseDomainIdentity", {})
    proofs = gate.get("requiredProofs", {})
    evidence = {
        "sourceTargetSdkAtLeast36": target_sdk is not None and target_sdk >= 36,
        "playReleasePresetConfigured": len(release) == 1,
        "playAabBuiltAndIndependentlyVerified": False,
        "nonDebugReleaseSignerLineageProven": proofs.get("androidStableReleaseSignerLineage") == "PROVEN",
        "stableAppIdLocked": stable_identity.get("stablePackageLockedAndSigned") is True,
        "dedicatedLauncherArtworkPresent": icon_sources_valid,
        "physicalSamsungInstallAndUpdateProven": (
            proofs.get("androidPhysicalFirstLaunch") == "PROVEN"
            and proofs.get("androidUpgradeRollbackPath") == "PROVEN"
        ),
        "publicAssetRightsCleared": proofs.get("publicArtRightsAndProvenance") == "PROVEN",
        "storeSubmissionAndPrivacyDeclarationsVerified": False,
        "professorExactFinalArtifactApproval": (
            gate.get("professorAuthority", {}).get("exactStableSignedArtifactReviewed") is True
        ),
    }
    # A typed source preset is NOT a release binary, even if someone names it
    # "Google Play Release". Binary SHA256, signer, target SDK and Play Console
    # submission require their own external receipts.
    source = {
        "androidPresetNames": [p["name"] for p in android],
        "existingDebugPackage": opt.get("package/unique_name", ""),
        "existingDebugVersionCode": opt.get("version/code", ""),
        "existingSourceTargetSdk": target_sdk,
        "debugOutput": (debug or {}).get("exportPath"),
        "separateReleasePackageCandidate": stable_identity.get("stablePackageCandidate"),
        "privateArtExcludedFromPublicByDefault": True,
    }
    return {
        "schema": "luhmOs.googlePlayReadiness.v1",
        "state": "SOURCE_PREFLIGHT_ONLY",
        "source": source,
        "evidence": evidence,
        "missing": [name for name, passed in evidence.items() if not passed],
        "googlePlayReady": all(evidence.values()),
        "googlePlayUploaded": False,
        "stableReleaseSigned": False,
        "crownStatus": "STOP",
        "noKeystoreOrPrivateModelReads": True,
    }


def self_test(presets: list[dict], gate: dict, identity: dict) -> None:
    base = audit(presets, gate, identity)
    assert base["source"]["existingSourceTargetSdk"] == 36, "unexpected source SDK baseline"
    assert base["evidence"]["sourceTargetSdkAtLeast36"], "SDK 36 no longer configured"
    assert not base["googlePlayReady"], "source alone cannot prove public release"
    assert not base["evidence"]["playAabBuiltAndIndependentlyVerified"]
    changed = json.loads(json.dumps(presets))
    debug = next(p for p in changed if p["name"] == "Android Proposed")
    debug["options"]["gradle_build/target_sdk"] = "35"
    assert not audit(changed, gate, identity)["evidence"]["sourceTargetSdkAtLeast36"], "SDK downgrade slipped through"
    changed = json.loads(json.dumps(presets))
    changed[0]["name"] = "Google Play Release"
    spoof = audit(changed, gate, identity)
    assert not spoof["evidence"]["playAabBuiltAndIndependentlyVerified"], "renamed preset forged AAB"
    assert not spoof["googlePlayReady"], "renamed preset forged approval"
    print("GOOGLE_PLAY_PREFLIGHT_NEGATIVE_TESTS=PASS")


def current_source_sha() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, stderr=subprocess.DEVNULL,
            text=True, timeout=5,
        ).strip()
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--require-ready", action="store_true")
    args = parser.parse_args()
    presets = parse_presets(PRESET.read_text(encoding="utf-8"))
    gate = json.loads(RELEASE_GATE.read_text(encoding="utf-8"))
    identity = json.loads(UPDATE_ID.read_text(encoding="utf-8"))
    if args.self_test:
        self_test(presets, gate, identity)
    report = audit(presets, gate, identity)
    report["sourceRef"] = current_source_sha()
    print(json.dumps(report, indent=2, sort_keys=True))
    if args.require_ready and not report["googlePlayReady"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

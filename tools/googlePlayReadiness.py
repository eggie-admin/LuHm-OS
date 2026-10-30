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


def play_release_source_contract(release: list[dict], identity: dict) -> dict:
    """Validate a proposed AAB source preset, never the binary or signer."""
    preset = release[0] if len(release) == 1 else {}
    options = preset.get("options", {})
    try:
        target_sdk = int(options.get("gradle_build/target_sdk", ""))
    except (ValueError, TypeError):
        target_sdk = None
    output = preset.get("exportPath", "")
    parts = output.split("/")
    safe_aab_path = (
        len(parts) >= 3 and parts[:2] == ["build", "android"]
        and all(part not in ("", ".", "..") for part in parts)
        and output.endswith(".aab")
    )
    package = options.get("package/unique_name", "")
    candidate = identity.get("reverseDomainIdentity", {}).get("stablePackageCandidate", "")
    valid = (
        len(release) == 1 and safe_aab_path and bool(candidate)
        and package == candidate and not package.endswith((".testing", ".beta"))
        and options.get("gradle_build/use_gradle_build") == "true"
        and options.get("architectures/arm64-v8a") == "true"
        and options.get("package/signed") == "true"
        and target_sdk is not None and target_sdk >= 36
    )
    return {
        "valid": bool(valid), "targetSdk": target_sdk,
        "package": package, "output": output,
    }


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
    release_source = play_release_source_contract(release, identity)
    release_opt = release[0]["options"] if len(release) == 1 else {}
    icon_files = {key: release_opt.get(key, "") for key in icon_keys}
    icon_sources_valid = all(
        bool(value) and (ROOT / value.replace("res://", "")).is_file()
        for value in icon_files.values()
    )
    stable_identity = identity.get("reverseDomainIdentity", {})
    proofs = gate.get("requiredProofs", {})
    evidence = {
        "sourceTargetSdkAtLeast36": (
            release_source["targetSdk"] is not None
            and release_source["targetSdk"] >= 36
        ),
        "playReleasePresetConfigured": release_source["valid"],
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
        "releaseSourceTargetSdk": release_source["targetSdk"],
        "releaseSourcePackage": release_source["package"],
        "releaseSourceOutput": release_source["output"],
        "releasePresetNamePresent": len(release) == 1,
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
    assert base["source"]["existingSourceTargetSdk"] is not None and base["source"]["existingSourceTargetSdk"] >= 36, "debug SDK floor regressed"
    assert not base["evidence"]["playAabBuiltAndIndependentlyVerified"], "source forged a built AAB"
    assert not base["googlePlayReady"], "source alone cannot prove public release"

    # A valid *proposal* still cannot prove an AAB, a durable signer or approval.
    changed = json.loads(json.dumps(presets))
    debug = next(p for p in changed if p["name"] == "Android Proposed")
    proposed = json.loads(json.dumps(debug))
    proposed["name"] = "Google Play Release"
    proposed["exportPath"] = "build/android/luhmos-proposed.aab"
    proposed["options"]["package/unique_name"] = identity["reverseDomainIdentity"]["stablePackageCandidate"]
    changed.append(proposed)
    valid_source = audit(changed, gate, identity)
    assert valid_source["evidence"]["playReleasePresetConfigured"], "valid AAB source shape rejected"
    assert valid_source["evidence"]["sourceTargetSdkAtLeast36"], "release SDK 36 rejected"
    assert not valid_source["evidence"]["playAabBuiltAndIndependentlyVerified"]
    assert not valid_source["googlePlayReady"]

    # A named preset is insufficient. Reject APKs, identity drift, unsafe
    # paths, missing Gradle/ARM64 and SDK downgrade independently.
    for field, value in (
        ("exportPath", "build/android/luhmos-proposed.apk"),
        ("exportPath", "../outside/luhmos.aab"),
        ("package/unique_name", "art.eggiebagelface.luhmos.testing"),
        ("gradle_build/use_gradle_build", "false"),
        ("architectures/arm64-v8a", "false"),
        ("package/signed", "false"),
        ("gradle_build/target_sdk", "35"),
    ):
        altered = json.loads(json.dumps(changed))
        candidate = altered[-1]
        if field == "exportPath":
            candidate["exportPath"] = value
        else:
            candidate["options"][field] = value
        report = audit(altered, gate, identity)
        assert not report["evidence"]["playReleasePresetConfigured"], f"invalid release preset passed: {field}={value}"
        if field == "gradle_build/target_sdk":
            assert not report["evidence"]["sourceTargetSdkAtLeast36"], "release SDK downgrade passed"

    duplicate = json.loads(json.dumps(changed))
    duplicate.append(json.loads(json.dumps(proposed)))
    assert not audit(duplicate, gate, identity)["evidence"]["playReleasePresetConfigured"], "duplicate release preset passed"
    renamed = json.loads(json.dumps(presets))
    next(p for p in renamed if p["name"] == "Android Proposed")["name"] = "Google Play Release"
    assert not audit(renamed, gate, identity)["evidence"]["playReleasePresetConfigured"], "renamed debug APK passed"
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

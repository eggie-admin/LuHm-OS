#!/usr/bin/env python3
"""Fail closed on signed beta workflow shell and signing policy regressions.

Source-level checks only: never claims a real APK, owner secret, or tablet proof.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/samsung-lite-signed-beta.yml"


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise SystemExit("RED_SIGNED_BETA_WORKFLOW:" + reason)


def check() -> None:
    content = WORKFLOW.read_text(encoding="utf-8")
    for marker in (
        "      - name: Owner CAST and source gate",
        "      - name: Configure Godot Android SDK paths",
        "      - name: Owner-held beta keystore",
        "      - name: Stage isolated non-debug beta preset",
        "      - name: Export ARM64 non-debug beta",
        "      - name: Verify exact APK identity and signer",
        "      - name: Prepare offline F-Droid beta workspace (no publication)",
        "      - name: Upload private signed beta candidate",
        "      - name: Remove keystore from runner",
        "          python3 tests/testSignedBetaWorkflow.py",
        "          echo 'FDROID_OFFLINE_CANDIDATE_READY_NOT_SIGNED_NOT_PUBLISHED'",
    ):
        require(marker in content, "missing:" + marker.strip())

    start = content.index("      - name: Prepare offline F-Droid beta workspace")
    end = content.index("      - name: Upload private signed beta candidate", start)
    scope = content[start:end]
    lines = scope.splitlines()
    require(not any(line.rstrip().endswith(chr(92) * 2) for line in lines),
            "double shell continuation: commands would split incorrectly")

    for command in ("python3 tools/stageFdroidTabletBeta.py",
                    "python3 tools/prepareFdroidRepoCandidate.py"):
        matches = [line.rstrip() for line in lines if command in line]
        require(len(matches) == 1 and matches[0].endswith(chr(92)),
                "missing command continuation:" + command)

    for arg in ("--expected-source", "--expected-signer", "--expected-apk-sha256",
                "--aapt", "--apksigner"):
        require(arg in scope, "missing binary verification:" + arg)

    for secret in ("LUHM_BETA_SIGNING_P12_B64", "LUHM_BETA_SIGNING_PASSWORD",
                   "LUHM_BETA_SIGNING_ALIAS", "LUHM_BETA_SIGNER_SHA256"):
        require("secrets." + secret in content, "signing secret contract:" + secret)

    require("test \"$GITHUB_ACTOR\" ==" in content,
            "owner-only dispatch missing")
    require("test \"$SOURCE_REF\" ==" in content,
            "exact-current-main source gate missing")
    require("GODOT_ANDROID_KEYSTORE_RELEASE_PATH=" in content,
            "persistent release keystore not configured")
    require('export/android/android_sdk_path = "$ANDROID_HOME"' in content
            and 'export/android/java_sdk_path = "$JAVA_HOME"' in content,
            "Godot Android SDK locations not set")
    require("--export-release 'Android Proposed'" in content,
            "non-debug export missing")
    require('applicationId":"art.eggiebagelface.luhmos.beta' in content,
            "stable beta identity missing")
    require("false" in content and "deviceProof" in content
            and "betaUpgradeProof" in content,
            "false device/upgrade receipts missing")
    require("gh release create" not in content
            and "fdroid update" not in content
            and "firebase appdistribution" not in content,
            "unapproved public distribution")
    require("retention-days: 14" in content,
            "private artifact retention missing")
    print("GREEN_SIGNED_BETA_SOURCE_AND_STAGING_CONTRACT")
    print("NO_OWNER_KEY_OR_REAL_APK_OR_DEVICE_PROOF_FROM_SOURCE_TEST")


if __name__ == "__main__":
    check()

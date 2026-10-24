#!/usr/bin/env python3
"""Fail closed on signed beta workflow shell and signing policy regressions.

Source-level checks only: never claims a real APK, owner secret, or tablet proof.
"""
from pathlib import Path
import copy
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/samsung-lite-signed-beta.yml"


def check_environment_policy() -> None:
    # GitHub GET responses put prevent_self_review inside required_reviewers,
    # unlike the top-level field accepted by the environment PUT endpoint.
    valid = {
        "protection_rules": [{"type": "required_reviewers",
                              "prevent_self_review": True,
                              "reviewers": [{"type": "User", "reviewer": {"login": "reviewer"}}]}],
        "deployment_branch_policy": {"protected_branches": True},
    }
    cases = [("real GET shape", valid, True)]
    for label, mutate in (
        ("self-review enabled", lambda p: p["protection_rules"][0].update(prevent_self_review=False)),
        ("missing self-review field", lambda p: p["protection_rules"][0].pop("prevent_self_review")),
        ("empty reviewer list", lambda p: p["protection_rules"][0].update(reviewers=[])),
        ("missing reviewer list", lambda p: p["protection_rules"][0].pop("reviewers")),
        ("no reviewer rule", lambda p: p.update(protection_rules=[])),
        ("unprotected branches", lambda p: p["deployment_branch_policy"].update(protected_branches=False)),
        ("missing branch policy", lambda p: p.pop("deployment_branch_policy")),
    ):
        candidate = copy.deepcopy(valid)
        mutate(candidate)
        # A top-level lookalike must not override an unsafe nested rule.
        candidate["prevent_self_review"] = True
        cases.append((label, candidate, False))
    for path in (WORKFLOW, ROOT / "tools/auditBetaSigningPolicy.sh",
                 ROOT / "tools/provisionOwnerBetaSigner.sh"):
        filters = re.findall(r"jq -e '([^']+)'", path.read_text())
        filters = [f for f in filters if "required_reviewers" in f]
        require(len(filters) == 1, "one environment policy filter:" + path.name)
        for label, policy, expected in cases:
            result = subprocess.run(["jq", "-e", filters[0]], input=json.dumps(policy),
                                    text=True, capture_output=True, timeout=5)
            require((result.returncode == 0) == expected,
                    "environment policy:" + path.name + ":" + label)


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise SystemExit("RED_SIGNED_BETA_WORKFLOW:" + reason)


def check() -> None:
    check_environment_policy()
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
    require("GODOT_ANDROID_KEYSTORE_RELEASE_PATH:" in content
            and "GODOT_ANDROID_KEYSTORE_RELEASE_USER:" in content
            and "GODOT_ANDROID_KEYSTORE_RELEASE_PASSWORD:" in content,
            "step-scoped release signing variables missing")
    require("GODOT_ANDROID_KEYSTORE_RELEASE_PASSWORD=$BETA_PASSWORD" not in content,
            "signing password must not enter GITHUB_ENV")
    require("-storepass:env BETA_PASSWORD" in content,
            "keytool must not receive password in process command line")
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
    require("environment:" in content and "name: luhm-beta-signing" in content,
            "owner signing requires protected environment")
    require("PROTECTED_SIGNING_ENVIRONMENT_GREEN" in content
            and "prevent_self_review == true" in content
            and "required_reviewers" in content,
            "server environment safeguards missing")
    require("tools/checkBetaReleaseBaseline.py" in content
            and "BETA_VERSION_CODE" in content
            and "ACTUAL_VERSION" in content,
            "signed release version floor and exported APK version verification missing")
    bootstrap = (ROOT / "tools/provisionOwnerBetaSigner.sh").read_text()
    require('SIGNING_ENV="luhm-beta-signing"' in bootstrap
            and '--repo "$REPO" --env "$SIGNING_ENV"' in bootstrap,
            "owner signer bootstrap must use environment-only secrets")
    require("secrets.LUHM_SIGNING_POLICY_READ_TOKEN" in content,
            "read-only governance token missing")
    require("GH_TOKEN: ${{ github.token }}\n        run: |\n          set -euo pipefail\n          ENV_INFO" not in content,
            "default workflow token cannot inspect admin governance")
    require("(.reviewers // []) | length > 0" in content,
            "require actual independent reviewer assignment")
    require((ROOT / "tools/auditBetaSigningPolicy.sh").is_file(),
            "owner policy inspection helper missing")
    require("VERIFIED_FIRST_BETA" in bootstrap
            and "repo_secret_names=" in bootstrap,
            "first-beta signing key must never be minted without verified history")
    print("GREEN_SIGNED_BETA_SOURCE_AND_STAGING_CONTRACT")
    print("NO_OWNER_KEY_OR_REAL_APK_OR_DEVICE_PROOF_FROM_SOURCE_TEST")


if __name__ == "__main__":
    check()

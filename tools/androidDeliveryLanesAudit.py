#!/usr/bin/env python3
"""Read-only proposed-to-beta Android delivery and lowercase naming audit."""
from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCTRINE = "doctrine/androidDeliveryLanesV1.json"
PROPOSED = "doctrine/proposedWorkingLaneV1.json"
NAMING = "doctrine/namingNamespaceCanonV1.json"
NATIVE = "androidWeb3Plugin/plugin/src/main/java/art/eggiebagelface/luhmos/web3/AndroidWeb3CockpitPlugin.kt"
GRADLE = "androidWeb3Plugin/plugin/build.gradle.kts"


def read_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def validate(policy: dict, proposed: dict, naming: dict, native: str, gradle: str) -> list[str]:
    issues: list[str] = []

    def require(ok: bool, reason: str) -> None:
        if not ok:
            issues.append(reason)

    namespace = naming.get("namespaces", {}).get("kebabCase", {})
    rules = policy.get("naming", {})
    slug_pattern = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
    app_id_pattern = r"^[a-z][a-z0-9]*(?:\.[a-z][a-z0-9]*)+$"
    require(policy.get("schema") == "luhmOs.androidDeliveryLanes.v1", "schema drift")
    require(policy.get("authority") == "Professor", "Professor authority drift")
    require(policy.get("crownStatus") == "STOP", "Crown authority drift")
    require(policy.get("status") == "SOURCE_CONFIGURED_CANDIDATE", "runtime promotion claim")
    require(rules.get("canon") == NAMING, "missing naming canon")
    require(namespace.get("law") == "all lowercase" and namespace.get("regex") == slug_pattern,
            "canonical lowercase kebab namespace drift")
    require(rules.get("transportSlugPattern") == slug_pattern, "transport regex drift")
    require(rules.get("transportSlugConvention") == "all lowercase kebab-case", "transport rule drift")
    require(rules.get("internalCodeConvention") == "camelHump", "internal camelHump drift")
    require(rules.get("androidApplicationIdPattern") == app_id_pattern,
            "Android application IDs need lowercase dotted identifiers")
    for slug in rules.get("examples", []):
        require(isinstance(slug, str) and re.fullmatch(slug_pattern, slug) is not None,
                "invalid transport slug: " + str(slug))
    require(len(rules.get("examples", [])) >= 3, "missing naming samples")

    hook = proposed.get("androidPrototypeDelivery", {})
    require(hook.get("contract") == DOCTRINE, "proposed lane missing Android policy")
    require(hook.get("proposedMayExperimentBeforeBetaHardening") is True, "prototype blocked by beta")
    require(hook.get("betaNeedsSeparateSecurityAndDeviceEvidence") is True, "beta proof shortcut")
    require(hook.get("currentBuildAutomationGate") ==
            "FORGE_CAST_UNCHANGED_PENDING_FOCUSED_MIGRATION", "forged Forge auto-build activation")
    lanes = policy.get("lanes", {})
    proto, beta, release = (lanes.get(name, {}) for name in ("proposed", "beta", "release"))
    require(proto.get("isolated") is True and proto.get("localAutomatedBuildDesired") is True,
            "first-time isolated rapid prototype lane missing")
    require(proto.get("disposableDebugSignerOnly") is True and
            proto.get("productionSecrets") is False and proto.get("externalPublication") is False and
            proto.get("publicNetworkExposure") is False and proto.get("providerSpend") is False,
            "prototype leaked into privileged or public lane")
    require(proto.get("status") == "DESIGN_ONLY_FAST_PATH_NOT_YET_ACTIVE" and
            proto.get("forgeFastPathImplementation") == "PENDING_FOCUSED_CHANGE_TO_CAST_GATE",
            "unproven prototype automation enabled")
    for name in ("requireSecureMessageBoundary", "requireDependencyAndSecretScanning",
                 "requireMinimumRuntimeTests", "requirePhysicalSamsungDeviceSmoke",
                 "requireSignedTesterArtifactAndCertificateLineage", "requireVersionAndUpgradeRollbackEvidence"):
        require(beta.get(name) is True, "beta gate missing: " + name)
    for name in ("prohibitDebugCertificate", "requireLintUnitInstrumentationAndUiTests",
                 "requireNoKnownCriticalVulnerabilities", "requireProvenUpdatePath",
                 "requireFinalProfessorPublicationApproval", "requireArtifactSha256AndProvenance"):
        require(release.get(name) is True, "release gate missing: " + name)
    platform = policy.get("platform", {})
    require(platform.get("compileSdkDoesNotProveTargetSdk") is True and
            platform.get("targetSdkForNewHandsetPlaySubmissionFrom20260831") == 36 and
            release.get("requireGooglePlayTargetSdkAtLeast") == 36,
            "Google Play handset target SDK check missing")
    require(platform.get("endApplicationTargetSdkCurrentEvidence") ==
            "UNKNOWN_UNTIL_EXPORTED_APK_OR_AAB_VERIFIED", "target SDK improperly claimed")
    require("compileSdk = 36" in gradle, "Android library compile SDK drift")
    for marker in ("MAX_BRIDGE_MESSAGE_CHARS = 512", "raw.length > MAX_BRIDGE_MESSAGE_CHARS",
                   '"bridge_payload_too_large"', '"bridge_keys_rejected"',
                   "payload.keys().asSequence().toSet() != expectedKeys",
                   "isMainFrame", "WebViewCompat.addWebMessageListener",
                   "sourceOrigin.toString() != LOCAL_ORIGIN", "allowFileAccess = false",
                   "WebSettings.MIXED_CONTENT_NEVER_ALLOW"):
        require(marker in native, "WebView security contract missing: " + marker)
    require("addJavascriptInterface" not in native, "unsafe JavaScript interface enabled")
    for name in ("agentQuarantineUnchanged", "noCredentialsInGit",
                 "policyDoesNotBypassExistingForgeGateUntilImplemented",
                 "sourceCiDoesNotProveInstalledApp"):
        require(policy.get("invariants", {}).get(name) is True, "missing invariant: " + name)
    return issues


def run_self_test(policy: dict, proposed: dict, naming: dict, native: str, gradle: str) -> list[str]:
    errors: list[str] = []
    def rejected(label: str, modified_policy: dict, modified_proposed: dict = proposed,
                 modified_native: str = native) -> None:
        if not validate(modified_policy, modified_proposed, naming, modified_native, gradle):
            errors.append("negative control accepted: " + label)

    bad = copy.deepcopy(policy)
    bad["naming"]["examples"][0] = "Android-Proposed-Debug"
    rejected("uppercase slug", bad)
    bad = copy.deepcopy(policy)
    bad["lanes"]["proposed"]["productionSecrets"] = True
    rejected("secrets in prototype", bad)
    bad = copy.deepcopy(policy)
    bad["lanes"]["beta"]["requireSecureMessageBoundary"] = False
    rejected("missing beta bridge check", bad)
    bad = copy.deepcopy(policy)
    bad["lanes"]["release"]["requireGooglePlayTargetSdkAtLeast"] = 35
    rejected("stale release target SDK", bad)
    bad = copy.deepcopy(policy)
    bad["lanes"]["proposed"]["status"] = "ACTIVE"
    rejected("fake prototype gate release", bad)
    rejected("missing size guard", copy.deepcopy(policy),
             modified_native=native.replace("raw.length > MAX_BRIDGE_MESSAGE_CHARS", "false"))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    policy = read_json(DOCTRINE)
    proposed = read_json(PROPOSED)
    naming = read_json(NAMING)
    native = (ROOT / NATIVE).read_text(encoding="utf-8")
    gradle = (ROOT / GRADLE).read_text(encoding="utf-8")
    errors = validate(policy, proposed, naming, native, gradle)
    if args.self_test:
        errors.extend(run_self_test(policy, proposed, naming, native, gradle))
    print(json.dumps({
        "schema": "luhmOs.androidDeliveryLanesAudit.v1",
        "status": "GREEN_SOURCE_ONLY" if not errors else "RED_SOURCE_ONLY",
        "scope": "naming, source policy and static WebView guards only",
        "runtimeApkBuilt": False,
        "physicalDeviceProven": False,
        "prototypeForgeGateModified": False,
        "issues": errors,
    }, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

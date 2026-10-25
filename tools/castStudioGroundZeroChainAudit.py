#!/usr/bin/env python3
"""Static, read-only CAST chain inspection: Codespaces ground zero -> studio -> ground zero.

This tool NEVER provisions hardware, enters Codespaces, starts servers, builds,
installs, merges, publishes, dispatches CAST, or grants runtime/crown authority.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
contractPath = root / "doctrine/castStudioGroundZeroChainV1.json"
taskIds = [
    "groundHardware", "ubuntuTrust", "toolchainRuntime", "remoteStudio",
    "runtimeReverse", "trustReverse", "hardwareReverse",
]
phaseLaws = ["UP", "UP", "UP", "APEX", "DOWN", "DOWN", "DOWN"]
levels = [0, 1, 2, 3, 2, 1, 0]
sourcePattern = re.compile(r"[0-9a-f]{40}\Z")
scopePattern = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}\Z")
slugPattern = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
identityPattern = re.compile(r"[a-z][A-Za-z0-9]*\Z")
sourceLaw = "AI proposes. Policy authorizes. CI proves. Human promotes."


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError("RED_CAST_STUDIO_CHAIN_" + reason)


def inspect(document: dict, *, checkPaths: bool = True) -> dict:
    require(isinstance(document, dict), "DOCUMENT_TYPE")
    require(document.get("schema") == "luhmOs.castStudioGroundZeroChain.v1", "SCHEMA")
    require(document.get("status") == "SOURCE_CANDIDATE_NOT_RUNTIME_VERIFIED", "SOURCE_STATUS")
    require(document.get("sourceLaw") == sourceLaw, "SOURCE_LAW")
    require(document.get("ownerRepository") == "eggie-admin/LuHm-OS", "REPO_ID")
    require(document.get("exactSource") == "RESOLVE_AT_EACH_INSPECTION_NO_STALE_SHA", "FRESHNESS")
    studio = document.get("targetStudio", {})
    require(studio.get("platform") == "GitHub Codespaces", "STUDIO_PROVIDER")
    require(studio.get("image") == "ubuntu:26.04", "STUDIO_IMAGE")
    require(studio.get("githubCodespacesKernelIsProviderHosted") is True, "KERNEL_BOUNDARY")
    require(studio.get("alwaysOnGuaranteed") is False, "PERSISTENCE_CLAIM")
    require(studio.get("renderIsDifferentHost") is True, "HOST_CONFLATION")
    for flag in ("claimRunning", "claimHardwareAccess", "claimPhysicalHost", "standaloneUbuntuVm"):
        require(studio.get(flag) is False, "UNVERIFIED_" + flag)
    law = document.get("chainLaw", {})
    require(law.get("ascent") == [0, 1, 2, 3] and law.get("descent") == [3, 2, 1, 0], "BIDIRECTIONAL_ORDER")
    require([x.get("index") for x in law.get("foundationalLayers", [])] == [0, 1, 2, 3], "LAYERS")
    for flag in (
        "softwareCompositionAxesIndependent",
        "technologyEscalation0To3GrantsNoAuthority",
        "evidenceRecheckedOnReturn", "oneScheduledRunner",
        "noAutomaticHostAction", "noAutomaticCastDispatch",
        "noPublicRelease", "noUnquarantine", "noPaidResources",
        "noSecretExposure", "noReformatOrDeviceInstall"
    ):
        require(law.get(flag) is True, "LAW_" + flag)
    require(law.get("maxSupportParallelInspections") == 3, "WORKER_BUDGET")
    require(law.get("concurrentMutableSourceLanes") == 1, "MUTATION_LANE")
    require(law.get("attemptsPerTick") == 2, "BOUNDED_ATTEMPTS")
    stage = document.get("stageReadiness", {})
    require(stage.get("outcome") == "STAGING_PREPARATION_ONLY", "STAGING_CLAIM")
    for key in (
        "allSevenStageEvidenceRequired", "exactSourceCIBeforeReview",
        "codespaceBuildAndSmokeRequired", "renderAndChatGptMountIndependentlyVerified",
        "samsungProofSeparatelyRequired", "explicitProfessorScopedCastNeededForActualBuild",
        "originalMediaRightsHumanReviewed", "developerCannotSelfPromote"
    ):
        require(stage.get(key) is True, "PROOF_" + key)
    require(stage.get("initialClaim") == "UNVERIFIED_NOT_STAGED_FOR_LIVE_DEPLOYMENT", "INITIAL_CLAIM")
    # Device composition has three levels and a fourth, downward proof note.
    # One cross-platform experience NEVER implies a cross-platform Android APK.
    mobile = document.get("mobileComposition", {})
    require(mobile.get("schema") == "luhmOs.castCrossPlatformComposition.v1", "MOBILE_SCHEMA")
    require(mobile.get("status") == "SOURCE_POLICY_ONLY_NO_PLATFORM_RELEASE_PROOF", "MOBILE_STATUS")
    require(mobile.get("universalProductPrinciple") ==
            "ONE_SHARED_EXPERIENCE_MULTIPLE_PLATFORM_DELIVERY_ADAPTERS", "UNIVERSALITY")
    require(mobile.get("zeroInstallInterpretation") == "BROWSER_LINK_WITH_NO_NATIVE_PACKAGE_INSTALL", "ZERO_INSTALL")
    require(mobile.get("userGestureMayStillBeRequired") is True, "HUMAN_GESTURE")
    levels = mobile.get("threeLevels", [])
    require(isinstance(levels, list) and len(levels) == 3, "THREE_LEVELS")
    require([x.get("index") for x in levels] == [0, 1, 2], "LEVEL_ORDER")
    require([x.get("id") for x in levels] ==
            ["deviceHardwareDelivery", "machineAbiFirmwareKernel", "appRuntimePackaging"], "LEVEL_IDS")
    require([x.get("displaySlug") for x in levels] ==
            ["device-hardware-delivery", "machine-abi-firmware-kernel", "app-runtime-packaging"], "LEVEL_SLUGS")
    for level in levels:
        require(isinstance(level.get("objective"), str) and len(level["objective"]) > 30, "LEVEL_OBJECTIVE")
    require([x.get("target") for x in levels[0].get("crossPlatform", [])] ==
            ["android", "samsung", "iphone"], "DEVICE_TARGETS")
    require(levels[0].get("iPhoneCanInstallApk") is False, "IOS_APK")
    require(levels[0].get("nativePackageOutputIsNotUniversal") is True, "NATIVE_FORMAT_SPLIT")
    require(levels[1].get("androidPolicy") == "PRESERVE_OEM_STOCK_KERNEL_GKI_KMI_VENDOR_MODULES", "KERNEL_POLICY")
    require(levels[1].get("iosPolicy") == "NO_KERNEL_OR_FIRMWARE_MUTATION_APP_SANDBOX_ONLY", "IOS_KERNEL_POLICY")
    for field in ("neverFlashFirmware", "neverReplaceVendorKernel", "noBlindMainlineMigration"):
        require(levels[1].get(field) is True, "FIRMWARE_GUARD_" + field)
    require(levels[2].get("initialNativeIosStatus") == "PARKED", "IOS_NATIVE_STATE")
    for field in ("noAutomaticInstall", "noSecretInBrowser", "noUserVisibleCliRequired",
                  "noDuplicateRenderEngineByDefault"):
        require(levels[2].get(field) is True, "APP_GUARD_" + field)
    note = mobile.get("fourthNote", {})
    require(note.get("id") == "groundZeroReprise" and
            note.get("displaySlug") == "ground-zero-reprise", "FOURTH_NOTE")
    require(note.get("notClaimedUntilRuntimeEvidence") is True and
            note.get("finalGate") == "PROFESSOR_HUMAN_APPROVAL_NO_AUTOMATIC_CROWN",
            "FOURTH_NOTE_AUTHORITY")
    require(len(note.get("checks", [])) >= 7, "REPRISE_EVIDENCE")
    distribution = mobile.get("distribution", {})
    require(distribution.get("androidApk") == "ANDROID_ONLY_INSTALLABLE_ARTIFACT", "APK_SCOPE")
    require(distribution.get("iosNative") ==
            "SEPARATE_IOS_SIGNING_APPLE_DISTRIBUTION_IF_LATER_APPROVED", "APPLE_SCOPE")
    require(distribution.get("iosCannotExecuteApk") is True, "IOS_BINARY_BOUNDARY")
    require(distribution.get("unownedDeviceSilentNativeInstallPromised") is False, "SILENT_INSTALL_CLAIM")
    require(distribution.get("ownedManagedDeviceSilentNativeInstallRequiresApprovedMdm") is True, "MDM_POLICY")
    require(all(value is False for value in mobile.get("runtimeEvidence", {}).values()), "RUNTIME_CLAIMS")
    for field in ("userMustNotFlashOrInstallKernel",):
        require(mobile.get(field) is True, "USER_KERNEL_GUARD")
    for field in ("buildDispatched", "promotion"):
        require(mobile.get(field) is False, "MOBILE_AUTHORITY_" + field)
    require(mobile.get("crownStatus") == "STOP", "MOBILE_CROWN")
    tasks = document.get("tasks")
    require(isinstance(tasks, list) and len(tasks) == 7, "TASK_COUNT")
    require([t.get("id") for t in tasks] == taskIds, "TASK_ORDER")
    require([t.get("leg") for t in tasks] == phaseLaws, "ASCENT_DESCENT")
    require([t.get("layer") for t in tasks] == levels, "LAYER_ORDER")
    require([t.get("order") for t in tasks] == list(range(7)), "ORDER")
    for index, item in enumerate(tasks):
        require(identityPattern.fullmatch(item["id"]) is not None, "TASK_ID")
        require(slugPattern.fullmatch(item.get("slug", "")) is not None, "DISPLAY_SLUG")
        require(item.get("dependsOn") == ([] if index == 0 else [tasks[index-1]["id"]]), "DAG")
        require(item.get("initialState") == "UNKNOWN_REQUIRES_CURRENT_EVIDENCE", "EVIDENCE_TRUTH")
        require(item.get("executionAllowed") is False and item.get("buildDispatched") is False, "EXECUTION_CLAIM")
        for field in ("target", "next"):
            require(isinstance(item.get(field), str) and len(item[field]) >= 15, "TASK_" + field)
        require(len(item.get("evidence", [])) >= 3, "MISSING_EVIDENCE")
        require(len(item.get("refs", [])) >= 2, "MISSING_SOURCE_REFS")
        for rel in item["refs"]:
            require(re.fullmatch(r"[A-Za-z0-9_./-]+", rel) and ".." not in Path(rel).parts, "PATH_TRAVERSAL")
            if checkPaths:
                require((root / rel).is_file(), "SOURCE_REF_NOT_FOUND")
    for key in ("sourceWritesAllowed", "buildDispatched", "hostMountVerified", "runtimeVerified", "promotion"):
        require(document.get(key) is False, "AUTHORITY_" + key)
    require(document.get("crownStatus") == "STOP", "CROWN")
    return {
        "layerCount": 4,
        "taskCount": 7,
        "up": tasks[:4],
        "down": tasks[4:],
        "sourceVerifiedOnly": True,
    }


def preview(sourceRef: str, scopeId: str, *, document: dict | None = None) -> dict:
    require(sourcePattern.fullmatch(sourceRef) is not None, "SOURCE_REF")
    require(scopePattern.fullmatch(scopeId) is not None, "SCOPE_ID")
    data = document if document is not None else json.loads(contractPath.read_text(encoding="utf-8"))
    info = inspect(data)
    return {
        "schema": "luhmOs.castStudioGroundZeroPreview.v1",
        "status": "SOURCE_ARRAY_ONLY_CODESPACE_RUNTIME_UNVERIFIED",
        "sourceRef": sourceRef,
        "scopeId": scopeId,
        "platform": "GitHub Codespaces",
        "osImageTarget": "ubuntu:26.04",
        "taskCount": info["taskCount"],
        "mobileComposition": {
            "schema": data["mobileComposition"]["schema"],
            "status": data["mobileComposition"]["status"],
            "threeLevels": [
                {"index": level["index"], "id": level["id"], "displaySlug": level["displaySlug"]}
                for level in data["mobileComposition"]["threeLevels"]
            ],
            "fourthNote": data["mobileComposition"]["fourthNote"]["displaySlug"],
            "iphoneCanExecuteApk": False,
            "zeroNativeInstallWebTarget": True,
            "nativeInstallSilentWithoutManagement": False,
            "livePlatformProof": False,
            "buildDispatched": False,
            "crownStatus": "STOP",
        },
        "tasks": [
            {
                "id": t["id"], "slug": t["slug"], "leg": t["leg"], "layer": t["layer"],
                "evidenceRequired": t["evidence"], "next": t["next"],
                "status": t["initialState"], "dependsOn": t["dependsOn"],
                "executionAuthorized": False
            } for t in data["tasks"]
        ],
        "parallelReadOnlyInspectionsMax": 3,
        "concurrentSourceMutationsMax": 1,
        "codespaceRunningProven": False,
        "hostMountVerified": False,
        "buildDispatched": False,
        "castEnvelopesGranted": 0,
        "liveDeployAuthorized": False,
        "crownStatus": "STOP",
    }


def selfTest() -> None:
    original = json.loads(contractPath.read_text(encoding="utf-8"))
    assert inspect(original)["taskCount"] == 7
    sample = preview("a" * 40, "professor/ubuntu-cast-studio")
    assert [x["layer"] for x in sample["tasks"]] == levels
    assert sample["buildDispatched"] is False and sample["codespaceRunningProven"] is False
    assert sample["castEnvelopesGranted"] == 0 and sample["crownStatus"] == "STOP"
    for key, value in (
        ("sourceWritesAllowed", True), ("runtimeVerified", True),
        ("crownStatus", "GREEN"), ("promotion", True)
    ):
        bad = copy.deepcopy(original)
        bad[key] = value
        try: inspect(bad)
        except ValueError: pass
        else: raise AssertionError("Unsafe contract state accepted")
    for field, value in (
        ("layer", 3), ("leg", "APEX"), ("slug", "HardwareReverse"),
        ("initialState", "GREEN"), ("executionAllowed", True)
    ):
        bad = copy.deepcopy(original)
        bad["tasks"][-1][field] = value
        try: inspect(bad)
        except ValueError: pass
        else: raise AssertionError("Unsafe layer/task claim accepted")
    for mutate in (
        lambda obj: obj["mobileComposition"]["threeLevels"].pop(),
        lambda obj: obj["mobileComposition"]["threeLevels"][0].__setitem__("iPhoneCanInstallApk", True),
        lambda obj: obj["mobileComposition"]["threeLevels"][1].__setitem__("neverReplaceVendorKernel", False),
        lambda obj: obj["mobileComposition"]["distribution"].__setitem__("iosCannotExecuteApk", False),
        lambda obj: obj["mobileComposition"]["distribution"].__setitem__("unownedDeviceSilentNativeInstallPromised", True),
        lambda obj: obj["mobileComposition"]["runtimeEvidence"].__setitem__("iphoneNativeBuildProof", True),
        lambda obj: obj["mobileComposition"]["fourthNote"].__setitem__("notClaimedUntilRuntimeEvidence", False)
    ):
        bad = copy.deepcopy(original)
        mutate(bad)
        try: inspect(bad)
        except ValueError: pass
        else: raise AssertionError("Cross-platform binary/kernel/user control drift accepted")
    assert sample["mobileComposition"]["iphoneCanExecuteApk"] is False
    assert sample["mobileComposition"]["livePlatformProof"] is False
    for candidate in ("main", "f" * 39):
        try: preview(candidate, "professor/ubuntu-cast-studio")
        except ValueError: pass
        else: raise AssertionError("Unpinned source accepted")
    print("CAST_STUDIO_GROUND_ZERO_SEVEN_STAGE_SOURCE_AUDIT_GREEN_NOT_RUNTIME")


def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only source-stage audit of ground-zero -> Ubuntu studio -> ground-zero")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--source-ref")
    parser.add_argument("--scope-id")
    args = parser.parse_args()
    if args.self_test:
        selfTest()
    elif args.source_ref and args.scope_id:
        print(json.dumps(preview(args.source_ref, args.scope_id), indent=2))
    else:
        parser.error("Use --self-test or --source-ref 40HEX --scope-id SCOPE")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Source-only four-platform plugin encapsulation and update-boundary audit."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "doctrine/fourTargetPluginEncapsulationV1.json"
SOURCE = ROOT / "doctrine/currentSourceTruthV3.json"
REMOTE = ROOT / "doctrine/selfHostedRemoteUpdatesV1.json"
STABLE = ROOT / "doctrine/stablePluginUpdateSpineV1.json"

CANONICAL = re.compile(r"^[a-z][A-Za-z0-9]*$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
SHA40 = re.compile(r"^[0-9a-f]{40}$")
FAMILIES = {"androidSamsung", "iosIphone", "linuxDesktop", "windowsDesktop"}
LANES = ["testing", "proposed", "beta", "betaLts", "stable"]


def audit(doc: dict, source: dict, remote: dict, stable: dict) -> list[str]:
    problems: list[str] = []
    def need(condition, error):
        if not condition:
            problems.append(error)

    need(doc.get("schema") == "luhmOs.fourTargetPluginEncapsulation.v1", "SCHEMA_DRIFT")
    need(doc.get("status") == "SOURCE_PROPOSAL_NOT_DEPLOYED", "FALSE_SOURCE_GREEN")
    need(doc.get("authority") == "Professor", "AUTHORITY_DRIFT")
    need(doc.get("sourceLaw") == "AI proposes. Policy authorizes. CI proves. Human promotes.", "APPROVAL_LAW_DRIFT")
    need(doc.get("sourceOfTruth") == "doctrine/currentSourceTruthV3.json", "SOURCE_TRUTH_POINTER_DRIFT")
    need(doc.get("namespaceCanon") == "doctrine/namingNamespaceCanonV1.json", "NAMING_POINTER_DRIFT")
    need(doc.get("compositionCanon") == "doctrine/luHmOSFourLayerArchitectureV1.json", "COMPOSITION_POINTER_DRIFT")
    need(bool(SHA40.fullmatch(doc.get("proposalBaseSourceRef", ""))), "INVALID_PROPOSAL_BASE_SHA")
    need(doc.get("referenceProposal", {}).get("prNumber") == 521
         and doc.get("referenceProposal", {}).get("status") == "OPEN_DRAFT_NOT_CANON", "DRAFT_MISREPRESENTED_AS_CANON")

    pkg = doc.get("runtimePackageSemantics", {})
    need(pkg.get("portablePluginManifest") == "plugins/luhm-os/plugin.json"
         and pkg.get("portableMcpServerConfig") == "plugins/luhm-os/mcp.json", "PLUGIN_PACKAGE_CHANGED")
    need(pkg.get("installedPrivateSiteApp") == "PRESERVE_EXISTING_SITE_BINDING", "SITE_IDENTITY_UNSAFE")
    need(pkg.get("sourcePortablePluginVersion") == "0.5.2", "PORTABLE_BASELINE_DRIFT")
    need(pkg.get("installedSiteVersionObserved") == "1.0.21", "SITE_OBSERVATION_DRIFT")
    need(pkg.get("noRemoteAssetsRequiredForFirstPaint") == "DESIGN_REQUIREMENT_NOT_MOUNT_PROOF", "OFFLINE_FALLBACK_FALSE_PROOF")
    need(pkg.get("compiledNativeClientsDoNotContainOpenAiSecrets") is True, "SECRET_BOUNDARY")
    need(pkg.get("openAiAppDoesNotGrantNativeDevicePermissions") is True, "NATIVE_PERMISSION_DRIFT")

    assets = doc.get("defaultAssets", {})
    need(assets.get("assetCount") == 110 and assets.get("integrityChecksPassed") == 557
         and assets.get("bytes") == 355761 and bool(SHA256.fullmatch(assets.get("sha256", ""))),
         "PRIVATE_STARTER_ARCHIVE_PROOF_DRIFT")
    need(assets.get("rightsStatus") == "DRAFT_NOT_PUBLIC_APPROVED"
         and assets.get("runtimeProof") == "UNVERIFIED"
         and assets.get("releaseOnlyRightsApprovedAssets") is True
         and assets.get("privateReferencesMustNotEnterPublicPackages") is True,
         "ART_RIGHTS_OR_RUNTIME_GREEN_FABRICATION")
    need(assets.get("noPrivateGoogleDriveInPublicManifest") is True, "PRIVATE_DRIVE_LEAK")
    need("fallbackCopy" in assets.get("requiredBaselineClasses", [])
         and "provenanceAndLicenseIndex" in assets.get("requiredBaselineClasses", []),
         "OFFLINE_DEFAULTS_MISSING")

    entries = doc.get("fourBuildFamilies", [])
    need(isinstance(entries, list) and len(entries) == 4, "FOUR_FAMILY_COUNT_DRIFT")
    if isinstance(entries, list):
        ids = [x.get("id") for x in entries if isinstance(x, dict)]
        need(len(ids) == 4 and set(ids) == FAMILIES and all(CANONICAL.fullmatch(x or "") for x in ids),
             "FOUR_FAMILY_IDENTITY_DRIFT")
        if set(ids) == FAMILIES:
            by_id = {x["id"]: x for x in entries}
            need("apk" in by_id["androidSamsung"].get("packageProposed", "")
                 and "aab" in by_id["androidSamsung"].get("packageStable", ""), "ANDROID_PACKAGE_DRIFT")
            need("Xcode" in by_id["iosIphone"].get("packageProposed", "")
                 and "ipa" in by_id["iosIphone"].get("packageBeta", "")
                 and "macOS Xcode" in by_id["iosIphone"].get("buildSystem", ""), "IOS_BUILD_PROOF_DRIFT")
            need("tar.gz" in by_id["linuxDesktop"].get("packageProposed", "")
                 and "aarch64" in by_id["linuxDesktop"].get("target", ""), "PI_ARM64_PACKAGING_MISSING")
            need("zip" in by_id["windowsDesktop"].get("packageProposed", "")
                 and "msix" in by_id["windowsDesktop"].get("packageStable", "")
                 and "WSL" in by_id["windowsDesktop"].get("target", ""), "WINDOWS_PACKAGE_DRIFT")
            need(all(isinstance(x.get("requiredProof"), list) and len(x["requiredProof"]) >= 5 for x in entries),
                 "DEVICE_PROOF_MISSING")
            need(all(".apk" not in by_id[x].get("packageBeta", "") for x in ("iosIphone", "linuxDesktop", "windowsDesktop")),
                 "ANDROID_APK_MASQUERADING_AS_OTHER_PLATFORM")

    roles = doc.get("serviceRoles", {})
    need(roles.get("basementUbuntu") == "PRIVATE_BUILD_AND_ASSET_STUDIO_NOT_FIFTH_PUBLIC_INSTALLER"
         and roles.get("raspberryPi") == "LINUX_ARM64_VARIANT_AND_OPTIONAL_HEADLESS_CANON_NODE"
         and roles.get("chatGptPlugin") == "SINGLE_INSTALLED_SITE_FRONT_DOOR_SEPARATE_FROM_ALL_FOUR",
         "FIVE_DEVICE_ROLE_MISUNDERSTANDING")

    lanes = doc.get("deliveryLanes", [])
    need(isinstance(lanes, list) and [x.get("id") for x in lanes] == LANES, "RELEASE_LANE_DRIFT")
    need(all(row.get("publication") is False and row.get("requiredEvidence") for row in lanes), "UNAUTHORIZED_PUBLICATION")

    update = doc.get("remoteUpdate", {})
    need(update.get("currentManifest") == remote.get("endpoint")
         and update.get("currentAssetRoute") == remote.get("assetRoute")
         and update.get("sourceModule") == remote.get("sourceModule")
         and update.get("currentPolicy") == "doctrine/selfHostedRemoteUpdatesV1.json", "UPDATE_SOURCE_DRIFT")
    need(update.get("sourceOfBuild") == "GITHUB_REVIEWED_MAIN_ONLY", "UNREVIEWED_SOURCE_UPDATE")
    need(update.get("host") == "EXISTING_RENDER_HTTPS_SAME_ORIGIN", "NEW_HOST_SURPRISE")
    need(all(update.get(key) is True for key in (
        "clientMayCheckForUpdates", "verifyHashBeforeUse", "contentAddressedCache",
        "offlineFallbackRequired", "failedUpdateRetainsLastKnownGood",
        "pluginSkillsAndMetadataRequireVersionedPackageUpdate",
        "mcpToolChangesRequireHostCompatibilityAndRefresh",
        "breakingUiChangesRequireVersionedUiResourceUri",
        "nativeBinaryReleaseRequiresPlatformSignatureAndApproval",
    )), "UPDATE_GUARDS_MISSING")
    need(all(update.get(key) is True for key in (
        "clientMayNotLoadExecutableCodeFromManifest",
        "clientMayNotFetchRawMainToExecute",
        "clientMayNotAutoInstallApkIpaLinuxOrWindowsBinaries",
    )), "REMOTE_EXECUTION_OR_INSTALL_BYPASS")
    need(remote.get("remoteScriptExecution") is False
         and remote.get("automaticApkInstall") is False
         and remote.get("runtimeCdnScripts") is False, "EXISTING_REMOTE_SOURCE_POLICY_BYPASSED")
    need(stable.get("singleInstallShell", {}).get("reinstallForPresentationChange") is False,
         "SINGLE_INSTALL_UPDATE_SPINE_DRIFT")
    need(source.get("status") == "AMBER_PROPOSED_SEAL_OF_TRUTH"
         and source.get("crownStatus") == "STOP", "GLOBAL_CANON_NOT_PROPOSED")

    boundary = doc.get("boundary", {})
    need(all(boundary.get(k) is False for k in (
        "privateSiteBackendChanged", "newRemoteRepoConnectionCreated", "privatePackRepublished",
        "buildExecuted", "liveUpdateDeployed", "productReleaseAuthority", "agentQuarantineReleased",
    )) and boundary.get("crownStatus") == "STOP", "RUNTIME_OR_CROWN_FALSE_CLAIM")
    return problems


def main() -> int:
    doc = json.loads(CONTRACT.read_text(encoding="utf-8"))
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    remote = json.loads(REMOTE.read_text(encoding="utf-8"))
    stable = json.loads(STABLE.read_text(encoding="utf-8"))
    errors = audit(doc, source, remote, stable)
    print(json.dumps({
        "schema": "luhmOs.fourTargetPluginEncapsulationAudit.v1",
        "status": "GREEN_SOURCE_ONLY" if not errors else "RED_SOURCE_CONTRACT",
        "fourPackageFamilies": 4,
        "channelCount": 5,
        "actualBuilds": 0,
        "livePluginUpdate": False,
        "crownStatus": "STOP",
        "errors": errors
    }, indent=2))
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())

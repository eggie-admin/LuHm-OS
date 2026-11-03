#!/usr/bin/env python3
"""Read-only Meta/Samsung/F-Droid separation gate for LuHm-OS proposed source.

This is a source inventory, NOT an APK SBOM, F-Droid listing, legal license
opinion, store approval, or vendor authorization. No network or file writes.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = "doctrine/metaSamsungStoreBridgeV1.json"
EXPECTED = {"org.godotengine:godot:4.7.2.stable", "androidx.webkit:webkit:1.17.1"}
PACKAGE = "art.eggiebagelface.luhmos.beta"

def audit(policy: dict, license_text: str, gradle: str, preset: str,
          fdroid_stager: str) -> list[str]:
    errors: list[str] = []
    def need(ok: bool, label: str) -> None:
        if not ok:
            errors.append(label)
    identity = policy.get("creator", {})
    p = policy.get("providerEvidence", {})
    ig = p.get("instagram", {})
    fdroid = policy.get("distribution", {}).get("fdroid", {})
    safety = policy.get("security", {})
    need(policy.get("schema") == "luhmOs.metaSamsungStoreBridge.v1", "schema")
    need(policy.get("status") == "PROPOSED_SOURCE_REVIEW_ONLY", "proposalOnly")
    need(policy.get("authority") == "Professor" and
         policy.get("crownStatus") == "STOP", "crownGate")
    need(identity.get("publisher") == "Eggie Bagelface" and
         identity.get("product") == "LuHm-OS" and
         identity.get("platformPartnerClaim") is False, "identityNoEndorsement")
    need(ig.get("accountConnection") == "CONNECTED" and
         ig.get("privateUserProfileRead") == "SUCCEEDED_2026_11_01" and
         ig.get("officialPartnership") is False and
         ig.get("metaBusinessPortfolioAdmin") == "UNKNOWN" and
         ig.get("metaBusinessVerification") == "UNKNOWN" and
         ig.get("writeExecuted") is False, "instagramEvidenceBoundary")
    need(p.get("samsung", {}).get("galaxySellerPortal") == "UNKNOWN" and
         p.get("googlePlay", {}).get("developerAccount") == "UNKNOWN",
         "storeEligibilityUnknown")
    need(fdroid.get("targetPackage") == PACKAGE and
         fdroid.get("storeCategory") == "Games", "fDroidAppIdentity")
    need(fdroid.get("licenseEvidence") == "ROOT_LICENSE_GPL_V3_TEXT_OBSERVED" and
         fdroid.get("licenseExactIdentifier") ==
         "PENDING_SOURCE_HEADER_AND_DERIVATIVE_LICENSE_REVIEW",
         "licenseNotMisrepresented")
    need(license_text.lstrip().startswith("GNU GENERAL PUBLIC LICENSE") and
         re.search(r"Version\s+3,\s+29\s+June\s+2007", license_text) is not None,
         "actualRootGpl3")
    need(fdroid.get("antiFeatureClassification") == "NOT_YET_AUDITED_ON_REAL_APK" and
         fdroid.get("publicFdroid") == "NOT_PUBLISHED", "antiFeatureUnverified")
    need(fdroid.get("currentSourceCheck", {}).get("godotExport") ==
         "permissions/internet=false" and
         "permissions/internet=false" in preset, "offlineCore")
    need("permissions/internet=true" not in preset, "noOnlineCoreOverride")
    need(fdroid.get("onlineServicePolicy") ==
         "PLAYABLE_OFFLINE_NO_REQUIRED_PROPRIETARY_BACKEND",
         "optionalBusinessService")
    direct = set(re.findall(r'\bimplementation\s*\(\s*"([^"]+)"', gradle))
    need(direct == EXPECTED and
         set(fdroid.get("currentSourceCheck", {}).get("androidPluginDeclaredDependencies", []))
         == EXPECTED, "knownDirectDependenciesOnly")
    dep_calls = re.findall(r'\b(?:implementation|api|runtimeOnly|compileOnly)\s*\(\s*([^\n)]+)', gradle)
    need(len(dep_calls) == 2 and
         all(c.lstrip().startswith('"') for c in dep_calls),
         "noOpaqueDependencyDeclarations")
    blocked = ("com.facebook.android", "com.meta.", "com.google.firebase",
               "com.google.android.gms", "com.google.android.play",
               "com.samsung.android.sdk")
    need(not any(s in gradle.lower() for s in blocked), "noProprietarySdkDeclaration")
    need(not re.search(r'\b(fileTree|files)\s*\(', gradle),
         "noUnreviewedBinaryDependency")
    need("APP=\"" + PACKAGE + "\"" in fdroid_stager, "fdroidPackageStable")
    for key in ("noBackgroundWorkers", "noPublicTokenStorage", "noMetaCredentialInApk",
                "noProprietaryTrackingInFdroid", "noPublicEndorsementClaim",
                "noFakeAntiFeatureLabels", "noAutoPost", "noAutoSubmit",
                "noAutoSign", "noAutoMerge", "noAutoDeploy"):
        need(safety.get(key) is True, "policy:" + key)
    need(safety.get("newSpendUsd") == 0, "noNewSpend")
    need(policy.get("audit", {}).get("mode") == "STATIC_SOURCE_ONLY",
         "noFalseRuntimeClaim")
    return errors


def runSourceAudit(root: Path = ROOT) -> None:
    policy = json.loads((root / CONTRACT).read_text(encoding="utf-8"))
    license_text = (root / "LICENSE").read_text(encoding="utf-8")
    gradle = (root / "androidWeb3Plugin/plugin/build.gradle.kts").read_text(encoding="utf-8")
    preset = (root / "export_presets.cfg").read_text(encoding="utf-8")
    stager = (root / "tools/prepareFdroidRepoCandidate.py").read_text(encoding="utf-8")
    errors = audit(policy, license_text, gradle, preset, stager)
    if errors:
        raise SystemExit("RED_META_SAMSUNG_SOURCE_BOUNDARY:" + ",".join(errors))
    # Required fail-closed controls: changing each class must turn GREEN into RED.
    import copy
    variants = []
    swapped = copy.deepcopy(policy)
    swapped["providerEvidence"]["instagram"]["officialPartnership"] = True
    variants.append(("fakeMetaPartner", swapped, license_text, gradle, preset, stager))
    swapped = copy.deepcopy(policy)
    swapped["distribution"]["fdroid"]["antiFeatureClassification"] = "NONE"
    variants.append(("fakeNoAntiFeatures", swapped, license_text, gradle, preset, stager))
    variants.append(("fakeApacheLicense", policy, license_text.replace(
        "GNU GENERAL PUBLIC LICENSE", "Apache License"), gradle, preset, stager))
    variants.append(("metaSdkInjected", policy, license_text,
                     gradle.replace('implementation("androidx.webkit:webkit:1.17.1")',
                         'implementation("com.facebook.android:facebook-android-sdk:18.0.0")'),
                     preset, stager))
    variants.append(("internetEnabled", policy, license_text, gradle,
                     preset.replace("permissions/internet=false", "permissions/internet=true"),
                     stager))
    variants.append(("wrongAppPackage", policy, license_text, gradle,
                     preset, stager.replace('APP="' + PACKAGE + '"',
                                           'APP="invalid.example.app"')))
    variants.append(("autoPublish", {**policy, "security": {
        **policy["security"], "noAutoPost": False}},
        license_text, gradle, preset, stager))
    for label, candidate, lic, grad, pr, stage in variants:
        if not audit(candidate, lic, grad, pr, stage):
            raise SystemExit("RED_FALSE_GREEN_NEGATIVE_CONTROL:" + label)
    print("GREEN_META_SAMSUNG_SOURCE_BOUNDARY_7_NEGATIVE_CONTROLS")
    print("SOURCE_ONLY: no real APK SBOM, transitive license proof, vendor partnership, or store acceptance")


if __name__ == "__main__":
    runSourceAudit()

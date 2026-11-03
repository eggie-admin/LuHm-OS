#!/usr/bin/env python3
"""Fail-closed source-only LuHm-OS thin-client / vendor-kernel audit.

No build, networking, firmware writes, package installation or source mutation.
Passing checks never proves a physical kernel, installed APK, runtime, or store.
"""
from __future__ import annotations

import copy
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = "doctrine/thinClientKernelBoundaryV1.json"
KOTLIN_PATH = ("androidWeb3Plugin/plugin/src/main/java/"
               "art/eggiebagelface/luhmos/web3/AndroidWeb3CockpitPlugin.kt")
EXPECTED_MODULES = [
    "kernelVendorPlatform", "linuxBuildEssentials",
    "python3ControlPlane", "godot4Game",
]
EXPECTED_COMPOSITION = [
    "coreLibrary", "pluginExtension",
    "classWidgetOrganization", "stubAdapterBoundary",
]
EXPECTED_DIRECT = {
    "org.godotengine:godot:4.7.2.stable",
    "androidx.webkit:webkit:1.17.1",
}
FORBIDDEN_APK_SERVICES = {
    "Termux", "Node.js/npm interpreter", "MariaDB server",
    "DNSmasq", "NGINX", "Blender", "full VLC desktop",
    "GParted", "Rufus",
}
ORIGIN = "https://appassets.androidplatform.net"

def audit(p: dict, modules: dict, composition: dict, vendor: dict,
          preset: str, godot: str, kotlin: str, html: str, gradle: str,
          frontend_package: dict, docker: str) -> list[str]:
    errors: list[str] = []
    def need(condition: bool, key: str) -> None:
        if not condition:
            errors.append(key)

    need(p.get("schema") == "luhmOs.thinClientKernelBoundary.v1" and
         p.get("status") == "PROPOSED_SOURCE_ONLY" and
         p.get("authority") == "Professor" and p.get("crownStatus") == "STOP",
         "canonState")
    layers = p.get("stack", {})
    kernel = layers.get("kernel", {})
    hardware = layers.get("hardwareFirmware", {})
    os_layer = layers.get("operatingSystem", {})
    client = layers.get("client", {})
    optional = layers.get("remoteOptional", {})
    need(hardware.get("policy") == "INHERIT_PLATFORM_UNMODIFIED" and
         hardware.get("firmwareFlash") is False and
         hardware.get("biosOrBootloaderWrites") is False and
         hardware.get("chipsetDriverChanges") is False,
         "firmwareInherited")
    need(kernel.get("android") == "INHERIT_VENDOR_ANDROID_GKI_KMI_DO_NOT_REPLACE" and
         kernel.get("linuxHost") == "INHERIT_HOST_KERNEL_NO_CUSTOM_KERNEL" and
         kernel.get("kernelModuleChanges") is False and
         kernel.get("kernelPatches") is False and
         kernel.get("actualKernelBuildOrIntegrityProof") == "NOT_PROVEN",
         "kernelNotModifiedOrFaked")
    need(os_layer.get("unrooted") is True and
         os_layer.get("runtime") == "Android System WebView plus Godot native runtime",
         "androidInheritsPlatform")
    source_modules = modules.get("sourceModules", [])
    need([x.get("id") for x in source_modules] == EXPECTED_MODULES and
         p.get("moduleBoundary", {}).get("kernelBase") == EXPECTED_MODULES[0],
         "fourSourceModules")
    first = source_modules[0] if source_modules else {}
    need(first.get("canonicalChangePolicy") == "securityUpdatesOnly" and
         {"AndroidGkiKmi", "SamsungVendorModules", "upstreamAbiContracts"}
         <= set(first.get("preserve", [])),
         "vendorAbiPreserved")
    need([x.get("id") for x in composition.get("layers", [])] ==
         EXPECTED_COMPOSITION and p.get("composition") == EXPECTED_COMPOSITION,
         "fourCompositionLayers")
    matrix = p.get("matrix4x4", [])
    hexes = [cell.get("hex") for row in matrix for cell in row.get("checks", [])]
    need(len(matrix) == 4 and all(len(row.get("checks", [])) == 4 for row in matrix)
         and hexes == [f"0x{i:02X}" for i in range(16)],
         "logicalHexMatrix")
    need(client.get("networkPermission") is False and
         client.get("arm64") is True and client.get("androidSdkTarget") == 36,
         "minimalAndroidTarget")
    need('permissions/internet=false' in preset and
         'permissions/internet=true' not in preset,
         "offlinePermission")
    for arch, flag in [("arm64-v8a", "true"), ("armeabi-v7a", "false"),
                       ("x86", "false"), ("x86_64", "false")]:
        need(f"architectures/{arch}={flag}" in preset, "arch:" + arch)
    need('gradle_build/target_sdk="36"' in preset and
         'gradle_build/min_sdk="24"' in preset and
         'package/unique_name="art.eggiebagelface.luhmos.testing"' in preset and
         client.get("betaPackage") == "art.eggiebagelface.luhmos.beta",
         "androidPackageSdkAndBetaIsolation")
    need('run/main_scene="res://scenes/Main.tscn"' in godot and
         'renderer/rendering_method="gl_compatibility"' in godot and
         'renderer/rendering_method.mobile="gl_compatibility"' in godot and
         client.get("godotRenderer") == "gl_compatibility",
         "godotSceneAndMobileRenderer")
    need(ORIGIN in kotlin and
         client.get("webviewOrigin") == ORIGIN and
         "WebViewAssetLoader.Builder()" in kotlin and
         'private const val LOCAL_PREFIX = "/assets/"' in kotlin and
         "setOf(LOCAL_ORIGIN)" in kotlin and
         "WebViewCompat.addWebMessageListener" in kotlin and
         "shouldInterceptRequest" in kotlin and
         "return blockedResponse()" in kotlin,
         "localWebviewOnly")
    need("addJavascriptInterface(" not in kotlin and
         "allowFileAccess = false" in kotlin and
         "allowContentAccess = false" in kotlin and
         "domStorageEnabled = false" in kotlin and
         "databaseEnabled = false" in kotlin and
         "MIXED_CONTENT_NEVER_ALLOW" in kotlin and
         "bridge_keys_rejected" in kotlin,
         "noPrivilegedJavascriptOrPersistence")
    script_src = re.findall(r"<script\b[^>]*\bsrc\s*=\s*['\"]([^'\"]+)", html, re.I)
    style_src = re.findall(r"<link\b[^>]*\bhref\s*=\s*['\"]([^'\"]+)", html, re.I)
    need(bool(script_src) and bool(style_src) and
         all(x.startswith("./") for x in script_src + style_src) and
         "./vendor/jquery-3.7.1.min.js" in script_src and
         'data-luhm-cockpit' in html,
         "localUiOnly")
    allowed = client.get("assetAllowlist", [])
    referenced = {"index.html", "vendor/jquery-LICENSE.txt"} | {
        x[2:] for x in (script_src + style_src)
    }
    need(len(allowed) == 9 and set(allowed) == referenced and
         client.get("androidBundle") == "EXPLICIT_ALLOWLIST_GENERATED_SYNC_ONLY" and
         client.get("javascriptSource") ==
         "LOCAL_PINNED_JQUERY_COPIED_FROM_NPM_LOCK_BEFORE_BUILD",
         "smallExplicitAssetInventory")
    declared = re.search(r"val cockpitAssetPaths\s*=\s*listOf\((.*?)\n\)", gradle, re.S)
    actual_paths = re.findall(r'"([^"]+)"', declared.group(1)) if declared else []
    need(actual_paths == allowed and
         'assets.srcDir(cockpitAssetsDirectory)' in gradle and
         'assets.srcDir("../../frontEnd")' not in gradle and
         'include(*cockpitAssetPaths.toTypedArray())' in gradle and
         "tasks.registering(Sync::class)" in gradle and
         "dependsOn(stageCockpitAssets)" in gradle and
         "RED_COCKPIT_ASSETS" in gradle,
         "onlyCuratedAssetsInAar")
    need(frontend_package.get("private") is True and
         frontend_package.get("dependencies") == {"jquery": "3.7.1"} and
         client.get("uiLibraryPinned") == "3.7.1",
         "minimalJqueryDependency")
    direct = set(re.findall(r'\bimplementation\s*\(\s*"([^"]+)"', gradle))
    need(direct == EXPECTED_DIRECT and
         len(re.findall(r'\b(?:api|implementation|runtimeOnly|compileOnly)\s*\(', gradle)) == 2 and
         'assets.srcDir(cockpitAssetsDirectory)' in gradle and
         'assets.srcDir("../../frontEnd")' not in gradle,
         "thinAndroidDependencies")
    android = vendor.get("architectureProfiles", {}).get("samsungClient", {})
    linux = vendor.get("architectureProfiles", {}).get("linuxHeadless", {})
    heavy = vendor.get("architectureProfiles", {}).get("linuxStudio", {})
    need(FORBIDDEN_APK_SERVICES <= set(android.get("forbiddenRuntimeRequirements", [])),
         "noStudioServerOnTablet")
    need("Python3 standard library including sqlite3" in linux.get("minimum", []) and
         linux.get("notASecondKernel") is True and
         "Godot4" in heavy.get("mayUse", []) and
         "ffmpeg" in docker.lower() and
         "blender" in docker.lower() and
         "/usr/sbin/policy-rc.d" in docker and
         'CMD ["sleep", "infinity"]' in docker,
         "headlessAndStudioProfilesSeparate")
    need(optional.get("startAutomatically") is False and
         optional.get("studio") == ".devcontainer/Dockerfile" and
         "Meta" not in str(optional.get("heavyTools", [])),
         "optionalStudioNotCore")
    safety = p.get("security", {})
    for k in ("noRoot", "noFirmwareFlash", "noKernelFork",
              "noInternetRequired", "noMetaOrGoogleSdkRequired",
              "noSecretInClient", "noAutomaticProviderSpend", "noAutoMerge",
              "noAutoSign", "noAutoDeploy", "noAutoPublish",
              "workersQuarantined"):
        need(safety.get(k) is True, "security:" + k)
    release = p.get("release", {})
    need(all(release.get(k) is False for k in (
             "apkBuiltAtThisRef", "physicalSamsungInstalled", "stableSignerVerified",
             "publicBeta")) and release.get("crownStatus") == "STOP",
         "noFalseReleaseProof")
    need(p.get("proof", {}).get("mode") == "STATIC_SOURCE_ONLY" and
         p.get("proof", {}).get("negativeControls") == 12,
         "honestSourceOnlyClaim")
    return errors


def runSourceAudit(root: Path = ROOT) -> None:
    def load(path: str) -> dict:
        return json.loads((root / path).read_text(encoding="utf-8"))
    def read(path: str) -> str:
        return (root / path).read_text(encoding="utf-8")

    p = load(POLICY_PATH)
    modules = load("doctrine/modularSourceArchitectureV1.json")
    composition = load("doctrine/luHmOSFourLayerArchitectureV1.json")
    vendor = load("doctrine/vendorReductionV1.json")
    preset = read("export_presets.cfg")
    godot = read("project.godot")
    kotlin = read(KOTLIN_PATH)
    html = read("frontEnd/index.html")
    gradle = read("androidWeb3Plugin/plugin/build.gradle.kts")
    frontend_package = load("frontEnd/package.json")
    docker = read(".devcontainer/Dockerfile")
    base = (p, modules, composition, vendor, preset, godot,
            kotlin, html, gradle, frontend_package, docker)
    errors = audit(*base)
    # The signed and testing workflows both need lock-pinned local jquery
    # before the AAR asset-merge. Source checks cannot prove a compiled bundle.
    for workflow_path in (
        ".github/workflows/samsung-lite-signed-beta.yml",
        ".github/workflows/android-testing-build.yml",
    ):
        workflow = read(workflow_path)
        start = workflow.find("- name: Stage allowlisted offline cockpit assets")
        build = workflow.find("- name: Build Android Web3 cockpit plugin")
        if not (0 <= start < build and
                "npm ci --ignore-scripts --no-audit --no-fund" in workflow[start:build] and
                "npm run stage:jquery" in workflow[start:build] and
                "test -s vendor/jquery-LICENSE.txt" in workflow[start:build]):
            errors.append("missingPinnedJqueryPrestage:" + workflow_path)
    if errors:
        raise SystemExit("RED_THIN_CLIENT_CANON:" + ",".join(errors))
    negatives = []
    variant = copy.deepcopy(p)
    variant["stack"]["kernel"]["kernelPatches"] = True
    negatives.append(("kernelPatch", (variant, *base[1:])))
    negatives.append(("internetEnabled", (p, modules, composition, vendor,
        preset.replace("permissions/internet=false", "permissions/internet=true"),
        *base[5:])))
    negatives.append(("arm64Disabled", (p, modules, composition, vendor,
        preset.replace("architectures/arm64-v8a=true", "architectures/arm64-v8a=false"),
        *base[5:])))
    negatives.append(("remoteScript", (p, modules, composition, vendor, preset,
        godot, kotlin, html + '<script src="https://example.com/a.js"></script>',
        gradle, frontend_package, docker)))
    negatives.append(("nativeJavascriptInterface", (p, modules, composition,
        vendor, preset, godot, kotlin + "\naddJavascriptInterface(any);",
        html, gradle, frontend_package, docker)))
    negatives.append(("proprietarySdk", (p, modules, composition, vendor, preset,
        godot, kotlin, html,
        gradle + '\nimplementation("com.facebook.android:facebook-android-sdk:18.0.0")',
        frontend_package, docker)))
    other = copy.deepcopy(frontend_package)
    other["dependencies"]["react"] = "19.0.0"
    negatives.append(("heavyUiDependency", (*base[:9], other, docker)))
    negatives.append(("mobileRenderer", (p, modules, composition, vendor, preset,
        godot.replace('renderer/rendering_method.mobile="gl_compatibility"',
                      'renderer/rendering_method.mobile="gl_mobile"'),
        kotlin, html, gradle, frontend_package, docker)))
    variant = copy.deepcopy(p)
    variant["security"]["noAutoDeploy"] = False
    negatives.append(("autoDeployment", (variant, *base[1:])))
    changed = copy.deepcopy(modules)
    changed["sourceModules"][0]["preserve"] = []
    negatives.append(("lostKernelAbi", (p, changed, *base[2:])))
    negatives.append(("broadAssetDirectory", (p, modules, composition,
        vendor, preset, godot, kotlin, html,
        gradle + '\nassets.srcDir("../../frontEnd")',
        frontend_package, docker)))
    negatives.append(("unreviewedPrototypeAsset", (p, modules, composition,
        vendor, preset, godot, kotlin, html,
        gradle.replace('"jquery/luhm.cast.js",',
                       '"jquery/luhm.cast.js",\n    "prototypes/glassWorld/index.html",'),
        frontend_package, docker)))
    assert len(negatives) == 12
    for label, args in negatives:
        if not audit(*args):
            raise SystemExit("RED_FALSE_GREEN:" + label)
    print("GREEN_THIN_CLIENT_CANON_SOURCE_12_NEGATIVE_CONTROLS")
    print("SOURCE_ONLY: kernel binary, firmware, real device and APK contents NOT VERIFIED")


if __name__ == "__main__":
    runSourceAudit()

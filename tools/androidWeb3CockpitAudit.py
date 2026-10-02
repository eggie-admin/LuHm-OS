#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []
warnings: list[str] = []

def require(ok: bool, message: str) -> None:
    if not ok:
        errors.append(message)

def read(rel: str) -> str:
    path = ROOT / rel
    require(path.is_file(), f"missing required file: {rel}")
    return path.read_text(encoding="utf-8") if path.is_file() else ""

def load_json(rel: str) -> dict:
    text = read(rel)
    if not text:
        return {}
    try:
        return json.loads(text)
    except Exception as exc:
        errors.append(f"invalid JSON {rel}: {exc}")
        return {}

contract = load_json("doctrine/ANDROID_WEB3_COCKPIT_SWITCH_V1.json")
bridge = load_json("doctrine/ANDROID_WEB3_BRIDGE_V1.json")
source = load_json("doctrine/SOURCE_OF_TRUTH.json")

html = read("frontEnd/index.html")
app = read("frontEnd/app.js")
front_readme = read("frontEnd/README.md")
back_readme = read("backEndGui/README.md")
kotlin = read("androidWeb3Plugin/plugin/src/main/java/art/eggiebagelface/luhmos/web3/AndroidWeb3CockpitPlugin.kt")
gradle_root = read("androidWeb3Plugin/build.gradle.kts")
gradle_plugin = read("androidWeb3Plugin/plugin/build.gradle.kts")
manifest = read("androidWeb3Plugin/plugin/src/main/AndroidManifest.xml")
export_plugin = read("addons/AndroidWeb3Cockpit/export_plugin.gd")
plugin_cfg = read("addons/AndroidWeb3Cockpit/plugin.cfg")
project = read("project.godot")
preset = read("export_presets.cfg")
godot_main = read("scripts/main.gd")
lum_avatar = read("scripts/game/lumAvatar.gd")
lum_rig_smoke = read("tests/lumRigV2Phase1Smoke.gd")
android_workflow = read(".github/workflows/android-testing-build.yml")
godot_workflow = read(".github/workflows/godot-web-harness.yml")
rig_workflow = read(".github/workflows/lumrigv2-phase1.yml")
cast_gate = read("tools/forgeCastGate.py")
forge = load_json("doctrine/FORGE_TWINS_V3.json")

# Milestone and authority.
require(contract.get("status") == "AMBER_ANDROID_WEB3_COCKPIT_SOURCE_READY_CAST_BUILD_PENDING",
        "milestone must remain source-ready / CAST-build-pending")
require(contract.get("authority") == "Professor", "Professor authority drift")
require(contract.get("crownStatus") == "STOP", "Crown must remain STOP")
require(contract.get("promotion") is False, "promotion must remain false")
require(contract.get("targetArchitecture", {}).get("userFacingCockpit") ==
        "Android System WebView hosting packaged LuHm frontEnd/", "WebView target drift")
require(contract.get("targetArchitecture", {}).get("frontendPrivilege") is False,
        "front end may not become privileged")
require(contract.get("targetArchitecture", {}).get("shellAuthority") is False,
        "shell authority forbidden")
require(contract.get("currentEvidence", {}).get("wrapperSource") ==
        "IMPLEMENTED_STATIC_CANDIDATE", "wrapper source state drift")
require(contract.get("currentEvidence", {}).get("wrapperAar") == "PENDING_CAST_BUILD",
        "AAR must remain pending until CAST build")
require(contract.get("currentEvidence", {}).get("apkIntegration") == "PENDING_CAST_BUILD",
        "APK integration must remain pending until CAST build")
require(contract.get("currentEvidence", {}).get("physicalSamsungWebViewProof") == "PENDING",
        "must not fake Samsung WebView proof")

aw3 = source.get("androidWeb3Cockpit", {})
require(source.get("milestone", "").startswith("Android Web3 Cockpit"),
        "SOURCE_OF_TRUTH active milestone did not switch")
require(aw3.get("contract") == "doctrine/ANDROID_WEB3_COCKPIT_SWITCH_V1.json",
        "SOURCE_OF_TRUTH missing Web3 contract")
require(aw3.get("runtime") == "Android System WebView", "runtime must be Android System WebView")
require(aw3.get("webViewWrapper") == "SOURCE_IMPLEMENTED_BUILD_PENDING",
        "source truth wrapper state drift")
require(aw3.get("pluginAar") == "PENDING_CAST_BUILD", "source truth AAR gate drift")
require(aw3.get("physicalSamsungProof") == "PENDING", "physical proof must remain pending")
require(aw3.get("crownStatus") == "STOP", "source truth Crown must remain STOP")
require(source.get("cockpitSwitch", {}).get("historicalOnly") is True,
        "prior native cockpit receipt must remain historical evidence")

# Browser surface.
require("jquery-3.7.1.min.js" in html, "pinned local jQuery missing")
require("http://" not in html and "https://" not in html,
        "front-end HTML must not load remote runtime content")
for primitive in ("fetch(", "XMLHttpRequest", "WebSocket(", "eval(", "new Function("):
    require(primitive not in html and primitive not in app,
            f"forbidden web runtime primitive present: {primitive}")
require('window.LuHmNative' in app and '.postMessage' in app,
        "origin-scoped native message surface not wired from front end")
require('postNative("world_requested")' in app, "world request bridge missing")
require('postNative("cockpit_ready")' in app, "cockpit ready bridge missing")
require("luhm:backend:open" in app, "typed Godot/system boundary event missing")
require("Android Web3 cockpit" in html, "candidate cockpit identity missing from HTML")
require("Android System WebView" in front_readme, "front-end runtime target not documented")
require("shell execution" in back_readme.lower(), "Godot boundary must document shell prohibition")

# Native wrapper source.
for token in (
    "class AndroidWeb3CockpitPlugin",
    "WebViewAssetLoader.Builder()",
    "WebViewAssetLoader.AssetsPathHandler",
    'LOCAL_ORIGIN = "https://appassets.androidplatform.net"',
    'LOCAL_PREFIX = "/assets/"',
    "WebViewCompat.addWebMessageListener",
    "WebViewFeature.WEB_MESSAGE_LISTENER",
    "isMainFrame",
    "sourceOrigin.toString() != LOCAL_ORIGIN",
    "allowFileAccess = false",
    "allowContentAccess = false",
    "WebSettings.MIXED_CONTENT_NEVER_ALLOW",
    "assetLoader.shouldInterceptRequest(request.url) ?: blockedResponse()",
    "getCurrentWebViewPackage",
    '"world_requested"',
    '"cockpit_ready"',
    "@UsedByGodot",
):
    require(token in kotlin, f"Android wrapper missing control: {token}")
require("addJavascriptInterface" not in kotlin, "addJavascriptInterface is forbidden")
require("loadUrl(START_URL)" in kotlin, "wrapper must load only the packaged start URL")
require('return !allowed' in kotlin, "navigation must fail closed outside the local origin")
require('403' in kotlin and '"Blocked"' in kotlin, "blocked network response missing")

# Plugin build and v2 registration.
require('id("com.android.library") version "8.13.2" apply false' in gradle_root,
        "Android Gradle Plugin pin drift")
require('id("org.jetbrains.kotlin.android") version "2.2.21" apply false' in gradle_root,
        "Kotlin plugin pin drift")
require("compileSdk = 36" in gradle_plugin, "compileSdk drift")
require("minSdk = 24" in gradle_plugin, "minSdk drift")
require('implementation("org.godotengine:godot:4.7.2.stable")' in gradle_plugin,
        "Godot Android library pin drift")
require('implementation("androidx.webkit:webkit:1.17.1")' in gradle_plugin,
        "AndroidX WebKit pin drift")
require('assets.srcDir("../../frontEnd")' in gradle_plugin,
        "frontEnd assets are not packaged into plugin")
require("org.godotengine.plugin.v2." in manifest, "Godot v2 plugin metadata missing")
require("AndroidWeb3CockpitPlugin" in manifest, "plugin init class missing from manifest")
require("android.permission.INTERNET" not in manifest, "plugin manifest must not add INTERNET")
require('name="AndroidWeb3Cockpit"' in plugin_cfg, "Godot plugin.cfg identity drift")
require("AndroidWeb3Cockpit-debug.aar" in export_plugin, "debug AAR export path missing")
require("AndroidWeb3Cockpit-release.aar" in export_plugin, "release AAR export path missing")
require("androidx.webkit:webkit:1.17.1" in export_plugin, "WebKit export dependency missing")
require('enabled=PackedStringArray("res://addons/AndroidWeb3Cockpit/plugin.cfg")' in project,
        "Android Web3 export addon is not enabled")
require("permissions/internet=false" in preset, "Android export must remain no-INTERNET")

# Godot/native typed handoff.
for token in (
    'Engine.has_singleton("AndroidWeb3Cockpit")',
    'Engine.get_singleton("AndroidWeb3Cockpit")',
    'connect("world_requested", enterWorldMode)',
    'connect("cockpit_ready", _on_android_web3_ready)',
    'connect("bridge_error", _on_android_web3_error)',
    "android_web3_plugin.hideCockpit()",
    "android_web3_plugin.showCockpit()",
):
    require(token in godot_main, f"Godot bridge missing: {token}")

# Known pre-build rig blocker must be source-fixed before CAST.
require("look_target.top_level = true" in lum_avatar,
        "Lum look target must remain independent of parent bobbing")
require('initial_marker.top_level' in lum_rig_smoke,
        "Lum rig smoke must regression-check world-space look target")

# Bridge doctrine remains minimal.
require(bridge.get("localOrigin") == "https://appassets.androidplatform.net",
        "bridge local origin drift")
security = bridge.get("security", {})
for key in ("allowedMainFrameOnly", "exactOriginOnly"):
    require(security.get(key) is True, f"bridge security {key} must be true")
for key in ("arbitraryNavigation", "networkFallback", "addJavascriptInterface",
            "fileScheme", "contentScheme", "mixedContent", "arbitraryCommands",
            "shellAuthority", "crownAuthority"):
    require(security.get(key) is False, f"bridge security {key} must remain false")
allowed_js = [x.get("type") for x in bridge.get("javascriptToNative", [])]
require(allowed_js == ["cockpit_ready", "world_requested"],
        "JavaScript-to-native bridge types expanded unexpectedly")

# Forge CAST gating: build-producing workflows must be manual only.
require(forge.get("operationLaw") == "PROTECT != INGEST != MUTATE != CAST != JANITOR",
        "Forge operation law drift")
require('FORGE_CAST_GATE=DENIED' in cast_gate, "CAST gate must fail closed")
for rel, text in (
    ("android-testing-build.yml", android_workflow),
    ("godot-web-harness.yml", godot_workflow),
    ("lumrigv2-phase1.yml", rig_workflow),
):
    require("workflow_dispatch:" in text, f"{rel} must be manual workflow_dispatch")
    require("pull_request:" not in text, f"{rel} must not auto-build on pull_request")
    require(re.search(r"(?m)^\s*push:\s*$", text) is None, f"{rel} must not auto-build on push")
    require("forgeCastGate.py" in text, f"{rel} must invoke Forge CAST gate")
    require("${{ inputs.cast }}" in text, f"{rel} must bind explicit CAST input")
    require("${{ inputs.sourceRef }}" in text, f"{rel} must bind exact sourceRef")

require("Build Android Web3 cockpit plugin from exact CAST source" in android_workflow,
        "CAST Android workflow must build the Web3 AAR before Godot export")
require("gradle-8.13-bin.zip" in android_workflow, "pinned Gradle build tool missing")
require("20f1b1176237254a6fc204d8434196fa11a4cfb387567519c61556e8710aed78" in android_workflow,
        "Gradle distribution SHA-256 pin missing")
require(":plugin:assemble" in android_workflow, "Web3 plugin assemble step missing")

status = "GREEN_STATIC_ANDROID_WEB3_COCKPIT_SOURCE_READY" if not errors else "RED_ANDROID_WEB3_COCKPIT_SOURCE"
print(json.dumps({
    "schema": "luhm-os.android-web3-cockpit-static-audit.v2",
    "status": status,
    "errors": errors,
    "warnings": warnings,
    "wrapperSource": "IMPLEMENTED_STATIC_CANDIDATE",
    "aarBuild": "PENDING_CAST",
    "apkIntegration": "PENDING_CAST",
    "physicalSamsungProof": "PENDING",
    "installedWebViewVersion": "UNKNOWN_UNTIL_DEVICE",
    "crownStatus": "STOP"
}, indent=2))
sys.exit(0 if not errors else 2)

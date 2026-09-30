#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

def read(path):
    return (ROOT / path).read_text(encoding="utf-8")

def require(cond, label):
    if not cond:
        raise SystemExit(f"RED: {label}")
    print(f"GREEN: {label}")

doctrine = json.loads(read("doctrine/cathedralWebglassFinal-20260926.json"))
atelier = json.loads(read("doctrine/oniAtelierBodyForge-20260926.json"))
ritual = json.loads(read("doctrine/witchingHourThreeRitual-20260926.json"))
runtime_doctrine = json.loads(read("doctrine/runtimeDoctrine-20260926.json"))
require(doctrine["authority"] == "Professor", "Crown authority remains human")
require(atelier["authority"] == "Professor", "Oni Atelier remains Crown-gated")
require(ritual["authority"]["crown"] == "Professor", "Witching Hour remains Crown-gated")
require(runtime_doctrine["authority"]["crown"] == "Professor", "runtime doctrine remains Crown-gated")
require(doctrine["runtime"]["world_owner"].startswith("Godot 4"), "Godot owns world")
require(doctrine["runtime"]["ui_owner"].startswith("caged local Android WebView"), "WebView owns glass only")
require(atelier["runtime"]["mutationMode"] == "runtime_non_destructive", "BodyForge is non-destructive")
require(len(ritual["rituals"]) == 3, "exactly three bounded rituals")

world = read("scripts/game/neonWorld.gd")
require("LumPlinth" not in world, "literal Lum performance plinth removed")
require("_build_lum_resident" in world, "Lum is a world resident")

modifier = read("scripts/game/bodyProportionModifier.gd")
require("extends SkeletonModifier3D" in modifier, "Godot SkeletonModifier3D owns proportion pass")
require("set_bone_pose_scale" in modifier, "proportion pass uses bounded pose scaling")
require("set_bone_rest" not in modifier, "creator does not rewrite donor rest pose")

creator = read("scripts/game/bodyForgeController.gd") + read("scripts/game/characterCreatorRuntime.gd")
for token in ["height", "head", "shoulders", "torso", "arms", "legs", "hips", "frame"]:
    require(token in creator, f"BodyForge slider present: {token}")

ritual_runtime = read("scripts/game/ritualDirector.gd")
for ritual_id in ["crown_wake", "oni_trinity", "witching_hour"]:
    require(ritual_id in ritual_runtime, f"ritual runtime allowlist contains {ritual_id}")
for forbidden in ["FileAccess", "DirAccess", "HTTPRequest", "OS.execute", "shell", "su ", "setenforce"]:
    require(forbidden not in ritual_runtime, f"ritual runtime excludes capability: {forbidden}")

kotlin = read("native/kaiwebview/kaiwebview/src/main/java/art/eggiebagelface/luhmos/kaiwebview/KAIWebView.kt")
require("WebViewAssetLoader" in kotlin, "packaged asset origin loader")
require("WEB_MESSAGE_LISTENER" in kotlin, "origin-scoped message listener")
require("blockNetworkLoads = true" in kotlin, "WebView network loads blocked")
require("setAcceptCookie(false)" in kotlin, "cookies disabled")
for typed in ["avatar.tune", "avatar.reset", "avatar.inspect", "ritual.start"]:
    require(typed in kotlin, f"native bridge forwards typed event: {typed}")
for forbidden in ["addJavascriptInterface", "MIXED_CONTENT_ALWAYS_ALLOW", "allowUniversalAccessFromFileURLs", "allowFileAccessFromFileURLs"]:
    require(forbidden not in kotlin, f"forbidden WebView primitive absent: {forbidden}")

bridge = read("scripts/platform/kaiWebViewBridge.gd")
for typed in ["input.axis", "camera.delta", "window.mode", "app.quit", "avatar.tune", "avatar.reset", "avatar.inspect", "ritual.start"]:
    require(typed in bridge, f"typed bridge message present: {typed}")
for forbidden in ["shell", "exec(", "system(", "su ", "setenforce"]:
    require(forbidden not in bridge.lower(), f"no privileged/generic executor token: {forbidden}")

html = read("cockpit/index.html")
for asset in ["vendor/jquery/jquery.min.js", "vendor/jquery-ui/jquery-ui.min.js", "vendor/bootstrap/bootstrap.bundle.min.js", "vendor/vue/vue.global.prod.js", "jquery/luhm.atelier.js", "jquery/luhm.ritual.js", "ritual.css"]:
    require(asset in html, f"local packaged UI dependency referenced: {asset}")
require("connect-src 'none'" in html, "CSP blocks web network connections")
require("Oni Atelier // BodyForge" in html, "character creator panel packaged")
require("Witching Hour // Three Rituals" in html, "three-ritual panel packaged")

css = read("cockpit/styles.css")
for mode in ["bubble", "compact", "panel", "fullscreen"]:
    require(f'data-mode="{mode}"' in css, f"CSS window mode defined: {mode}")
require(".atelierSlider" in css, "BodyForge slider skin packaged")
require(".ritualGrid" in read("cockpit/ritual.css"), "ritual skin packaged")

deck = read("cockpit/jquery/luhm.deck.js")
for msg in ["input.axis", "camera.delta", "window.mode", "app.background", "app.quit", "avatar.tune", "avatar.reset", "avatar.inspect", "ritual.start"]:
    require(msg in deck, f"jQuery deck routes typed action: {msg}")

build = runtime_doctrine["build"]
export = read("export_presets.cfg")
require("permissions/internet=false" in export, "APK internet permission disabled")
require(f'package/unique_name="{build["package"]}"' in export, "runtime-doctrine package identity")
require(f'version/code={build["version_code"]}' in export, "runtime-doctrine version code")
require(f'version/name="{build["version_name"]}"' in export, "runtime-doctrine version name")

print("CATHEDRAL_FULL_MUTATION_10_PASS=GREEN")

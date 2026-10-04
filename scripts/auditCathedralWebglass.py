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
require(doctrine["authority"] == "Professor", "Crown authority remains human")
require(atelier["authority"] == "Professor", "Oni Atelier remains Crown-gated")
require(doctrine["runtime"]["world_owner"].startswith("Godot 4"), "Godot owns world")
require(doctrine["runtime"]["ui_owner"].startswith("caged local Android WebView"), "WebView owns glass only")
require(atelier["runtime"]["mutationMode"] == "runtime_non_destructive", "BodyForge is non-destructive")

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

kotlin = read("native/kaiwebview/kaiwebview/src/main/java/art/eggiebagelface/luhmos/kaiwebview/KAIWebView.kt")
require("WebViewAssetLoader" in kotlin, "packaged asset origin loader")
require("WEB_MESSAGE_LISTENER" in kotlin, "origin-scoped message listener")
require("blockNetworkLoads = true" in kotlin, "WebView network loads blocked")
require("setAcceptCookie(false)" in kotlin, "cookies disabled")
for typed in ["avatar.tune", "avatar.reset", "avatar.inspect"]:
    require(typed in kotlin, f"native bridge forwards typed creator event: {typed}")
for forbidden in ["addJavascriptInterface", "MIXED_CONTENT_ALWAYS_ALLOW", "allowUniversalAccessFromFileURLs", "allowFileAccessFromFileURLs"]:
    require(forbidden not in kotlin, f"forbidden WebView primitive absent: {forbidden}")

bridge = read("scripts/platform/kaiWebViewBridge.gd")
for typed in ["input.axis", "camera.delta", "window.mode", "app.quit", "avatar.tune", "avatar.reset", "avatar.inspect"]:
    require(typed in bridge, f"typed bridge message present: {typed}")
for forbidden in ["shell", "exec(", "system(", "su ", "setenforce"]:
    require(forbidden not in bridge.lower(), f"no privileged/generic executor token: {forbidden}")

html = read("cockpit/index.html")
for asset in ["vendor/jquery/jquery.min.js", "vendor/jquery-ui/jquery-ui.min.js", "vendor/bootstrap/bootstrap.bundle.min.js", "vendor/vue/vue.global.prod.js", "jquery/luhm.atelier.js"]:
    require(asset in html, f"local packaged UI dependency referenced: {asset}")
require("connect-src 'none'" in html, "CSP blocks web network connections")
require("Oni Atelier // BodyForge" in html, "character creator panel packaged")

css = read("cockpit/styles.css")
for mode in ["bubble", "compact", "panel", "fullscreen"]:
    require(f'data-mode="{mode}"' in css, f"CSS window mode defined: {mode}")
require(".atelierSlider" in css, "BodyForge slider skin packaged")

deck = read("cockpit/jquery/luhm.deck.js")
for msg in ["input.axis", "camera.delta", "window.mode", "app.background", "app.quit", "avatar.tune", "avatar.reset", "avatar.inspect"]:
    require(msg in deck, f"jQuery deck routes typed action: {msg}")

export = read("export_presets.cfg")
require('permissions/internet=false' in export, "APK internet permission disabled")
require('art.eggiebagelface.luhmos.cathedraltoy.atelier' in export, "side-by-side Oni Atelier package identity")
require('version/code=125' in export, "Oni Atelier version code")

print("CATHEDRAL_ONI_ATELIER_10_PASS=GREEN")

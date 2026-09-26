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
require(doctrine["authority"] == "Professor", "Crown authority remains human")
require(doctrine["runtime"]["world_owner"].startswith("Godot 4"), "Godot owns world")
require(doctrine["runtime"]["ui_owner"].startswith("caged local Android WebView"), "WebView owns glass only")

world = read("scripts/game/neonWorld.gd")
require("LumPlinth" not in world, "literal Lum performance plinth removed")
require("_build_lum_resident" in world, "Lum is a world resident")

kotlin = read("native/kaiwebview/kaiwebview/src/main/java/art/eggiebagelface/luhmos/kaiwebview/KAIWebView.kt")
require("WebViewAssetLoader" in kotlin, "packaged asset origin loader")
require("WEB_MESSAGE_LISTENER" in kotlin, "origin-scoped message listener")
require("blockNetworkLoads = true" in kotlin, "WebView network loads blocked")
require("setAcceptCookie(false)" in kotlin, "cookies disabled")
for forbidden in ["addJavascriptInterface", "MIXED_CONTENT_ALWAYS_ALLOW", "allowUniversalAccessFromFileURLs", "allowFileAccessFromFileURLs"]:
    require(forbidden not in kotlin, f"forbidden WebView primitive absent: {forbidden}")

bridge = read("scripts/platform/kaiWebViewBridge.gd")
for typed in ["input.axis", "camera.delta", "window.mode", "app.quit"]:
    require(typed in bridge, f"typed bridge message present: {typed}")
for forbidden in ["shell", "exec(", "system(", "su ", "setenforce"]:
    require(forbidden not in bridge.lower(), f"no privileged/generic executor token: {forbidden}")

html = read("cockpit/index.html")
for asset in ["vendor/jquery/jquery.min.js", "vendor/jquery-ui/jquery-ui.min.js", "vendor/bootstrap/bootstrap.bundle.min.js", "vendor/vue/vue.global.prod.js"]:
    require(asset in html, f"local packaged UI dependency referenced: {asset}")
require("connect-src 'none'" in html, "CSP blocks web network connections")

css = read("cockpit/styles.css")
for mode in ["bubble", "compact", "panel", "fullscreen"]:
    require(f'data-mode=\"{mode}\"' in css, f"CSS window mode defined: {mode}")

deck = read("cockpit/jquery/luhm.deck.js")
for msg in ["input.axis", "camera.delta", "window.mode", "app.background", "app.quit"]:
    require(msg in deck, f"jQuery deck routes typed action: {msg}")

export = read("export_presets.cfg")
require('permissions/internet=false' in export, "APK internet permission disabled")
require('art.eggiebagelface.luhmos.cathedraltoy.webglass' in export, "side-by-side WebGlass package identity")

print("CATHEDRAL_WEBGLASS_10_PASS=GREEN")

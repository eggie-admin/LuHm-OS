#!/usr/bin/env python3
"""Fail-closed Samsung Play Aramoor release gate. Source only, never device evidence."""
from pathlib import Path
import json,re,copy

ROOT=Path(__file__).resolve().parents[1]
HTML=(ROOT/"frontEnd/index.html").read_text()
CSS=(ROOT/"frontEnd/styles.css").read_text()
JS=(ROOT/"frontEnd/app.js").read_text()
KOTLIN=(ROOT/"androidWeb3Plugin/plugin/src/main/java/art/eggiebagelface/luhmos/web3/AndroidWeb3CockpitPlugin.kt").read_text()
GODOT=(ROOT/"scripts/main.gd").read_text()
BRIDGE=json.loads((ROOT/"doctrine/androidWeb3BridgeV2.json").read_text())
FIELD=json.loads((ROOT/"receipts/aramoorSamsungFieldObservation20261114.json").read_text())

def audit(html=HTML,css=CSS,js=JS,kotlin=KOTLIN,godot=GODOT,bridge=BRIDGE,field=FIELD):
    failures=[]
    def need(cond,label):
        if not cond:failures.append(label)
    need(html.count("data-luhm-play-aramoor")==1,"PLAY_CONTROL_MISSING_OR_DUPLICATE")
    need("PLAY ARAMOOR" in html and 'role="status"' in html,"PLAY_NOT_DISCOVERABLE")
    need(".playAramoorButton" in css and "min-height: 58px" in css and "focus-visible" in css,"PLAY_ACCESSIBILITY")
    need('postNative("aramoor_requested")' in js,"PLAY_TO_TYPED_JS")
    need('const accepted = postNative("aramoor_requested")' in js,"PLAY_TO_BRIDGE_CALL")
    need('"aramoor_requested" -> {' in kotlin and 'emitSignal(ARAMOOR_REQUESTED.name)' in kotlin,"NATIVE_TO_GODOT")
    need('private val ARAMOOR_REQUESTED = SignalInfo("aramoor_requested")' in kotlin,"NATIVE_SIGNAL")
    need('"world_requested", "aramoor_requested", "cockpit_ready", "local_art_pick_requested" -> setOf("type")' in kotlin,"EXACT_KEYS")
    need("payload.keys().asSequence().toSet() != expectedKeys" in kotlin,"NO_EXTRA_MESSAGE_KEYS")
    need('setOf(LOCAL_ORIGIN)' in kotlin and 'sourceOrigin.toString() != LOCAL_ORIGIN' in kotlin and 'isMainFrame' in kotlin,"NATIVE_ORIGIN")
    need('android_web3_plugin.connect("aramoor_requested", _enter_aramoor_mode)' in godot,"GODOT_WORLD_ROUTE")
    need('AramoorMainAdapterScript.new().open_world(self)' in godot,"GODOT_DELEGATED_WORLD")
    need(len(godot.splitlines()) <= 350,"MAIN_LINE_BUDGET")
    types=[x.get("type") for x in bridge.get("javascriptToNative",[])]
    need(types==["cockpitReady","oniRequested","worldRequested","aramoorRequested"],"CANON_BRIDGE_DRIFT")
    secure=bridge.get("security",{})
    need(all(secure.get(x) is True for x in ("allowedMainFrameOnly","exactOriginOnly")),"ORIGIN_AUTHORITY")
    need(all(secure.get(x) is False for x in ("arbitraryNavigation","networkFallback","addJavascriptInterface","fileScheme","contentScheme","mixedContent","arbitraryCommands","shellAuthority","crownAuthority")),"UNSAFE_BRIDGE")
    need('addJavascriptInterface' not in kotlin and 'allowFileAccess = false' in kotlin and 'allowContentAccess = false' in kotlin,"ANDROID_WEBVIEW_HARDENING")
    need(field.get("status")=="OBSERVED_INSTALL_AND_COCKPIT_ONLY","FAKE_DEVICE_STATE")
    need(field.get("crown")=="STOP" and field.get("releaseAuthority") is False,"FALSE_CROWN")
    need(all("proof that Play Aramoor" not in x for x in field.get("observations",[]) if isinstance(x,str)),"VIDEO_OVERCLAIM")
    need(field.get("apkSha256")=="24a8aef2c2fe44767260d5ca8055e5cfcd2637799180fbe79e06e36d2a3f9a21","HISTORICAL_APK_IDENTITY_DRIFT")
    return failures

def main():
    failures=audit()
    changes=[
       ("no_play",dict(html=HTML.replace("data-luhm-play-aramoor","data-luhm-play-dummy"))),
       ("no_bridge",dict(js=JS.replace('postNative("aramoor_requested")','postNative("world_requested")'))),
       ("no_native",dict(kotlin=KOTLIN.replace('emitSignal(ARAMOOR_REQUESTED.name)','emitSignal(WORLD_REQUESTED.name)'))),
       ("extra_keys",dict(kotlin=KOTLIN.replace('"world_requested", "aramoor_requested", "cockpit_ready", "local_art_pick_requested" -> setOf("type")','"world_requested", "aramoor_requested", "cockpit_ready" -> setOf("type", "payload")'))),
       ("no_godot",dict(godot=GODOT.replace('connect("aramoor_requested", _enter_aramoor_mode)','connect("aramoor_requested", enterWorldMode)'))),
       ("rights_escape",dict(bridge={**BRIDGE,"security":{**BRIDGE["security"],"shellAuthority":True}})),
       ("false_device",dict(field={**FIELD,"status":"DEVICE_GAMEPLAY_GREEN"})),
    ]
    for name, kwargs in changes:
        if not audit(**kwargs):failures.append("NEGATIVE_FALSE_GREEN:"+name)
    if failures:raise SystemExit("RED_ARAMOOR_SAMSUNG_NATIVE_PLAY="+",".join(failures))
    print("GREEN_ARAMOOR_SAMSUNG_NATIVE_PLAY_SOURCE")
    print("NEGATIVE_CONTROLS=7")
    print("OBSERVED_SAMSUNG_INSTALL_AND_COCKPIT_ONLY")
    print("GAMEPLAY_TOUCH_AND_OWNER_RELEASE_SIGNING=PENDING")

if __name__=="__main__":
    main()

#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors = []
warnings = []

def require(ok, message):
    if not ok:
        errors.append(message)

contract_path = ROOT / "doctrine" / "ANDROID_WEB3_COCKPIT_SWITCH_V1.json"
source_path = ROOT / "doctrine" / "SOURCE_OF_TRUTH.json"
html_path = ROOT / "frontEnd" / "index.html"
app_path = ROOT / "frontEnd" / "app.js"
frontend_readme = ROOT / "frontEnd" / "README.md"
backend_readme = ROOT / "backEndGui" / "README.md"

for path in [contract_path, source_path, html_path, app_path, frontend_readme, backend_readme]:
    require(path.is_file(), f"missing required file: {path.relative_to(ROOT)}")

if errors:
    for e in errors:
        print("ERROR:", e)
    raise SystemExit(2)

contract = json.loads(contract_path.read_text(encoding="utf-8"))
source = json.loads(source_path.read_text(encoding="utf-8"))
html = html_path.read_text(encoding="utf-8")
app = app_path.read_text(encoding="utf-8")
front = frontend_readme.read_text(encoding="utf-8")
back = backend_readme.read_text(encoding="utf-8")

require(contract.get("status") == "AMBER_ANDROID_WEB3_COCKPIT_WRAPPER_DEVICE_PROOF_PENDING", "milestone must remain AMBER until wrapper/device proof exists")
require(contract.get("authority") == "Professor", "Professor authority drift")
require(contract.get("crownStatus") == "STOP", "Crown must remain STOP")
require(contract.get("promotion") is False, "promotion must remain false")
require(contract.get("targetArchitecture", {}).get("userFacingCockpit") == "Android System WebView hosting packaged LuHm frontEnd/", "WebView target drift")
require(contract.get("targetArchitecture", {}).get("frontendPrivilege") is False, "front end may not become privileged")
require(contract.get("targetArchitecture", {}).get("shellAuthority") is False, "shell authority forbidden")
require(contract.get("currentEvidence", {}).get("androidNativeWebViewWrapperImplemented") is False, "must not claim wrapper implementation before code/proof")
require(contract.get("currentEvidence", {}).get("physicalSamsungWebViewProof") == "PENDING", "must not fake Samsung WebView proof")

require(source.get("milestone", "").startswith("Android Web3 Cockpit"), "SOURCE_OF_TRUTH active milestone did not switch")
aw3 = source.get("androidWeb3Cockpit", {})
require(aw3.get("contract") == "doctrine/ANDROID_WEB3_COCKPIT_SWITCH_V1.json", "SOURCE_OF_TRUTH missing Web3 contract")
require(aw3.get("runtime") == "Android System WebView", "runtime must be Android System WebView")
require(aw3.get("webViewWrapper") == "PENDING_IMPLEMENTATION", "wrapper must remain pending")
require(aw3.get("physicalSamsungProof") == "PENDING", "physical proof must remain pending")
require(aw3.get("crownStatus") == "STOP", "source truth Crown must remain STOP")
require(source.get("cockpitSwitch", {}).get("historicalOnly") is True, "prior native cockpit receipt must be marked historical, not erased")

require("jquery-3.7.1.min.js" in html, "pinned local jQuery missing")
require("http://" not in html and "https://" not in html, "front-end HTML must not load remote runtime content")
for primitive in ("fetch(", "XMLHttpRequest", "WebSocket(", "eval(", "new Function("):
    require(primitive not in html and primitive not in app, f"forbidden web runtime primitive present: {primitive}")

require("luhm:backend:open" in app, "typed Godot/system boundary event missing")
require("Android Web3 cockpit" in html, "candidate cockpit identity missing from HTML")
require("Android System WebView" in front, "front-end runtime target not documented")
require("no shell execution" in back.lower() or "does not expose shell execution" in back.lower(), "Godot boundary must explicitly forbid shell execution")

status = "GREEN_STATIC_ANDROID_WEB3_COCKPIT_SWITCH" if not errors else "RED_ANDROID_WEB3_COCKPIT_SWITCH"
print(json.dumps({
    "schema":"luhm-os.android-web3-cockpit-static-audit.v1",
    "status":status,
    "errors":errors,
    "warnings":warnings,
    "runtimeWrapperProof":"PENDING",
    "physicalSamsungProof":"PENDING",
    "crownStatus":"STOP"
}, indent=2))
sys.exit(0 if not errors else 2)

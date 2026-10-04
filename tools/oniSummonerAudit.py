#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "frontEnd/plugins/incoming/luhm-oni-summoner"
CONTROL = ROOT / "doctrine/ONI_MESH_CONTROL_PLANE_V2.json"
TRUTH = ROOT / "doctrine/SOURCE_OF_TRUTH.json"
CONTRACT = ROOT / "doctrine/ONI_SUMMONER_PLUGIN_V1.json"
MCP_MODULE = ROOT / "host/mcp/luhmOniSummoner.py"
HARNESS_SERVER = ROOT / "host/mcp/luhmHarnessServer.py"
WIDGET = ROOT / "host/harness/oni-summoner-widget.html"
LAW = "AI proposes. Policy authorizes. CI proves. Human promotes."

errors: list[str] = []

def require(condition: bool, code: str) -> None:
    if not condition:
        errors.append(code)

def load(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"RED_JSON_{path.name}:{exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"RED_OBJECT_{path.name}")
        return {}
    return value

truth = load(TRUTH)
control = load(CONTROL)
contract = load(CONTRACT)
manifest = load(PLUGIN / "oni-manifest.json")
js = (PLUGIN / "jquery.luhmOniSummoner.js").read_text(encoding="utf-8")
css = (PLUGIN / "jquery.luhmOniSummoner.css").read_text(encoding="utf-8")
widget = WIDGET.read_text(encoding="utf-8")
mcp = MCP_MODULE.read_text(encoding="utf-8")
server = HARNESS_SERVER.read_text(encoding="utf-8")

require(truth.get("source_law") == LAW, "RED_SOURCE_LAW")
require(control.get("sourceLaw") == LAW, "RED_CONTROL_LAW")
require(contract.get("sourceLaw") == LAW, "RED_PLUGIN_LAW")
require(manifest.get("sourceLaw") == LAW, "RED_MANIFEST_LAW")
require(control.get("boss") == "Lum" == manifest.get("boss"), "RED_BOSS")
require(control.get("humanAuthority") == "Professor" == manifest.get("humanAuthority"), "RED_AUTHORITY")
require(control.get("topology", {}).get("maxParallelSupportWorkers") == 3, "RED_SUPPORT_LIMIT")
require(control.get("topology", {}).get("maxMutableSourceLanesPerCandidate") == 1, "RED_MUTABLE_LANES")
require(contract.get("maxParallelSupportWorkers") == 3, "RED_CONTRACT_SUPPORT_LIMIT")
require(contract.get("maxMutableSourceLanesPerCandidate") == 1, "RED_CONTRACT_MUTABLE_LANES")

roles = control.get("roles", {})
manifest_roles = {row.get("name"): row for row in manifest.get("roles", []) if isinstance(row, dict)}
require(set(roles) == set(manifest_roles), "RED_ROSTER_DRIFT")
for name, spec in roles.items():
    row = manifest_roles.get(name, {})
    require(row.get("kind") == spec.get("kind"), f"RED_ROLE_KIND_{name}")
    if name != "Lum":
        require(row.get("defaultAuthority") == spec.get("defaultAuthority"), f"RED_ROLE_AUTH_{name}")
    require(bool(row.get("skillPath")), f"RED_SKILL_PATH_{name}")
    require((ROOT / row.get("skillPath", "MISSING")).is_file(), f"RED_SKILL_MISSING_{name}")

require('const PLUGIN = "luhmOniSummoner"' in js, "RED_JQUERY_PLUGIN_NAME")
require('$.fn[PLUGIN].version = "1.0.0-candidate.1"' in js, "RED_PLUGIN_VERSION")
require('"luhm:oni:summon"' in js and '"luhm:oni:activity"' in js, "RED_EVENT_CONTRACT")
require("No observed task packet is active." in js, "RED_NO_FAKE_ACTIVITY")
require("prefers-reduced-motion" in css, "RED_REDUCED_MOTION")
require('aria-live' in js, "RED_ARIA_LIVE")
require("hidden chain-of-thought" in widget.lower(), "RED_THINKING_BOUNDARY")
require('request("tools/call",{name,arguments:args})' in widget, "RED_MCP_APPS_TOOL_CALL")
require('window.openai?.callTool' in widget, "RED_CHATGPT_CALLTOOL_FALLBACK")
require('name="luhm_open_oni_summoner"' in mcp, "RED_MCP_RENDER_TOOL")
require('name="luhm_request_oni"' in mcp, "RED_MCP_SUMMON_TOOL")
require('ONI_SUMMONER_UI_RESOURCE_URI = "ui://luhm-os/oni-summoner-v1.html"' in mcp, "RED_MCP_RESOURCE")
require('"executionStarted": False' in mcp, "RED_NO_FAKE_EXECUTION")
require('from luhmOniSummoner import register_oni_summoner' in server, "RED_MCP_SERVER_IMPORT")
require('register_oni_summoner(' in server, "RED_MCP_SERVER_REGISTRATION")
require('for key in ("agentId", "displayName", "name")' in mcp, "RED_CANONICAL_ROSTER_ALIAS_BRIDGE")
require('r.name||r.displayName||r.agentId||"UNKNOWN"' in widget, "RED_WIDGET_ROSTER_NORMALIZATION")

for forbidden in (".html(", "innerHTML", "eval(", "new Function", "XMLHttpRequest", "WebSocket", "EventSource"):
    require(forbidden not in js, "RED_JS_SINK_" + forbidden.replace(" ", "_"))
for forbidden in ("https://", "http://", "fetch("):
    require(forbidden not in js, "RED_PLUGIN_NETWORK_" + forbidden.replace("/", "_"))

for flag in ("mutationAuthority", "greenAuthority", "releaseAuthority", "publicationAuthority", "productionSigningAuthority"):
    require(contract.get("authority", {}).get(flag) is False, "RED_AUTHORITY_CREEP_" + flag)

status = "GREEN_ONI_SUMMONER_PLUGIN_SOURCE" if not errors else "RED_ONI_SUMMONER_PLUGIN_SOURCE"
report = {
    "schema": "luhm-os.oni-summoner-audit.v1",
    "status": status,
    "errors": errors,
    "roleCount": len(manifest_roles),
    "jquery": manifest.get("jquery", {}).get("required", "UNKNOWN"),
    "surfaces": ["jquery-in-app", "mcp-apps-in-chat"],
    "chatToolCall": "luhm_request_oni",
    "thinkingEcho": contract.get("thinkingEcho", "UNKNOWN"),
    "crownStatus": "STOP",
}
print(json.dumps(report, indent=2))
raise SystemExit(1 if errors else 0)

#!/usr/bin/env python3
"""Read-only integration audit: exact-source Godot export, MCP app, Render/Cloudflare split."""
import ast
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
doc = json.loads((root / "doctrine/godotInChatEdgeBridgeV1.json").read_text(encoding="utf-8"))
cf = json.loads((root / "doctrine/cloudflareAirTrafficControllerV1.json").read_text(encoding="utf-8"))
module = (root / "host/mcp/luhmHarness.py").read_text(encoding="utf-8")
player = (root / "host/harness/godotPlayerWidget.html").read_text(encoding="utf-8")
presets = (root / "export_presets.cfg").read_text(encoding="utf-8")
ast.parse(module)

def need(ok, message):
    if not ok:
        raise SystemExit("RED_GODOT_EDGE_" + message)

need(doc["schema"] == "luhmOs.godotInChatEdgeBridge.v1", "SCHEMA")
need(doc["status"] == "SOURCE_ONLY_INTEGRATION_CANDIDATE", "STATUS")
source = doc["sourceProof"]
need(source["playerCandidateCommit"] == "45eaaddd8bb72ca34c69c40a4214fca94364fe13", "BUILD_SOURCE")
need(source["godotWebExportWorkflowRunId"] == 37736153654, "BUILD_RECEIPT")
need(source["godotWebExportStatus"] == "GREEN_EXACT_SOURCE", "BUILD_STATE")
need(source["appHostProof"] == "NOT_VERIFIED" and source["androidChatGptPlaybackProof"] == "NOT_VERIFIED", "CLIENT_EVIDENCE")
app = doc["architecture"]["appLayer"]
origin = doc["architecture"]["originLayer"]
dns = doc["architecture"]["dnsLayer"]
need(app["resourceUri"] == "ui://luhm-os/godot-player-v1.html", "APP_URI")
need(app["toolName"] == "luhm_open_godot_player", "TOOL_ID")
need(app["resourceUri"] in module and 'name="luhm_open_godot_player"' in module, "TOOL_WIRING")
need('"/harness/godot-export/{asset_path:path}"' in module, "EXPORT_ROUTE")
need('"frameDomains": [public_origin] if public_origin else []' in module, "FRAME_ALLOWLIST")
need("wasm-unsafe-eval" in module and "allow-pointer-lock" in module, "WEBGL_SANDBOX")
need("<!-- LUHM_GODOT_FRAME -->" in player, "FRAME_TEMPLATE")
need(origin["javaRuntimeRequired"] is False, "JAVA_BOUNDARY")
need(all(x in origin["runtimeRequirements"] for x in ("javascript", "webassembly", "webgl2", "https")), "WEB_TECHNOLOGY")
need(origin["wasmMimeType"] == "application/wasm", "WASM_MIME")
need('variant/thread_support=false' in presets, "THREAD_POLICY")
need(cf["lanes"]["publicChatPluginMcp"]["currentEndpoint"] == origin["currentHttpsOrigin"] + "/mcp", "CURRENT_ORIGIN")
need(dns["recordProposal"]["type"] == "CNAME" and dns["recordProposal"]["proxied"] is False, "DNS_BOOTSTRAP")
need(dns["recordProposal"]["target"] == "luhm-os-harness-green.onrender.com", "DNS_TARGET")
need(dns["noLiveDnsMutation"] and dns["tunnelNotRequired"], "DNS_AUTHORITY")
need(doc["naming"]["preferredSlug"] == "luhm-os", "DRAGON_TAIL")
need(doc["safety"]["crownStatus"] == "STOP", "CROWN")
need(all(doc["safety"][x] is True for x in ("noAutomaticDeployment", "noDnsOrProxyChanges", "noProductionPublication")), "AUTHORITY")
states = {x["id"]: x["state"] for x in doc["evidenceGates"]}
need(states["exactGodotWebExport"] == "PROVED", "EXPORT_EVIDENCE")
need(states["staticHostDeployment"] == "UNVERIFIED" and states["androidEmbeddedPlayback"] == "UNVERIFIED", "HOST_EVIDENCE")
print("GREEN_GODOT_IN_CHAT_EDGE_SOURCE_ONLY")

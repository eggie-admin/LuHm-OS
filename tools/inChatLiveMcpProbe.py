#!/usr/bin/env python3
"""Read-only external smoke for two existing LuHm MCP Render services.

This is network observation, never ChatGPT host proof, Godot build, or Crown.
"""
from __future__ import annotations
import argparse
import json
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

ORIGINS = {
    "mcp": "https://luhm-os-harness-green.onrender.com",
    "godot": "https://luhm-os-godot-harness-green.onrender.com",
}
TOOLS = {
    "luhm_open_cockpit": "ui://luhm-os/cockpit-v2.html",
    "luhm_open_godot_player": "ui://luhm-os/godot-player-v1.html",
}
MOBILE_TOOLS = {"luhm_open_mobile_cockpit": "ui://luhm-os/mobile-cockpit-v1.html"}

def expected_tools(origin: str) -> dict[str, str]:
    # The Godot preview may lag the primary MCP service; never fabricate a shared deploy.
    return {**TOOLS, **(MOBILE_TOOLS if origin == ORIGINS["mcp"] else {})}

PROTOCOL = "2025-06-18"
MAX_BYTES = 2 * 1024 * 1024

def parse_rpc(body: bytes, content_type: str) -> dict:
    text = body.decode("utf-8", errors="replace")
    if content_type.startswith("text/event-stream"):
        data_lines = [line[5:].strip() for line in text.splitlines() if line.startswith("data:")]
        if not data_lines:
            raise ValueError("NO_SSE_DATA")
        return json.loads(data_lines[-1])
    return json.loads(text)

def read_public(origin: str, path: str, *, method: str = "GET",
                payload: dict | None = None) -> dict:
    if origin not in ORIGINS.values() or not path.startswith("/"):
        raise ValueError("OUTSIDE_FIXED_ORIGIN_ALLOWLIST")
    headers = {"Accept": "application/json, text/event-stream" if method == "POST" else "*/*",
               "User-Agent": "LuHm-read-only-crown-probe/1.0"}
    if method == "POST":
        headers["Content-Type"] = "application/json"
        headers["MCP-Protocol-Version"] = PROTOCOL
    data = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(origin + path, data=data, method=method, headers=headers)
    with urllib.request.urlopen(request, timeout=40) as response:
        raw = response.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ValueError("OVERSIZED_REMOTE_RESPONSE")
        return {"body": raw, "status": response.status,
                "contentType": response.headers.get("Content-Type", ""),
                "headers": dict(response.headers)}

def rpc(origin: str, method: str, rpc_id: int, params: dict | None = None) -> dict:
    request = {"jsonrpc": "2.0", "id": rpc_id, "method": method}
    if params is not None:
        request["params"] = params
    reply = read_public(origin, "/mcp", method="POST", payload=request)
    envelope = parse_rpc(reply["body"], reply["contentType"])
    if envelope.get("error"):
        raise ValueError(f"RPC_ERROR:{method}:{envelope['error'].get('code')}")
    if envelope.get("id") != rpc_id or not isinstance(envelope.get("result"), dict):
        raise ValueError(f"RPC_RESPONSE_ID_OR_RESULT_DRIFT:{method}")
    return envelope["result"]

def parse_script(html: str) -> str:
    scripts = re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>", html, re.I | re.S)
    if len(scripts) != 1:
        raise ValueError("COCKPIT_SCRIPT_COUNT")
    with tempfile.TemporaryDirectory() as path:
        target = Path(path) / "widget.js"
        target.write_text(scripts[0], encoding="utf-8")
        check = subprocess.run(["node", "--check", str(target)],
                               capture_output=True, text=True, timeout=10)
        if check.returncode:
            raise ValueError("COCKPIT_JAVASCRIPT_PARSE_FAIL")
    return "PARSE_PASS"

def observe(origin: str) -> dict:
    result: dict = {"origin": origin, "scope": "EXTERNAL_PUBLIC_MCP_ONLY",
                    "chatGptHost": "UNVERIFIED", "godotInteractive": "UNVERIFIED",
                    "checks": {}, "errors": []}
    def checked(name, operation):
        try:
            value = operation()
            result["checks"][name] = {"state": "PASS", "detail": value}
            return value
        except Exception as error:
            result["checks"][name] = {"state": "FAIL", "reason": str(error)[:220]}
            result["errors"].append(name)
            return None
    def config():
        raw = read_public(origin, "/harness/config.json")
        obj = json.loads(raw["body"])
        if obj.get("schema") != "luhmOs.harnessConfig.v2":
            raise ValueError("HARNESS_SCHEMA_DRIFT")
        return {"schema": obj["schema"]}
    checked("httpConfig", config)
    handshake = checked("mcpInitialize", lambda: rpc(origin, "initialize", 1, {
        "protocolVersion": PROTOCOL,
        "capabilities": {},
        "clientInfo": {"name": "luhm-observer", "version": "1.0"},
    }))
    if handshake is not None:
        result["checks"]["mcpInitialize"]["detail"] = {
            "server": handshake.get("serverInfo", {}).get("name", "UNKNOWN"),
            "protocol": handshake.get("protocolVersion", "UNKNOWN")}
    tools = checked("toolsList", lambda: rpc(origin, "tools/list", 2))
    discovered = {}
    required = expected_tools(origin)
    if tools is not None:
        for item in tools.get("tools", []):
            if item.get("name") in required:
                discovered[item["name"]] = (item.get("_meta") or {}).get("ui", {}).get("resourceUri")
        for name, expected in required.items():
            if discovered.get(name) != expected:
                result["errors"].append(f"missingOrDrift:{name}")
        result["checks"]["toolsList"]["detail"] = discovered
    cockpit = checked("cockpitUiResource", lambda: rpc(origin, "resources/read", 3, {"uri": TOOLS["luhm_open_cockpit"]}))
    if cockpit is not None:
        pages = [p.get("text", "") for p in cockpit.get("contents", []) if p.get("uri") == TOOLS["luhm_open_cockpit"]]
        checked("cockpitJavaScript", lambda: parse_script(pages[0]) if pages else (_ for _ in ()).throw(ValueError("EMPTY_COCKPIT_UI")))
    if origin == ORIGINS["mcp"]:
        mobile = checked("mobileUiResource", lambda: rpc(origin, "resources/read", 5, {"uri": MOBILE_TOOLS["luhm_open_mobile_cockpit"]}))
        if mobile is not None:
            pages = [p.get("text", "") for p in mobile.get("contents", []) if p.get("uri") == MOBILE_TOOLS["luhm_open_mobile_cockpit"]]
            checked("mobileJavaScript", lambda: parse_script(pages[0]) if pages else (_ for _ in ()).throw(ValueError("EMPTY_MOBILE_UI")))
            checked("mobileMountTest", lambda: (
                {"userGestureSource": "PRESENT_NOT_HOST_PROOF"} if pages and
                'id="nativeChatProofButton"' in pages[0] and
                "LUHM_CHAT_MOUNT_CANDIDATE userClicked=true" in pages[0]
                else (_ for _ in ()).throw(ValueError("MOBILE_MOUNT_GESTURE_MISSING"))
            ))
    player = checked("godotUiResource", lambda: rpc(origin, "resources/read", 4, {"uri": TOOLS["luhm_open_godot_player"]}))
    if player is not None:
        pages = [p.get("text", "") for p in player.get("contents", []) if p.get("uri") == TOOLS["luhm_open_godot_player"]]
        state = "IFRAME_CANDIDATE" if pages and "<iframe" in pages[0] else "NOT_STAGED"
        result["checks"]["godotViewerStage"] = {"state": state, "detail": "not a gameplay proof"}
    result["status"] = "EXTERNAL_MCP_PASS" if not result["errors"] else "EXTERNAL_MCP_VERIFY"
    return result

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", default="in-chat-public-mcp-probe.json")
    args = parser.parse_args()
    results = {k: observe(v) for k, v in ORIGINS.items()}
    report = {"schema": "luhmOs.publicMcpProbe.v1",
              "authority": "readOnlyObservation",
              "sourceGreen": False, "chatGptHostProven": False,
              "results": results}
    Path(args.report).write_text(json.dumps(report, indent=2) + "\n")
    for name, entry in results.items():
        print(name + ":" + entry["status"] + "; " + ",".join(entry["errors"]))
    print("PROBE_REPORT=" + args.report)
    # The workflow is an observation, NOT a runtime-green promotion gate.
    return 0

if __name__ == "__main__":
    sys.exit(main())

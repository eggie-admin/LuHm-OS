#!/usr/bin/env python3
"""Fail-closed, offline validation of a *Site-backed* LuHm MCP App mount.

Never infer a ChatGPT mobile iframe mount from these server-side checks.
Feed the unmodified tools/list and resources/read JSON-RPC result objects
from the *same exact Site MCP endpoint*, not the GitHub/Render harness.
Do not upload credentials, personal files, images or screenshots.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

MOBILE_URI = "ui://luhm-os/mobile-cockpit-v1.html"
MOBILE_TOOL = "luhm_open_mobile_cockpit"
APP_MIME = "text/html;profile=mcp-app"


def validate(tools_reply: object, resource_reply: object) -> dict:
    problems: list[str] = []
    # Untrusted, sanitized captures must produce RED evidence, not exceptions.
    if not isinstance(tools_reply, dict):
        tools_reply = {}
        problems.append("SITE_TOOLS_REPLY_MALFORMED")
    if not isinstance(resource_reply, dict):
        resource_reply = {}
        problems.append("SITE_RESOURCE_REPLY_MALFORMED")
    tools = tools_reply.get("tools")
    if not isinstance(tools, list):
        tools = []
        problems.append("SITE_TOOLS_LIST_MISSING")
    if any(not isinstance(t, dict) for t in tools):
        problems.append("SITE_TOOLS_LIST_MALFORMED_ENTRY")
    found = [t for t in tools if isinstance(t, dict) and t.get("name") == MOBILE_TOOL]
    if len(found) != 1:
        problems.append("SITE_MOBILE_TOOL_NOT_UNIQUE")
    else:
        metadata = found[0].get("_meta")
        if not isinstance(metadata, dict):
            if "_meta" in found[0]:
                problems.append("SITE_TOOL_META_MALFORMED")
            metadata = {}
        ui_meta = metadata.get("ui")
        if ui_meta is not None and not isinstance(ui_meta, dict):
            problems.append("SITE_TOOL_UI_META_MALFORMED")
        if (ui_meta.get("resourceUri") if isinstance(ui_meta, dict) else None) != MOBILE_URI:
            problems.append("SITE_TOOL_UI_RESOURCE_URI_MISSING")
        if metadata.get("openai/outputTemplate") != MOBILE_URI:
            problems.append("SITE_TOOL_OUTPUT_TEMPLATE_MISSING")
    contents = resource_reply.get("contents")
    if not isinstance(contents, list):
        contents = []
        problems.append("SITE_RESOURCE_READ_MISSING")
    if any(not isinstance(p, dict) for p in contents):
        problems.append("SITE_RESOURCE_READ_MALFORMED_ENTRY")
    found_pages = [p for p in contents if isinstance(p, dict) and p.get("uri") == MOBILE_URI]
    if len(found_pages) != 1:
        problems.append("SITE_MOBILE_UI_RESOURCE_NOT_UNIQUE")
    else:
        page = found_pages[0]
        if page.get("mimeType") != APP_MIME:
            problems.append("SITE_MOBILE_UI_WRONG_MIME")
        html = page.get("text")
        if not isinstance(html, str) or not html.lstrip().lower().startswith("<!doctype html"):
            problems.append("SITE_MOBILE_UI_HTML_MISSING")
        else:
            if len(html.encode("utf-8")) > 100_000:
                problems.append("SITE_MOBILE_UI_OVERSIZED")
            if "<script" not in html.lower() or "ui/initialize" not in html:
                problems.append("SITE_MOBILE_UI_HOST_BRIDGE_MISSING")
        read_meta = page.get("_meta")
        if not isinstance(read_meta, dict):
            if "_meta" in page:
                problems.append("SITE_RESOURCE_META_MALFORMED")
            read_meta = {}
        ui_meta = read_meta.get("ui")
        if ui_meta is not None and not isinstance(ui_meta, dict):
            problems.append("SITE_RESOURCE_UI_META_MALFORMED")
        if not isinstance(ui_meta.get("csp") if isinstance(ui_meta, dict) else None, dict):
            problems.append("SITE_MOBILE_UI_CSP_META_MISSING")
    return {
        "schema": "luhmOs.siteCastMountGuard.v1",
        "scope": "SAME_SITE_MCP_ENDPOINT_ONLY",
        "sourceAndServerContract": "PASS" if not problems else "FAIL",
        "problems": problems,
        "chatGptInlineMounted": "UNVERIFIED",
        "deviceTouchAndUndoProof": "UNVERIFIED",
        "siteBackendChanged": False,
        "crown": "STOP",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tools-json", required=True, type=Path)
    parser.add_argument("--resource-json", required=True, type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if args.tools_json.stat().st_size > 250_000 or args.resource_json.stat().st_size > 500_000:
        parser.error("input too large: submit only sanitized bounded MCP results")
    reply = validate(json.loads(args.tools_json.read_text()), json.loads(args.resource_json.read_text()))
    message = json.dumps(reply, indent=2) + "\n"
    if args.report:
        args.report.write_text(message, encoding="utf-8")
    print(message, end="")
    return int(reply["sourceAndServerContract"] != "PASS")


if __name__ == "__main__":
    raise SystemExit(main())

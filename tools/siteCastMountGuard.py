#!/usr/bin/env python3
"""Fail-closed Site MCP Apps resource binding audit.

Input MUST be sanitized captures from the SAME authenticated Site MCP endpoint.
GitHub harness and Render cannot be substituted for the owner-private Site.
A matched capture does not prove that ChatGPT displayed the visual card.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

SITE_URI = "ui://luhm-os/cockpit-site-v3.html"
SITE_TOOL = "luhm_open_cockpit"
MIME = "text/html;profile=mcp-app"


def collection(payload: object, key: str) -> list[dict]:
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if not isinstance(payload, dict):
        return []
    value = payload.get(key, [])
    return [x for x in value if isinstance(x, dict)] if isinstance(value, list) else []


def inspect(tools: object, resources: object, resource_read: object) -> dict:
    issues = []
    tool_matches = [item for item in collection(tools, "tools")
                    if item.get("name") == SITE_TOOL]
    if len(tool_matches) != 1:
        issues.append("site tool missing or duplicated")
    else:
        meta = tool_matches[0].get("_meta", {})
        if not isinstance(meta, dict):
            meta = {}
        ui = meta.get("ui", {})
        ui_uri = ui.get("resourceUri") if isinstance(ui, dict) else None
        fallback_uri = meta.get("openai/outputTemplate")
        if ui_uri != SITE_URI and fallback_uri != SITE_URI:
            issues.append("tool does not advertise the exact Site UI URI")
        if ui_uri and fallback_uri and ui_uri != fallback_uri:
            issues.append("tool UI URI and outputTemplate disagree")

    matches = [x for x in collection(resources, "resources") if x.get("uri") == SITE_URI]
    if len(matches) != 1:
        issues.append("Site resource missing or duplicated in resources/list")

    contents = collection(resource_read, "contents")
    views = [x for x in contents if x.get("uri") == SITE_URI]
    if len(views) != 1:
        issues.append("Site URI missing or duplicated in resources/read")
    else:
        view = views[0]
        if view.get("mimeType") != MIME:
            issues.append("Site UI resource MIME does not match MCP Apps")
        html = view.get("text", "")
        if not isinstance(html, str) or not html.strip() or "<" not in html:
            issues.append("Site HTML body is empty or not HTML-like")
        meta = view.get("_meta", {})
        ui = meta.get("ui") if isinstance(meta, dict) else None
        # Some hosts return CSP in resources/list rather than resources/read.
        candidates = [ui, matches[0].get("_meta", {}).get("ui") if matches and
                      isinstance(matches[0].get("_meta"), dict) else None]
        if not any(isinstance(v, dict) and isinstance(v.get("csp"), dict)
                   for v in candidates):
            issues.append("Site UI CSP metadata absent from resource payload")

    return {
        "schema": "luhmOs.siteCastMountGuard.v1",
        "siteResourceUri": SITE_URI,
        "siteToolName": SITE_TOOL,
        "captureStatus": "RED_SITE_RESOURCE_BINDING" if issues else "CAPTURE_CONSISTENT",
        "issues": issues,
        "chatGptInlineMountProven": False,
        "backendEdited": False,
        "ownerTouchProven": False,
        "crownStatus": "STOP",
    }


def self_test() -> None:
    tool = {"name": SITE_TOOL, "_meta": {"ui": {"resourceUri": SITE_URI},
            "openai/outputTemplate": SITE_URI}}
    resource = {"uri": SITE_URI}
    read = {"uri": SITE_URI, "mimeType": MIME, "text": "<html>Site app</html>",
            "_meta": {"ui": {"csp": {"connectDomains": [], "resourceDomains": []}}}}
    good = inspect({"tools": [tool]}, {"resources": [resource]}, {"contents": [read]})
    assert not good["issues"] and not good["chatGptInlineMountProven"]

    other = json.loads(json.dumps(tool))
    other["_meta"]["ui"]["resourceUri"] = "ui://luhm-os/cockpit-v2.html"
    other["_meta"]["openai/outputTemplate"] = "ui://luhm-os/cockpit-v2.html"
    assert inspect({"tools": [other]}, {"resources": [resource]},
                   {"contents": [read]})["issues"]
    no_mime = {**read, "mimeType": "text/html"}
    assert any("MIME" in x for x in inspect({"tools": [tool]},
        {"resources": [resource]}, {"contents": [no_mime]})["issues"])
    no_csp = {**read, "_meta": {}}
    assert any("CSP" in x for x in inspect({"tools": [tool]},
        {"resources": [resource]}, {"contents": [no_csp]})["issues"])
    no_resource = inspect({"tools": [tool]}, {"resources": []},
                          {"contents": [read]})
    assert no_resource["issues"]
    print("SITE_CAST_RESOURCE_GUARD_NEGATIVE_TESTS=PASS")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--tools", type=Path)
    parser.add_argument("--resources", type=Path)
    parser.add_argument("--resource-read", type=Path)
    args = parser.parse_args()
    if args.self_test:
        self_test()
    sources = [args.tools, args.resources, args.resource_read]
    if not any(sources):
        print(json.dumps({
            "schema": "luhmOs.siteCastMountGuard.v1",
            "captureStatus": "UNKNOWN_SITE_ENDPOINT_NOT_CAPTURED",
            "reason": "Three matching sanitized Site endpoint captures are required",
            "githubOrRenderCanSubstitute": False,
            "chatGptInlineMountProven": False,
            "crownStatus": "STOP",
        }, indent=2))
        return 0 if args.self_test else 2
    if not all(sources):
        parser.error("provide --tools, --resources, and --resource-read together")
    result = inspect(*[json.loads(path.read_text(encoding="utf-8")) for path in sources])
    print(json.dumps(result, indent=2))
    return 0 if not result["issues"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

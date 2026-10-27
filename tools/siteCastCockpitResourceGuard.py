#!/usr/bin/env python3
"""Fail-closed Site MCP Apps resource binding audit.

Input MUST be sanitized captures from the SAME authenticated Site MCP endpoint.
GitHub harness and Render cannot be substituted for the owner-private Site.
A matched capture does not prove that ChatGPT displayed the visual card.
"""
from __future__ import annotations

import argparse
import base64
import binascii
import json
from html.parser import HTMLParser
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


class ResourceHtmlParser(HTMLParser):
    """Structural HTML check; cannot prove JavaScript execution or app mounting."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tags: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list) -> None:
        self.tags.add(tag)


def html_from_content(view: dict) -> str | None:
    """MCP Apps permits text HTML or base64-encoded blob HTML."""
    raw_text = view.get("text")
    if isinstance(raw_text, str) and raw_text.strip():
        return raw_text
    blob = view.get("blob")
    if not isinstance(blob, str) or len(blob) > 2_800_000:
        return None
    try:
        return base64.b64decode(blob, validate=True).decode("utf-8")
    except (binascii.Error, ValueError, UnicodeDecodeError):
        return None


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

    # The MCP Apps specification permits UI-only resources to be omitted
    # from resources/list. A tool's advertised resourceUri plus successful
    # resources/read is authoritative; listing is optional discovery.
    matches = [x for x in collection(resources, "resources") if x.get("uri") == SITE_URI]
    if len(matches) > 1:
        issues.append("Site resource duplicated in resources/list")
    elif len(matches) == 1 and matches[0].get("mimeType") not in (None, MIME):
        issues.append("Site resources/list MIME does not match MCP Apps")

    contents = collection(resource_read, "contents")
    views = [x for x in contents if x.get("uri") == SITE_URI]
    if len(views) != 1:
        issues.append("Site URI missing or duplicated in resources/read")
    else:
        view = views[0]
        if view.get("mimeType") != MIME:
            issues.append("Site UI resource MIME does not match MCP Apps")
        html = html_from_content(view)
        if html is None or not html.lstrip().lower().startswith(
                ("<!doctype html", "<html")):
            issues.append("Site UI resource is not an HTML document (text or blob)")
        elif len(html.encode("utf-8")) > 2_000_000:
            issues.append("Site UI document exceeds 2 MB safety limit")
        else:
            parser = ResourceHtmlParser()
            parser.feed(html)
            if "html" not in parser.tags:
                issues.append("Site UI resource lacks an HTML document element")
            if "script" not in parser.tags:
                issues.append("Site UI resource has no application script")
        read_meta = view.get("_meta", {})
        list_meta = matches[0].get("_meta", {}) if len(matches) == 1 else {}
        for where, meta in (("resources/read", read_meta),
                            ("resources/list", list_meta)):
            ui = meta.get("ui") if isinstance(meta, dict) else None
            # MCP Apps specifies a restrictive default when CSP is omitted.
            # If a CSP is present, validate its structure; presence is not
            # mandatory and does not establish runtime or UI safety.
            if ui is not None and not isinstance(ui, dict):
                issues.append(where + " UI metadata is malformed")
            elif isinstance(ui, dict) and "csp" in ui:
                csp = ui["csp"]
                if not isinstance(csp, dict):
                    issues.append(where + " CSP metadata is malformed")
                elif any(not isinstance(value, list) or
                         not all(isinstance(domain, str) for domain in value)
                         for value in csp.values()):
                    issues.append(where + " CSP domain lists are malformed")

    return {
        "schema": "luhmOs.siteCastCockpitResourceGuard.v1",
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
    read = {"uri": SITE_URI, "mimeType": MIME,
            "text": '<!doctype html><html><script src="app.js"></script></html>',
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
    assert not inspect({"tools": [tool]}, {"resources": [resource]},
                       {"contents": [no_csp]})["issues"]
    bad_csp = {**read, "_meta": {"ui": {"csp": {"connectDomains": "*"}}}}
    assert any("CSP" in x for x in inspect({"tools": [tool]},
        {"resources": [resource]}, {"contents": [bad_csp]})["issues"])
    blob_read = {**read}
    blob_read.pop("text")
    blob_read["blob"] = base64.b64encode(read["text"].encode()).decode()
    assert not inspect({"tools": [tool]}, {"resources": [resource]},
                       {"contents": [blob_read]})["issues"]
    broken_blob = {**blob_read, "blob": "not_base64!"}
    assert any("HTML" in x for x in inspect({"tools": [tool]},
        {"resources": [resource]}, {"contents": [broken_blob]})["issues"])
    wrong_listing_mime = {**resource, "mimeType": "text/html"}
    assert any("MIME" in x for x in inspect({"tools": [tool]},
        {"resources": [wrong_listing_mime]}, {"contents": [read]})["issues"])
    no_resource = inspect({"tools": [tool]}, {"resources": []},
                          {"contents": [read]})
    assert not no_resource["issues"]  # UI-only listing may be omitted.
    no_list_endpoint = inspect({"tools": [tool]}, None,
                               {"contents": [read]})
    assert not no_list_endpoint["issues"]
    duplicated_listing = inspect({"tools": [tool]},
        {"resources": [resource, resource]}, {"contents": [read]})
    assert any("duplicated" in issue for issue in duplicated_listing["issues"])
    static_only = {**read, "text": "<html><h1>status JSON is not an app</h1></html>"}
    assert any("script" in x for x in inspect({"tools": [tool]},
        {"resources": [resource]}, {"contents": [static_only]})["issues"])
    not_html = {**read, "text": '{"tool":"ok"}'}
    assert any("HTML" in x for x in inspect({"tools": [tool]},
        {"resources": [resource]}, {"contents": [not_html]})["issues"])
    print("SITE_CAST_RESOURCE_GUARD_NEGATIVE_TESTS=PASS")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--tools", type=Path)
    parser.add_argument("--resources", type=Path, help="optional UI resource listing")
    parser.add_argument("--resource-read", type=Path)
    args = parser.parse_args()
    if args.self_test:
        self_test()
    if args.tools is None and args.resource_read is None and args.resources is None:
        print(json.dumps({
            "schema": "luhmOs.siteCastCockpitResourceGuard.v1",
            "captureStatus": "UNKNOWN_SITE_ENDPOINT_NOT_CAPTURED",
            "reason": "Matching sanitized Site tools/list and resources/read captures required; resources/list optional",
            "githubOrRenderCanSubstitute": False,
            "chatGptInlineMountProven": False,
            "crownStatus": "STOP",
        }, indent=2))
        return 0 if args.self_test else 2
    if args.tools is None or args.resource_read is None:
        parser.error("provide --tools and --resource-read together; --resources optional")
    def read_json(path: Path | None) -> object:
        return json.loads(path.read_text(encoding="utf-8")) if path else None
    result = inspect(read_json(args.tools), read_json(args.resources),
                     read_json(args.resource_read))
    print(json.dumps(result, indent=2))
    return 0 if not result["issues"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

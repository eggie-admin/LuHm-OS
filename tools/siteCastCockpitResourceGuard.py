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
from urllib.parse import urlsplit

SITE_URI = "ui://luhm-os/cockpit-site-v3.html"
SITE_TOOL = "luhm_open_cockpit"
MIME = "text/html;profile=mcp-app"
CSP_ORIGIN_FIELDS = {"connectDomains", "resourceDomains",
                     "frameDomains", "baseUriDomains"}


def valid_csp_origin(value: object, field: str) -> bool:
    """CSP metadata contains origins, never raw directives or arbitrary URLs."""
    if not isinstance(value, str) or not value or any(
            ch.isspace() for ch in value) or any(
            ch in value for ch in ("'", '"', ";", "?", "#", "\\")):
        return False
    try:
        parsed = urlsplit(value)
        if parsed.scheme not in ("https", "http", "wss", "ws"):
            return False
        if not parsed.netloc or not parsed.hostname or parsed.path:
            return False
        if parsed.username is not None or parsed.password is not None:
            return False
        host = parsed.hostname
        if "*" in host and not (
                field == "resourceDomains" and host.startswith("*.")
                and host.count("*") == 1 and len(host) > 2):
            return False
        if parsed.port is not None and not 1 <= parsed.port <= 65535:
            return False
        return True
    except ValueError:
        return False


def collection(payload: object, key: str) -> list[dict]:
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if not isinstance(payload, dict):
        return []
    value = payload.get(key, [])
    return [x for x in value if isinstance(x, dict)] if isinstance(value, list) else []


def unwrap_mcp_result(payload: object) -> object:
    """Accept bare captures or JSON-RPC result envelopes; reject error replies.

    Real MCP tools/list and resources/read can be saved as full JSON-RPC
    responses. Never let an error or contradictory sibling entries masquerade
    as a successful capture.
    """
    if not isinstance(payload, dict) or not any(
            key in payload for key in ("jsonrpc", "result", "error")):
        return payload
    if ("error" in payload or not isinstance(payload.get("result"), dict)
            or payload.get("jsonrpc", "2.0") != "2.0"
            or any(key in payload for key in ("tools", "resources", "contents"))):
        return {"_invalid_mcp_envelope": True}
    return payload["result"]


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
    tools = unwrap_mcp_result(tools)
    resources = unwrap_mcp_result(resources)
    resource_read = unwrap_mcp_result(resource_read)
    issues = []
    # A valid matching entry cannot launder malformed siblings in an MCP
    # capture. Preserve optional resources/list and sanitized array captures,
    # but reject any supplied collection with non-object members.
    for where, payload, key in (
        ("tools/list", tools, "tools"),
        ("resources/read", resource_read, "contents"),
        ("resources/list", resources, "resources"),
    ):
        if where == "resources/list" and payload is None:
            continue
        entries = (payload if isinstance(payload, list) else
                   payload.get(key) if isinstance(payload, dict) else None)
        if not isinstance(entries, list) or any(
                not isinstance(entry, dict) for entry in entries):
            issues.append(where + " capture has malformed entries")
    tool_matches = [item for item in collection(tools, "tools")
                    if item.get("name") == SITE_TOOL]
    if len(tool_matches) != 1:
        issues.append("site tool missing or duplicated")
    else:
        meta = tool_matches[0].get("_meta", {})
        if not isinstance(meta, dict):
            issues.append("site tool _meta is malformed")
            meta = {}
        ui = meta.get("ui")
        if ui is not None and not isinstance(ui, dict):
            issues.append("site tool UI metadata is malformed")
        ui_uri = ui.get("resourceUri") if isinstance(ui, dict) else None
        if isinstance(ui, dict) and "resourceUri" in ui and not isinstance(ui_uri, str):
            issues.append("site tool resourceUri is malformed")
        fallback_uri = meta.get("openai/outputTemplate")
        if "openai/outputTemplate" in meta and not isinstance(fallback_uri, str):
            issues.append("site tool outputTemplate is malformed")
        if ui_uri != SITE_URI and fallback_uri != SITE_URI:
            issues.append("tool does not advertise the exact Site UI URI")
        # A present but empty URI is contradictory evidence, not absence.
        # Never let a valid fallback mask a supplied empty MCP Apps URI.
        if ui_uri is not None and fallback_uri is not None and ui_uri != fallback_uri:
            issues.append("tool UI URI and outputTemplate disagree")

    # The MCP Apps specification permits UI-only resources to be omitted
    # from resources/list. A tool's advertised resourceUri plus successful
    # resources/read is authoritative; listing is optional discovery.
    # Optional discovery is not a license to silently accept a malformed
    # capture. None means not collected; an explicitly supplied capture must
    # have a valid resources array (an empty array is allowed).
    if resources is not None and not (
        isinstance(resources, list) or
        (isinstance(resources, dict) and isinstance(resources.get("resources"), list))
    ):
        issues.append("resources/list capture is malformed")
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
            # An absent _meta is valid, but a supplied non-object _meta
            # must never be silently treated as absent CSP evidence.
            if not isinstance(meta, dict):
                issues.append(where + " _meta is malformed")
                continue
            ui = meta.get("ui")
            # MCP Apps specifies a restrictive default when CSP is omitted.
            # If a CSP is present, validate its structure; presence is not
            # mandatory and does not establish runtime or UI safety.
            if ui is not None and not isinstance(ui, dict):
                issues.append(where + " UI metadata is malformed")
            elif isinstance(ui, dict) and "csp" in ui:
                csp = ui["csp"]
                if not isinstance(csp, dict):
                    issues.append(where + " CSP metadata is malformed")
                elif any(
                        field not in CSP_ORIGIN_FIELDS or
                        not isinstance(domains, list) or
                        not all(valid_csp_origin(domain, field)
                                for domain in domains)
                        for field, domains in csp.items()):
                    issues.append(where + " CSP domain lists contain invalid origins")

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

    # Real endpoint captures often include JSON-RPC 2.0 result envelopes.
    # Accept the successful envelope without weakening malformed/error gates.
    def rpc(payload: dict) -> dict:
        return {"jsonrpc": "2.0", "id": 7, "result": payload}

    wrapped = inspect(rpc({"tools": [tool]}),
                      rpc({"resources": [resource]}),
                      rpc({"contents": [read]}))
    assert wrapped["captureStatus"] == "CAPTURE_CONSISTENT"
    assert not wrapped["chatGptInlineMountProven"]
    assert not inspect(rpc({"tools": [tool]}), None,
                       rpc({"contents": [read]}))["issues"]
    assert not inspect({"result": {"tools": [tool]}}, None,
                       {"result": {"contents": [read]}})["issues"]
    for invalid in (
        {"jsonrpc": "2.0", "id": 7,
         "error": {"code": -32603, "message": "read failed"}},
        {"jsonrpc": "2.0", "id": 7, "result": []},
        {"jsonrpc": "1.0", "result": {"tools": [tool]}},
        {"result": {"tools": [tool]}, "tools": [tool]},
    ):
        assert inspect(invalid, None, {"contents": [read]})["issues"]
    assert inspect({"tools": [tool]},
                   {"jsonrpc": "2.0", "id": 7,
                    "error": {"code": -32603, "message": "list failed"}},
                   {"contents": [read]})["issues"]
    assert inspect({"tools": [tool]}, None,
                   {"jsonrpc": "2.0", "id": 7,
                    "error": {"code": -32603, "message": "read failed"}})["issues"]

    # Valid matching entries must not hide malformed siblings in any
    # supplied MCP collection. UI-only resources/list may still be absent.
    for where, bad_tools, bad_resources, bad_read in (
        ("tools/list", {"tools": [tool, "invalid"]},
         {"resources": [resource]}, {"contents": [read]}),
        ("resources/read", {"tools": [tool]},
         {"resources": [resource]}, {"contents": [read, "invalid"]}),
        ("resources/list", {"tools": [tool]},
         {"resources": [resource, "invalid"]}, {"contents": [read]}),
    ):
        problems = inspect(bad_tools, bad_resources, bad_read)["issues"]
        assert where + " capture has malformed entries" in problems

    # A valid legacy outputTemplate must not conceal malformed MCP Apps
    # metadata in an otherwise successful same-endpoint capture.
    bad_meta = {**tool, "_meta": "invalid"}
    assert any("_meta" in x for x in inspect({"tools": [bad_meta]},
        {"resources": [resource]}, {"contents": [read]})["issues"])
    bad_ui = {**tool, "_meta": {"ui": "invalid",
                               "openai/outputTemplate": SITE_URI}}
    assert any("UI metadata" in x for x in inspect({"tools": [bad_ui]},
        {"resources": [resource]}, {"contents": [read]})["issues"])
    bad_uri_type = {**tool, "_meta": {"ui": {"resourceUri": 42},
                                    "openai/outputTemplate": SITE_URI}}
    assert any("resourceUri is malformed" in x for x in inspect(
        {"tools": [bad_uri_type]}, {"resources": [resource]},
        {"contents": [read]})["issues"])
    bad_template_type = {**tool, "_meta": {"ui": {"resourceUri": SITE_URI},
                                         "openai/outputTemplate": 42}}
    assert any("outputTemplate is malformed" in x for x in inspect(
        {"tools": [bad_template_type]}, {"resources": [resource]},
        {"contents": [read]})["issues"])

    # Both metadata fields may be supported for compatibility, but a
    # supplied empty value must not be laundered by the valid peer.
    empty_ui_uri = {**tool, "_meta": {"ui": {"resourceUri": ""},
                                    "openai/outputTemplate": SITE_URI}}
    assert any("disagree" in x for x in inspect(
        {"tools": [empty_ui_uri]}, {"resources": [resource]},
        {"contents": [read]})["issues"])
    empty_template = {**tool, "_meta": {"ui": {"resourceUri": SITE_URI},
                                      "openai/outputTemplate": ""}}
    assert any("disagree" in x for x in inspect(
        {"tools": [empty_template]}, {"resources": [resource]},
        {"contents": [read]})["issues"])

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
    # Explicit malformed metadata must fail closed even if HTML and URI
    # otherwise match. An omitted _meta remains permitted.
    bad_read_meta = {**read, "_meta": "invalid"}
    assert any("resources/read _meta is malformed" in x for x in inspect(
        {"tools": [tool]}, {"resources": [resource]},
        {"contents": [bad_read_meta]})["issues"])
    bad_list_meta = {**resource, "_meta": ["invalid"]}
    assert any("resources/list _meta is malformed" in x for x in inspect(
        {"tools": [tool]}, {"resources": [bad_list_meta]},
        {"contents": [read]})["issues"])
    bad_csp = {**read, "_meta": {"ui": {"csp": {"connectDomains": "*"}}}}
    assert any("CSP" in x for x in inspect({"tools": [tool]},
        {"resources": [resource]}, {"contents": [bad_csp]})["issues"])
    # A string array alone is insufficient: CSP requires explicit origins.
    for bad_origin in ("*", "data:", "'unsafe-inline'",
                       "https://cdn.example.com/path",
                       "https://cdn.example.com;script-src *",
                       "https://user:pass@cdn.example.com"):
        bad_csp_origin = {**read, "_meta": {"ui": {"csp": {
            "resourceDomains": [bad_origin]}}}}
        assert any("CSP" in x for x in inspect(
            {"tools": [tool]}, {"resources": [resource]},
            {"contents": [bad_csp_origin]})["issues"])
    unknown_csp_field = {**read, "_meta": {"ui": {"csp": {
        "script-src": ["https://cdn.example.com"]}}}}
    assert any("CSP" in x for x in inspect(
        {"tools": [tool]}, {"resources": [resource]},
        {"contents": [unknown_csp_field]})["issues"])
    good_csp = {**read, "_meta": {"ui": {"csp": {
        "resourceDomains": ["https://*.example.com"],
        "connectDomains": ["https://api.example.com", "wss://ws.example.com"],
        "frameDomains": [], "baseUriDomains": []}}}}
    assert not inspect({"tools": [tool]}, {"resources": [resource]},
                       {"contents": [good_csp]})["issues"]
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
    malformed_listing = inspect({"tools": [tool]},
        {"resources": "invalid"}, {"contents": [read]})
    assert any("malformed" in issue for issue in malformed_listing["issues"])
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

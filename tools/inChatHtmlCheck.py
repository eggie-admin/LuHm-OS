#!/usr/bin/env python3
"""Deterministic LuHm in-chat HTML preflight.

Usage:
    python3 tools/inChatHtmlCheck.py frontEnd/index.html

This is a static source check. It never claims visual/browser/device proof.
"""
from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path


class Collector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tags: list[str] = []
        self.ids: list[str] = []
        self.hooks: list[str] = []
        self.scripts: list[str] = []
        self.stylesheets: list[str] = []
        self.inline_handlers: list[str] = []
        self.forms = 0
        self.buttons = 0
        self.inputs = 0

    def handle_starttag(self, tag: str, attrs):
        self.tags.append(tag)
        attr = dict(attrs)
        if attr.get("id"):
            self.ids.append(attr["id"])
        for key in attr:
            if key.startswith("data-luhm-"):
                self.hooks.append(key)
            if key.lower().startswith("on"):
                self.inline_handlers.append(key)
        if tag == "script" and attr.get("src"):
            self.scripts.append(attr["src"])
        if tag == "link" and attr.get("rel") == "stylesheet" and attr.get("href"):
            self.stylesheets.append(attr["href"])
        if tag == "form":
            self.forms += 1
        elif tag == "button":
            self.buttons += 1
        elif tag == "input":
            self.inputs += 1


def check(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    p = Collector()
    p.feed(text)

    duplicate_ids = sorted({x for x in p.ids if p.ids.count(x) > 1})
    network_primitives = sorted(set(re.findall(r"\b(fetch|XMLHttpRequest|WebSocket|EventSource)\b", text)))
    dangerous_sinks = sorted(set(re.findall(r"\b(innerHTML|outerHTML|document\.write|eval\s*\(|new\s+Function\s*\()", text)))
    external_urls = sorted(set(re.findall(r"(?:src|href)=[\"'](https?://[^\"']+)", text, flags=re.I)))

    required = {
        "doctype": text.lstrip().lower().startswith("<!doctype html>"),
        "lang": bool(re.search(r"<html[^>]+lang=[\"'][^\"']+[\"']", text, flags=re.I)),
        "charset": bool(re.search(r"<meta[^>]+charset=", text, flags=re.I)),
        "viewport": "name=\"viewport\"" in text or "name='viewport'" in text,
        "main": "main" in p.tags,
        "title": "title" in p.tags,
        "luhmCockpitHook": "data-luhm-cockpit" in p.hooks,
    }

    jquery_index = next((i for i, s in enumerate(p.scripts) if "jquery" in s.lower()), None)
    app_index = next((i for i, s in enumerate(p.scripts) if s.endswith("app.js")), None)
    script_order_ok = jquery_index is not None and app_index is not None and jquery_index < app_index

    failures = []
    if not all(required.values()):
        failures.append("required_structure")
    if duplicate_ids:
        failures.append("duplicate_ids")
    if p.inline_handlers:
        failures.append("inline_event_handlers")
    if network_primitives:
        failures.append("network_primitive_in_html")
    if dangerous_sinks:
        failures.append("dangerous_dom_sink_in_html")
    if external_urls:
        failures.append("external_http_asset")
    if not script_order_ok:
        failures.append("script_order")

    return {
        "schema": "luhm-os.in-chat-html-check.v1",
        "path": str(path),
        "status": "GREEN_STATIC_HTML" if not failures else "RED_STATIC_HTML",
        "visualProof": "NOT_CLAIMED",
        "browserProof": "NOT_CLAIMED",
        "required": required,
        "scriptOrder": {"scripts": p.scripts, "jqueryBeforeApp": script_order_ok},
        "counts": {"tags": len(p.tags), "buttons": p.buttons, "forms": p.forms, "inputs": p.inputs, "luhmHooks": len(set(p.hooks))},
        "duplicateIds": duplicate_ids,
        "inlineHandlers": sorted(set(p.inline_handlers)),
        "networkPrimitives": network_primitives,
        "dangerousSinks": dangerous_sinks,
        "externalHttpAssets": external_urls,
        "stylesheets": p.stylesheets,
        "failures": failures,
    }


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: inChatHtmlCheck.py <html-path>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    if not path.is_file():
        print(json.dumps({"status": "RED_STATIC_HTML", "error": "file_not_found", "path": str(path)}, indent=2))
        return 2
    receipt = check(path)
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt["status"] == "GREEN_STATIC_HTML" else 1


if __name__ == "__main__":
    raise SystemExit(main())

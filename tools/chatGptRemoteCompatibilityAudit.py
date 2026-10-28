#!/usr/bin/env python3
"""Offline OpenAI plugin remote-compatibility source audit, never host-mount proof."""
from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DOC = "doctrine/chatGptRemoteCompatibilityDebugLaneV1.json"
PLUGIN = "plugins/luhm-os/plugin.json"
MCP = "plugins/luhm-os/mcp.json"
HARNESS = "host/mcp/luhmHarness.py"
MOBILE = "host/harness/mobileCockpitWidget.html"
PRIVACY = "publicationSite/privacy.html"
TERMS = "publicationSite/terms.html"


def audit_data(policy: dict, plugin: dict, mcp: dict, harness: str,
               mobile: str, privacy: str, terms: str) -> list[str]:
    errors: list[str] = []
    def require(value, tag):
        if not value:
            errors.append(tag)

    require(policy.get("schema") == "luhmOs.chatGptRemoteCompatibilityDebugLane.v1", "schema")
    require(policy.get("status") == "SOURCE_CANDIDATE_DEBUG_NOT_DEPLOYED", "candidateOnly")
    require(policy.get("crownStatus") == "STOP", "crownStop")
    require(policy.get("noNewSitePlugin") is True and
            policy.get("noPublicPublishing") is True, "siteIdentity")
    require(policy.get("stagedProof", {}).get("sourcePassCannotOverrideHostRed") is True, "proofBoundary")
    require(policy.get("hostMount", {}).get("userObserved") == "RED_ANDROID_SOMETHING_WENT_WRONG", "androidRed")
    require(policy.get("target", {}).get("independentOwnedSitePlugin", {}).get("sharing") == "USER_PRIVATE", "privateSite")

    require(plugin.get("$schema") == "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json", "portableSchema")
    require(plugin.get("name") == "luhm-os" and plugin.get("license") == "GPL-3.0-only", "packageIdentity")
    interface = plugin.get("extensions", {}).get("com.openai", {}).get("interface", {})
    require(bool(interface.get("displayName")) and len(interface.get("displayName", "")) <= 30, "displayName")
    short = interface.get("shortDescription", "")
    require(isinstance(short, str) and 0 < len(short) <= 30 and "\n" not in short, "shortDescription")
    require(isinstance(interface.get("longDescription"), str)
            and 0 < len(interface.get("longDescription", "")) <= 4000, "longDescription")
    prompts = interface.get("defaultPrompt")
    require(isinstance(prompts, list) and 1 <= len(prompts) <= 3
            and all(isinstance(p, str) and 0 < len(p.strip()) <= 128
                    and p == p.strip() and "\n" not in p and "\r" not in p
                    and not re.search(r"@[A-Za-z]", p) for p in prompts), "starterPromptLimit")
    if isinstance(prompts, list):
        require(len(set(prompts)) == len(prompts), "starterPromptDuplicates")
    urls = ("websiteURL", "supportURL", "privacyPolicyURL", "termsOfServiceURL")
    for key in urls:
        try:
            p = urlparse(interface.get(key, ""))
            ok = p.scheme == "https" and bool(p.netloc) and not p.username and not p.password
        except (TypeError, ValueError):
            ok = False
        require(ok, "https" + key)
    review = plugin.get("extensions", {}).get("com.openai", {}).get("review", {}).get("test_cases", {})
    good = review.get("positive", [])
    bad = review.get("negative", [])
    require(isinstance(good, list) and len(good) == 5 and
            all(all(isinstance(x.get(k), str) and x[k].strip() for k in
                    ("description", "prompt", "tools_triggered", "expected_behavior"))
                for x in good), "fivePositiveCases")
    require(isinstance(bad, list) and len(bad) == 3 and
            all(isinstance(x.get("prompt"), str) and x["prompt"].strip() for x in bad), "threeNegativeCases")

    servers = mcp.get("mcpServers", {})
    require(mcp.get("$schema") == "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json"
            and list(servers) == ["luhm"], "mcpConfig")
    remote = servers.get("luhm", {})
    require(remote.get("type") == "streamable-http"
            and remote.get("url") == "https://luhm-os-harness-green.onrender.com/mcp", "stableHttpsMcp")
    require('APP_MIME_TYPE = "text/html;profile=mcp-app"' in harness, "mcpAppsMime")
    require('UI_RESOURCE_URI = "ui://luhm-os/cockpit-v2.html"' in harness, "fullUiResource")
    require('MOBILE_COCKPIT_RESOURCE_URI = "ui://luhm-os/mobile-cockpit-v1.html"' in harness, "mobileUiResource")
    require('name="luhm_open_cockpit"' in harness
            and 'name="luhm_open_mobile_cockpit"' in harness, "namedRenderTools")
    require('"ui": {"resourceUri": UI_RESOURCE_URI' in harness and
            '"ui": {"resourceUri": MOBILE_COCKPIT_RESOURCE_URI' in harness
            and '"openai/outputTemplate": UI_RESOURCE_URI' in harness, "descriptorUiBinding")
    require('mime_type=APP_MIME_TYPE' in harness and
            'def luhm_mobile_cockpit_resource()' in harness, "htmlResourceRegistration")
    require('"fallbackText"' in harness and
            '"testerDeviceMount": "NOT_VERIFIED"' in harness, "textFallbackAndTruth")
    require('"ui/initialize"' in mobile and
            '"ui/notifications/tool-result"' in mobile, "mobileMcpAppsBridge")
    require(not re.search(r'<(?:script|link|img|iframe)[^>]+(?:src|href)\s*=\s*["\']https?://', mobile, re.I),
            "mobileNoRemoteScript")
    require("privacy" in privacy.lower() and "Hosting and logs" in privacy
            and "data" in privacy.lower(), "privacySource")
    require("terms" in terms.lower() and "LuHm" in terms, "termsSource")
    return sorted(set(errors))


def audit(root: Path = ROOT) -> list[str]:
    try:
        policy = json.loads((root / DOC).read_text(encoding="utf-8"))
        plugin = json.loads((root / PLUGIN).read_text(encoding="utf-8"))
        mcp = json.loads((root / MCP).read_text(encoding="utf-8"))
        args = [(root / p).read_text(encoding="utf-8") for p in
                (HARNESS, MOBILE, PRIVACY, TERMS)]
    except (OSError, ValueError, TypeError) as e:
        return ["missingOrInvalidSource:" + type(e).__name__]
    return audit_data(policy, plugin, mcp, *args)


if __name__ == "__main__":
    problems = audit()
    if problems:
        for problem in problems:
            print("RED_OPENAI_REMOTE_SOURCE " + problem)
        raise SystemExit(1)
    print("GREEN_OPENAI_REMOTE_SOURCE_CONTRACT")
    print("SITE_BACKEND_RESOURCE_READ=UNVERIFIED")
    print("CHATGPT_ANDROID_WIDGET=RED_OBSERVED")
    print("DIRECTORY_SUBMISSION=NOT_AUTHORIZED")

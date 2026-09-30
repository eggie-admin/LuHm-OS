#!/usr/bin/env python3
"""Fail-closed source audit for the LuHm OS public read-only plugin milestone."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MILESTONE = ROOT / "doctrine/PLUGIN_PUBLICATION_MILESTONE_20260930.json"
SOURCE = ROOT / "doctrine/SOURCE_OF_TRUTH.json"
BOUNDARY = ROOT / "doctrine/RELEASE_BOUNDARY.json"
ENTERPRISE = ROOT / "doctrine/MCP_ENTERPRISE_SCOPE_V1.json"
SERVER = ROOT / "host/mcp/luhmMcpServer.py"
HARNESS_SERVER = ROOT / "host/mcp/luhmHarnessServer.py"
HARNESS_MODULE = ROOT / "host/mcp/luhmHarness.py"
REQUIREMENTS = ROOT / "host/mcp/requirements.txt"
PLUGIN = ROOT / "plugins/luhm-os/plugin.json"
MCP_CONFIG = ROOT / "plugins/luhm-os/mcp.json"
TESTS = ROOT / "plugins/luhm-os/review-tests.json"
PRIVACY = ROOT / "plugins/luhm-os/PRIVACY.md"
TERMS = ROOT / "plugins/luhm-os/TERMS.md"
SUBMISSION = ROOT / "plugins/luhm-os/PUBLIC_SUBMISSION_DRAFT.md"
HARNESS_MCP_URL = "https://luhm-os-harness-green.onrender.com/mcp"


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must be a JSON object")
    return value


def validate(
    milestone: dict,
    source: dict,
    boundary: dict,
    enterprise: dict,
    server_text: str,
    harness_server_text: str,
    harness_module_text: str,
    plugin: dict,
    mcp_config: dict,
    tests: dict,
) -> list[str]:
    errors: list[str] = []
    law = "AI proposes. Policy authorizes. CI proves. Human promotes."
    if milestone.get("sourceLaw") != law or source.get("source_law") != law:
        errors.append("source law drift")
    if source.get("authority") != "Professor" or milestone.get("authority") != "Professor":
        errors.append("Professor authority drift")
    if source.get("reconciliation", {}).get("status") != "GREEN_CURRENT_MAIN_SOURCE_TRUTH_RECONCILED":
        errors.append("current-main source truth reconciliation is not GREEN")
    if source.get("status", "").startswith("GREEN_FULL_SOURCE"):
        errors.append("full product GREEN overclaim")
    if milestone.get("scope") != "public-read-only-chatgpt-plugin":
        errors.append("publication scope drift")
    runtime = milestone.get("runtime", {})
    for field in ("toolsReadOnly",):
        if runtime.get(field) is not True:
            errors.append(f"runtime contract lost {field}")
    for field in ("writeToolsAllowed", "destructiveToolsAllowed", "productionSigningAuthority"):
        if runtime.get(field) is not False:
            errors.append(f"runtime authority creep: {field}")
    if milestone.get("publicationAuthority") is not False:
        errors.append("publication authority must remain false until external gates prove")
    if milestone.get("directoryPublicationProven") is not False:
        errors.append("directory publication cannot be source-asserted")
    if milestone.get("crownStatus") != "STOP":
        errors.append("Crown must remain STOP before external gates")

    deny = set(boundary.get("deny", []))
    if "publishing" not in deny:
        errors.append("global publishing deny was removed before external proof")
    if "production signing" not in deny:
        errors.append("production signing deny missing")

    transport = enterprise.get("transport", {})
    auth = enterprise.get("authentication", {})
    if transport.get("production") != "streamable-http" or transport.get("productionPath") != "/mcp":
        errors.append("production MCP transport drift")
    if transport.get("statelessHttp") is not True:
        errors.append("MCP transport must remain stateless")
    if transport.get("sessionOwnsAuthority") is not False or transport.get("sessionOwnsSourceTruth") is not False:
        errors.append("MCP session authority creep")
    if auth.get("currentPublicTools") != "anonymous-read-only":
        errors.append("public tool posture is not anonymous read-only")
    if auth.get("privateOrWriteToolsRequireOAuth21") is not True:
        errors.append("private/write OAuth boundary drift")
    if auth.get("oauthImplemented") is not False:
        errors.append("OAuth implementation overclaim")

    required_server_phrases = (
        "READ_ONLY_INTERNAL",
        "readOnlyHint=True",
        "destructiveHint=False",
        "openWorldHint=False",
        'streamable_http_path="/mcp"',
        "stateless_http=True",
        "enable_dns_rebinding_protection=True",
        '@server.custom_route("/healthz"',
        '@server.custom_route("/.well-known/openai-apps-challenge"',
        "OPENAI_APPS_CHALLENGE",
        'host="0.0.0.0"',
    )
    for phrase in required_server_phrases:
        if phrase not in server_text:
            errors.append(f"MCP server publication hardening missing: {phrase}")

    required_harness_server_phrases = (
        "register_harness(",
        "core.READ_ONLY_INTERNAL",
        'streamable_http_path="/mcp"',
        "stateless_http=True",
        'host="0.0.0.0"',
    )
    for phrase in required_harness_server_phrases:
        if phrase not in harness_server_text:
            errors.append(f"harness server publication hardening missing: {phrase}")

    required_harness_module_phrases = (
        'UI_RESOURCE_URI = "ui://luhm-os/cockpit-v1.html"',
        'APP_MIME_TYPE = "text/html;profile=mcp-app"',
        'name="luhm_open_cockpit"',
        '"publicationAuthority": False',
        '"greenAuthority": False',
    )
    for phrase in required_harness_module_phrases:
        if phrase not in harness_module_text:
            errors.append(f"ChatGPT harness UI contract missing: {phrase}")

    mcp_url = mcp_config.get("mcpServers", {}).get("luhm", {}).get("url")
    if mcp_url != HARNESS_MCP_URL:
        errors.append(f"plugin MCP endpoint is not live harness: {mcp_url!r}")

    interface = plugin.get("extensions", {}).get("com.openai", {}).get("interface", {})
    if interface.get("capabilities") != ["Read"]:
        errors.append("plugin manifest is not read-only")
    for field in ("displayName", "shortDescription", "longDescription", "developerName", "websiteURL", "privacyPolicyURL", "termsOfServiceURL"):
        if not interface.get(field):
            errors.append(f"plugin manifest missing {field}")

    positive = tests.get("positive", [])
    negative = tests.get("negative", [])
    if len(positive) != 5:
        errors.append("publication requires exactly five positive tests")
    if len(negative) != 3:
        errors.append("publication requires exactly three negative tests")
    for entry in positive + negative:
        if not entry.get("prompt") or not entry.get("expected"):
            errors.append("review test missing prompt or expected behavior")

    for path in (SERVER, HARNESS_SERVER, HARNESS_MODULE, REQUIREMENTS, MCP_CONFIG, PRIVACY, TERMS, SUBMISSION):
        if not path.is_file() or path.stat().st_size == 0:
            errors.append(f"missing publication input: {path.relative_to(ROOT)}")

    return errors


def git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def main() -> int:
    milestone = load(MILESTONE)
    source = load(SOURCE)
    boundary = load(BOUNDARY)
    enterprise = load(ENTERPRISE)
    plugin = load(PLUGIN)
    mcp_config = load(MCP_CONFIG)
    tests = load(TESTS)
    errors = validate(
        milestone,
        source,
        boundary,
        enterprise,
        SERVER.read_text(encoding="utf-8"),
        HARNESS_SERVER.read_text(encoding="utf-8"),
        HARNESS_MODULE.read_text(encoding="utf-8"),
        plugin,
        mcp_config,
        tests,
    )
    report = {
        "schema": "luhm-os.plugin-publication-source-audit.v2",
        "status": "GREEN_PUBLICATION_SOURCE_READY" if not errors else "RED_PUBLICATION_SOURCE",
        "sourceCommit": git_head(),
        "mcpUrl": mcp_config.get("mcpServers", {}).get("luhm", {}).get("url", "UNKNOWN"),
        "chatUiResource": "ui://luhm-os/cockpit-v1.html",
        "contractErrors": errors,
        "publicationAuthority": False,
        "directoryPublicationProven": False,
        "externalGates": milestone.get("externalGates", {}),
        "crownStatus": "STOP",
    }
    out = ROOT / "build/plugin-publication/source-readiness.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if errors:
        raise SystemExit("plugin publication source audit failed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

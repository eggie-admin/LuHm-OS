#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCTRINE = ROOT / "doctrine" / "MCP_ENTERPRISE_SCOPE_V1.json"
SERVER = ROOT / "host" / "mcp" / "luhmMcpServer.py"
SKILL = ROOT / "plugins" / "luhm-os" / "skills" / "luhm-agent-workflow" / "SKILL.md"
MCP = ROOT / "plugins" / "luhm-os" / "mcp.json"
RENDER = ROOT / "render.yaml"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load(path: Path) -> dict:
    value = json.loads(read(path))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain an object")
    return value


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def audit() -> None:
    for path in (DOCTRINE, SERVER, SKILL, MCP, RENDER):
        require(path.is_file(), f"missing enterprise MCP input: {path.relative_to(ROOT)}")

    doctrine = load(DOCTRINE)
    require(doctrine.get("schema") == "luhm-os.mcp-enterprise-scope.v1", "enterprise MCP schema drift")
    require(doctrine.get("sourceLaw") == "AI proposes. Policy authorizes. CI proves. Human promotes.", "source law drift")

    transport = doctrine.get("transport", {})
    require(transport.get("production") == "streamable-http", "production transport drift")
    require(transport.get("productionPath") == "/mcp", "production MCP path drift")
    require(transport.get("productionFqdn") == "mcp.eggiebagelface.art", "production FQDN drift")
    require(transport.get("statelessHttp") is True, "production HTTP must remain stateless")
    require(transport.get("sessionOwnsAuthority") is False, "session must not own authority")
    require(transport.get("sessionOwnsSourceTruth") is False, "session must not own source truth")

    scope = doctrine.get("requestScope", {})
    required_fields = scope.get("requiredFieldsForTruthSensitiveRouting", [])
    require(required_fields == ["taskId", "sourceRef", "scopeId"], "truth-sensitive request scope drift")
    require(scope.get("unknownSourceMayPromote") is False, "UNKNOWN source must not promote")
    require(scope.get("scopeMayEscalateAuthority") is False, "scope must not escalate authority")
    require(scope.get("scopeMayOverrideCrown") is False, "scope must not override Crown")

    auth = doctrine.get("authentication", {})
    require(auth.get("currentPublicTools") == "anonymous-read-only", "public beta auth posture drift")
    require(auth.get("privateOrWriteToolsRequireOAuth21") is True, "private/write tools must require OAuth 2.1")
    require(auth.get("oauthImplemented") is False, "OAuth must not be claimed implemented before evidence")
    require("established identity provider" in str(auth.get("implementationRule", "")).lower(), "IdP implementation rule missing")

    server = read(SERVER)
    for phrase in (
        "ENTERPRISE_SCOPE",
        "TRUTH_SCOPE_KINDS",
        "luhm_validate_scope",
        "luhm_transport_contract",
        "taskId",
        "sourceRef",
        "scopeId",
        "sessionOwnsAuthority",
        "sessionOwnsSourceTruth",
        "stateless_http=True",
        "max_request_body_size=1 * 1024 * 1024",
        "enable_dns_rebinding_protection=True",
    ):
        require(phrase in server, f"enterprise MCP server hardening missing: {phrase}")

    require('TRUTH_SCOPE_KINDS = {"patch", "build", "release"}' in server, "truth-sensitive route set drift")
    require("if truth_sensitive or kind in TRUTH_SCOPE_KINDS:" in server, "route scope enforcement missing")
    require("_require_explicit_scope(scope)" in server, "explicit scope validation missing")
    require("oauthImplemented" in server and "RED_MCP_OAUTH_STATUS_OVERCLAIM" in server, "OAuth overclaim guard missing")

    skill = read(SKILL)
    for phrase in (
        "Transport state is not source truth",
        "taskId",
        "sourceRef",
        "scopeId",
        "OAuth 2.1",
        "established identity provider",
        "OpenAI Secure MCP Tunnel",
    ):
        require(phrase in skill, f"portable skill enterprise rule missing: {phrase}")

    skill_lower = skill.lower()
    for forbidden in (
        "session owns authority",
        "session grants authority",
        "session owns source truth",
        "session grants source truth",
        "session state grants authority",
    ):
        require(forbidden not in skill_lower, f"skill accidentally grants authority to session state: {forbidden}")

    mcp = load(MCP)
    remote = mcp.get("mcpServers", {}).get("luhm", {})
    require(remote.get("type") == "streamable-http", "plugin MCP transport drift")
    require(remote.get("url") == "https://mcp.eggiebagelface.art/mcp", "plugin MCP FQDN drift")

    render = read(RENDER)
    for phrase in (
        "name: luhm-os-mcp",
        "region: ohio",
        "healthCheckPath: /healthz",
        "LUHM_MCP_PROFILE",
        "value: production",
        "LUHM_MCP_FQDN",
        "mcp.eggiebagelface.art",
        "OPENAI_APPS_CHALLENGE",
        "sync: false",
    ):
        require(phrase in render, f"Render deployment hardening missing: {phrase}")

    print("LUHM_MCP_ENTERPRISE_GREEN")


if __name__ == "__main__":
    audit()

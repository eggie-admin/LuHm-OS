#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "luhm-os"
RENDER_BLUEPRINT = ROOT / "render.yaml"
MCP_SERVER = ROOT / "host" / "mcp" / "luhmMcpServer.py"
EXPECTED_FQDN = "mcp.eggiebagelface.art"
EXPECTED_REMOTE_URL = f"https://{EXPECTED_FQDN}/mcp"


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


def require_https(url: str, label: str) -> None:
    parsed = urlparse(url)
    require(parsed.scheme == "https" and bool(parsed.netloc), f"{label} must be HTTPS")


def audit() -> None:
    required = [
        PLUGIN / "plugin.json",
        PLUGIN / "mcp.json",
        PLUGIN / "mcp.local.json",
        PLUGIN / "mcp.remote.example.json",
        PLUGIN / "README.md",
        PLUGIN / "DEPLOYMENT.md",
        PLUGIN / "PRIVACY.md",
        PLUGIN / "TERMS.md",
        PLUGIN / "skills" / "luhm-agent-workflow" / "SKILL.md",
        RENDER_BLUEPRINT,
        MCP_SERVER,
    ]
    for path in required:
        require(path.is_file(), f"missing plugin/deployment file: {path.relative_to(ROOT)}")

    manifest = load(PLUGIN / "plugin.json")
    require(manifest.get("$schema") == "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json", "plugin schema drift")
    require(manifest.get("name") == "luhm-os", "plugin name drift")
    require(manifest.get("version") == "0.2.0", "plugin version drift")
    require(manifest.get("license") == "GPL-3.0-only", "plugin license drift")
    require(manifest.get("repository") == "https://github.com/eggie-admin/LuHm-OS", "plugin repository drift")

    openai = manifest.get("extensions", {}).get("com.openai", {})
    interface = openai.get("interface", {})
    require(interface.get("displayName") == "LuHm OS", "OpenAI display name drift")
    require(interface.get("capabilities") == ["Read"], "candidate plugin must remain read-only")
    require(interface.get("brandColor") == "#7C3AED", "brand color drift")
    for key in ("websiteURL", "privacyPolicyURL", "termsOfServiceURL"):
        require_https(str(interface.get(key, "")), key)
    prompts = interface.get("defaultPrompt", [])
    require(isinstance(prompts, list) and len(prompts) >= 2, "plugin starter prompts missing")

    production_mcp = load(PLUGIN / "mcp.json")
    require(production_mcp.get("$schema") == "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json", "production MCP schema drift")
    production = production_mcp.get("mcpServers", {}).get("luhm", {})
    require(production.get("type") == "streamable-http", "production MCP transport drift")
    production_url = str(production.get("url", ""))
    require(production_url == EXPECTED_REMOTE_URL, "production MCP FQDN drift")
    require_https(production_url, "production MCP URL")
    require(urlparse(production_url).hostname == EXPECTED_FQDN, "production MCP hostname drift")

    local_mcp = load(PLUGIN / "mcp.local.json")
    require(local_mcp.get("$schema") == "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json", "local MCP schema drift")
    local = local_mcp.get("mcpServers", {}).get("luhm_local", {})
    require(local.get("type") == "streamable-http", "local MCP transport drift")
    require(local.get("url") == "http://127.0.0.1:8788/mcp", "local MCP must remain loopback development only")

    remote_example = load(PLUGIN / "mcp.remote.example.json")
    remote_template = remote_example.get("mcpServers", {}).get("luhm_remote", {})
    require(remote_template.get("type") == "streamable-http", "remote template transport drift")
    remote_template_url = str(remote_template.get("url", ""))
    require_https(remote_template_url, "remote MCP template")
    require(urlparse(remote_template_url).hostname == "luhm-mcp.example.invalid", "remote template must remain non-routable")

    server_source = read(MCP_SERVER)
    for phrase in (
        "MCPServer(",
        "ToolAnnotations(",
        "readOnlyHint=True",
        "destructiveHint=False",
        "openWorldHint=False",
        "TransportSecuritySettings(",
        "enable_dns_rebinding_protection=True",
        "allowed_hosts=[fqdn, f\"{fqdn}:*\"]",
        "@server.custom_route(\"/healthz\"",
        "@server.custom_route(\"/.well-known/openai-apps-challenge\"",
        "OPENAI_APPS_CHALLENGE",
        "host=\"0.0.0.0\"",
        "max_request_body_size=1 * 1024 * 1024",
    ):
        require(phrase in server_source, f"MCP production hardening missing: {phrase}")

    render = read(RENDER_BLUEPRINT)
    for phrase in (
        "name: luhm-mcp",
        "region: ohio",
        "autoDeployTrigger: checksPass",
        "healthCheckPath: /healthz",
        f"- {EXPECTED_FQDN}",
        "renderSubdomainPolicy: enabled",
        "python host/mcp/luhmMcpServer.py --check",
        "python tools/luhmPluginPackageAudit.py",
        "LUHM_MCP_PROFILE",
        "value: production",
        "LUHM_MCP_FQDN",
        "OPENAI_APPS_CHALLENGE",
        "sync: false",
        "PYTHON_VERSION",
        "value: 3.12.11",
    ):
        require(phrase in render, f"Render enterprise deployment drift: {phrase}")

    deployment = read(PLUGIN / "DEPLOYMENT.md")
    for phrase in (
        "mcp.eggiebagelface.art",
        "DNS only",
        "AAAA",
        "letsencrypt.org",
        "pki.goog",
        "CROWN CUTOVER",
        "OAuth 2.1",
        "renderSubdomainPolicy: disabled",
    ):
        require(phrase in deployment, f"deployment runbook missing gate: {phrase}")

    skill = read(PLUGIN / "skills" / "luhm-agent-workflow" / "SKILL.md")
    for phrase in (
        "AI proposes. Policy authorizes. CI proves. Human promotes.",
        "Lum is the only conversational boss",
        "UNKNOWN",
        "Secure MCP Tunnel",
    ):
        require(phrase in skill, f"portable skill missing doctrine: {phrase}")

    privacy = read(PLUGIN / "PRIVACY.md")
    terms = read(PLUGIN / "TERMS.md")
    require("development candidate" in privacy.lower(), "privacy candidate status missing")
    require("development candidate" in terms.lower(), "terms candidate status missing")
    require("provider credentials" in privacy.lower(), "privacy credential boundary missing")
    require("human" in terms.lower(), "terms human-authority boundary missing")

    secret_pattern = re.compile(
        r"(sk-proj-[A-Za-z0-9_-]{8,}|BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY|AIza[A-Za-z0-9_-]{20,})"
    )
    scan_roots = [PLUGIN, ROOT / "host" / "mcp"]
    for scan_root in scan_roots:
        for path in scan_root.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".json", ".md", ".txt", ".py"}:
                require(secret_pattern.search(read(path)) is None, f"secret-like material detected: {path.relative_to(ROOT)}")
    require(secret_pattern.search(render) is None, "secret-like material detected: render.yaml")

    print("LUHM_PLUGIN_PACKAGE_GREEN")


if __name__ == "__main__":
    audit()

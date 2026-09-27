#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "luhm-os"


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
        PLUGIN / "mcp.remote.example.json",
        PLUGIN / "README.md",
        PLUGIN / "PRIVACY.md",
        PLUGIN / "TERMS.md",
        PLUGIN / "skills" / "luhm-agent-workflow" / "SKILL.md",
    ]
    for path in required:
        require(path.is_file(), f"missing plugin package file: {path.relative_to(ROOT)}")

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

    local_mcp = load(PLUGIN / "mcp.json")
    require(local_mcp.get("$schema") == "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json", "local MCP schema drift")
    local = local_mcp.get("mcpServers", {}).get("luhm_local", {})
    require(local.get("type") == "streamable-http", "local MCP transport drift")
    require(local.get("url") == "http://127.0.0.1:8788/mcp", "local MCP must remain loopback development only")

    remote_mcp = load(PLUGIN / "mcp.remote.example.json")
    remote = remote_mcp.get("mcpServers", {}).get("luhm_remote", {})
    require(remote.get("type") == "streamable-http", "remote MCP transport drift")
    remote_url = str(remote.get("url", ""))
    require_https(remote_url, "remote MCP template")
    require(urlparse(remote_url).hostname == "luhm-mcp.example.invalid", "remote template must remain non-routable until deployed")
    require("127.0.0.1" not in remote_url and "localhost" not in remote_url, "remote template points at loopback")

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
    for path in PLUGIN.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".json", ".md", ".txt"}:
            require(secret_pattern.search(read(path)) is None, f"secret-like material detected: {path.relative_to(ROOT)}")

    print("LUHM_PLUGIN_PACKAGE_GREEN")


if __name__ == "__main__":
    audit()

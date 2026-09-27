#!/usr/bin/env python3
"""LuHm OS MCP server for local development and hardened Render deployment.

The server exposes a bounded read-only tool surface. It never embeds provider
credentials, mutates repository state, executes Crown-gated actions, signs builds,
publishes releases, or grants GREEN authority.

Local profile: loopback only.
Production profile: Render/public HTTPS edge, explicit FQDN host allowlist,
health endpoint, and OpenAI domain-verification challenge endpoint.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from mcp.server import MCPServer
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import ToolAnnotations
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse, Response

ROOT = Path(__file__).resolve().parents[2]
SOURCE_TRUTH = ROOT / "doctrine" / "SOURCE_OF_TRUTH.json"
CONTROL_PLANE = ROOT / "doctrine" / "ONI_MESH_CONTROL_PLANE_V2.json"
OPENAI_DEPLOYMENT = ROOT / "doctrine" / "openAiLumOniDeployment-20260927.json"
ROUTER = ROOT / "tools" / "lumTaskRouter.py"
ROUTE_KINDS = {
    "direct", "read", "records", "proof", "patch", "build", "external",
    "monitor", "release", "art", "media", "dictation", "asset",
}

SERVER_NAME = "luhm-os"
SERVER_VERSION = "0.2.0"
DEFAULT_PUBLIC_FQDN = "mcp.eggiebagelface.art"
LOCAL_HOST = "127.0.0.1"
LOCAL_PORT = 8788

server = MCPServer(
    SERVER_NAME,
    title="LuHm OS",
    description="Read-only LuHm source-truth, Oni routing, and proof-contract tools.",
    version=SERVER_VERSION,
    instructions=(
        "LuHm OS is evidence-gated. AI proposes; policy authorizes; CI proves; human promotes. "
        "Use read-only status, roster, routing, and proof-contract tools to inspect the current workflow. "
        "Never infer GREEN, promotion, signing, publication, or public exposure from these tools. "
        "Professor remains final authority."
    ),
)

READ_ONLY_INTERNAL = ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    openWorldHint=False,
    idempotentHint=True,
)


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} must contain an object")
    return value


def _skill_status() -> list[dict[str, Any]]:
    control = _load_json(CONTROL_PLANE)
    roles = control.get("roles", {})
    directory_map = {
        "Lum": "lum",
        "Kiri": "kiriContextOni",
        "Tetsu": "buildOnis",
        "Kaji": "buildOnis",
        "Momo": "momoResearchOni",
        "Shiori": "shioriCriticOni",
        "DrNao": "doctorOni",
        "Kugi": "kugiToolOni",
        "Fumi": "fumiSecretaryOni",
        "Sumi": "sumiAssetOni",
        "Koe": "koeDictationOni",
        "Yume": "yumeArtOni",
    }
    out: list[dict[str, Any]] = []
    for name, role in roles.items():
        folder = directory_map.get(name, "")
        skill = ROOT / "agents" / folder / "SKILL.md" if folder else None
        out.append(
            {
                "name": name,
                "kind": role.get("kind", "UNKNOWN") if isinstance(role, dict) else "UNKNOWN",
                "defaultAuthority": role.get("defaultAuthority", "UNKNOWN") if isinstance(role, dict) else "UNKNOWN",
                "skillPath": str(skill.relative_to(ROOT)) if skill else "UNKNOWN",
                "skillPresent": bool(skill and skill.is_file()),
            }
        )
    return out


def _status_payload() -> dict[str, Any]:
    truth = _load_json(SOURCE_TRUTH)
    deploy = _load_json(OPENAI_DEPLOYMENT)
    return {
        "schema": "luhm-os.mcp-status.v1",
        "sourceLaw": truth.get("source_law", "UNKNOWN"),
        "sourceTruthStatus": truth.get("status", "UNKNOWN"),
        "canonicalMain": truth.get("canonicalMain", {}),
        "candidate": truth.get("currentFullGameCandidate", {}),
        "agentWorkflowCandidate": truth.get("agentWorkflowCandidate", {}),
        "remainingExternalGates": truth.get("remainingExternalGates", {}),
        "openAiDeploymentStatus": deploy.get("status", "UNKNOWN"),
        "publicationAuthority": bool(truth.get("publication_authority", False)),
        "promotion": bool(truth.get("promotion", False)),
        "greenAuthority": False,
    }


def _roster_payload() -> dict[str, Any]:
    control = _load_json(CONTROL_PLANE)
    return {
        "schema": "luhm-os.mcp-roster.v1",
        "boss": control.get("boss", "UNKNOWN"),
        "humanAuthority": control.get("humanAuthority", "UNKNOWN"),
        "maxParallelSupportWorkers": control.get("topology", {}).get("maxParallelSupportWorkers", "UNKNOWN"),
        "helperRecruitment": control.get("topology", {}).get("helperRecruitment", "UNKNOWN"),
        "roles": _skill_status(),
        "greenAuthority": False,
    }


def _profile() -> str:
    return os.environ.get("LUHM_MCP_PROFILE", "local").strip().lower()


def _public_fqdn() -> str:
    fqdn = os.environ.get("LUHM_MCP_FQDN", DEFAULT_PUBLIC_FQDN).strip().lower().rstrip(".")
    if not fqdn or "://" in fqdn or "/" in fqdn or ":" in fqdn:
        raise ValueError("LUHM_MCP_FQDN must be a bare DNS hostname")
    return fqdn


def _render_external_hostname() -> str:
    hostname = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "").strip().lower().rstrip(".")
    if not hostname:
        return ""
    if "://" in hostname or "/" in hostname or ":" in hostname or not hostname.endswith(".onrender.com"):
        raise ValueError("RENDER_EXTERNAL_HOSTNAME must be a bare *.onrender.com hostname")
    return hostname


def _production_security() -> TransportSecuritySettings:
    fqdn = _public_fqdn()
    allowed_hosts = [fqdn, f"{fqdn}:*"]
    render_hostname = _render_external_hostname()
    if render_hostname:
        allowed_hosts.extend([render_hostname, f"{render_hostname}:*"])
    return TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=allowed_hosts,
        allowed_origins=[],
    )


def _assert_source_contract() -> None:
    status = _status_payload()
    roster = _roster_payload()
    if status["sourceLaw"] != "AI proposes. Policy authorizes. CI proves. Human promotes.":
        raise RuntimeError("RED_SOURCE_LAW_DRIFT")
    if not roster["roles"] or not all(role["skillPresent"] for role in roster["roles"]):
        raise RuntimeError("RED_AGENT_SKILL_MISSING")
    for kind in ("records", "proof"):
        if kind not in ROUTE_KINDS:
            raise RuntimeError("RED_ROUTE_KIND_MISSING")


@server.tool(annotations=READ_ONLY_INTERNAL)
def luhm_status() -> dict[str, Any]:
    """Read current LuHm source-truth and deployment gates without changing anything."""
    return _status_payload()


@server.tool(annotations=READ_ONLY_INTERNAL)
def luhm_agent_roster() -> dict[str, Any]:
    """List canonical Lum/Oni roles and whether each canonical SKILL.md is present."""
    return _roster_payload()


@server.tool(annotations=READ_ONLY_INTERNAL)
def luhm_route_task(
    kind: str,
    truth_sensitive: bool = False,
    contested: bool = False,
    external_fact: bool = False,
    asset_review: bool = False,
) -> dict[str, Any]:
    """Compute the deterministic LuHm task route and bounded worker plan without mutating state."""
    if kind not in ROUTE_KINDS:
        raise ValueError(f"unsupported task kind: {kind}")
    command = [sys.executable, str(ROUTER), kind]
    if truth_sensitive:
        command.append("--truth-sensitive")
    if contested:
        command.append("--contested")
    if external_fact:
        command.append("--external-fact")
    if asset_review:
        command.append("--asset-review")
    completed = subprocess.run(
        command,
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        timeout=10,
        env={"PATH": ""},
    )
    result = json.loads(completed.stdout)
    result["mcpMutationAuthority"] = False
    return result


@server.tool(annotations=READ_ONLY_INTERNAL)
def luhm_proof_contract() -> dict[str, Any]:
    """Return LuHm proof-vault and evidence authority boundaries without changing anything."""
    truth = _load_json(SOURCE_TRUTH)
    return {
        "schema": "luhm-os.mcp-proof-contract.v1",
        "androidRuntimeNetworkDefault": False,
        "androidProviderSecrets": False,
        "vault": {
            "storage": "app-private-content-addressed",
            "identity": "sha256",
            "importState": "UNKNOWN_UNTIL_ADJUDICATED",
            "rawSafUriExposedToModel": False,
        },
        "unknownIsNotGreen": bool(truth.get("unknown_is_not_green", True)),
        "sourceLaw": truth.get("source_law", "UNKNOWN"),
        "greenAuthority": False,
    }


@server.custom_route("/healthz", methods=["GET"])
async def healthz(_: Request) -> Response:
    """Minimal public liveness/readiness probe. Never returns project data or secrets."""
    try:
        _assert_source_contract()
    except Exception:
        return JSONResponse(
            {"status": "unhealthy", "service": SERVER_NAME, "version": SERVER_VERSION},
            status_code=503,
            headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"},
        )
    return JSONResponse(
        {"status": "ok", "service": SERVER_NAME, "version": SERVER_VERSION},
        headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"},
    )


@server.custom_route("/.well-known/openai-apps-challenge", methods=["GET"])
async def openai_apps_challenge(_: Request) -> Response:
    """Return exactly the OpenAI plugin domain-verification token when configured."""
    token = os.environ.get("OPENAI_APPS_CHALLENGE", "").strip()
    if not token:
        return PlainTextResponse(
            "not configured",
            status_code=404,
            headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"},
        )
    return PlainTextResponse(
        token,
        headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"},
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("transport", nargs="?", default="streamable-http", choices=("streamable-http", "stdio"))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    if args.check:
        _assert_source_contract()
        if _profile() == "production":
            _production_security()
        print("LUHM_MCP_SOURCE_GREEN")
        return 0

    if args.transport == "stdio":
        server.run(transport="stdio")
        return 0

    profile = _profile()
    if profile == "production":
        port = int(os.environ.get("PORT", "10000"))
        server.run(
            transport="streamable-http",
            host="0.0.0.0",
            port=port,
            streamable_http_path="/mcp",
            stateless_http=True,
            json_response=True,
            max_request_body_size=1 * 1024 * 1024,
            transport_security=_production_security(),
        )
        return 0

    server.run(
        transport="streamable-http",
        host=LOCAL_HOST,
        port=LOCAL_PORT,
        streamable_http_path="/mcp",
        stateless_http=True,
        json_response=True,
        max_request_body_size=1 * 1024 * 1024,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

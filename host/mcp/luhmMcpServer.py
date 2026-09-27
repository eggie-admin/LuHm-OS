#!/usr/bin/env python3
"""Private localhost MCP bridge for the LuHm OS agent workflow.

This server exposes read-only, deterministic workflow/status tools. It never embeds
provider credentials, mutates repository state, executes Crown-gated actions, or binds
to a public interface. ChatGPT developer-mode access should use OpenAI Secure MCP
Tunnel or another explicitly approved HTTPS bridge.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

ROOT = Path(__file__).resolve().parents[2]
SOURCE_TRUTH = ROOT / "doctrine" / "SOURCE_OF_TRUTH.json"
CONTROL_PLANE = ROOT / "doctrine" / "ONI_MESH_CONTROL_PLANE_V2.json"
OPENAI_DEPLOYMENT = ROOT / "doctrine" / "openAiLumOniDeployment-20260927.json"
ROUTER = ROOT / "tools" / "lumTaskRouter.py"

server = FastMCP(
    "luhm-os",
    host="127.0.0.1",
    port=8788,
    stateless_http=True,
    instructions=(
        "LuHm OS is evidence-gated. AI proposes; policy authorizes; CI proves; human promotes. "
        "Use read-only status/roster/routing tools to inspect the current workflow. Never infer GREEN, "
        "promotion, signing, publication, or public exposure from these tools. Professor is final authority."
    ),
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


@server.tool()
def luhm_status() -> dict[str, Any]:
    """Read current LuHm source-truth and deployment gates without changing anything."""
    truth = _load_json(SOURCE_TRUTH)
    deploy = _load_json(OPENAI_DEPLOYMENT)
    return {
        "schema": "luhm-os.mcp-status.v1",
        "sourceLaw": truth.get("source_law", "UNKNOWN"),
        "sourceTruthStatus": truth.get("status", "UNKNOWN"),
        "canonicalMain": truth.get("canonicalMain", {}),
        "candidate": truth.get("currentFullGameCandidate", {}),
        "remainingExternalGates": truth.get("remainingExternalGates", {}),
        "openAiDeploymentStatus": deploy.get("status", "UNKNOWN"),
        "publicationAuthority": bool(truth.get("publication_authority", False)),
        "promotion": bool(truth.get("promotion", False)),
        "greenAuthority": False,
    }


@server.tool()
def luhm_agent_roster() -> dict[str, Any]:
    """List canonical Lum/Oni roles and whether each canonical SKILL.md is present."""
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


@server.tool()
def luhm_route_task(
    kind: str,
    truth_sensitive: bool = False,
    contested: bool = False,
    external_fact: bool = False,
    asset_review: bool = False,
) -> dict[str, Any]:
    """Run the deterministic LuHm task router and return its bounded worker plan."""
    allowed = {"direct", "read", "patch", "build", "external", "monitor", "release", "art", "media", "dictation", "asset"}
    if kind not in allowed:
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


@server.tool()
def luhm_proof_contract() -> dict[str, Any]:
    """Return the proof-vault and evidence authority boundaries used by LuHm OS."""
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("transport", nargs="?", default="streamable-http", choices=("streamable-http", "stdio"))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        status = luhm_status()
        roster = luhm_agent_roster()
        if status["sourceLaw"] != "AI proposes. Policy authorizes. CI proves. Human promotes.":
            raise SystemExit("RED_SOURCE_LAW_DRIFT")
        if not roster["roles"] or not all(role["skillPresent"] for role in roster["roles"]):
            raise SystemExit("RED_AGENT_SKILL_MISSING")
        print("LUHM_MCP_SOURCE_GREEN")
        return 0
    server.run(transport=args.transport)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

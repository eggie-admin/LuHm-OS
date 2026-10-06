#!/usr/bin/env python3
"""LuHm OS MCP server for local development and hardened Render deployment.

The server exposes a bounded read-only tool surface. It never embeds provider
credentials, mutates repository state, executes Crown-gated actions, signs builds,
publishes releases, or grants GREEN authority.

Local profile: loopback only.
Production profile: Render/public HTTPS edge, explicit FQDN host allowlist,
health endpoint, OpenAI domain-verification challenge endpoint, and explicit
request scope for truth-sensitive routing. Transport/session state never owns
LuHm source truth or authority.
"""
from __future__ import annotations

import argparse
import json
import os
import re
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
SOURCE_TRUTH = ROOT / "doctrine" / "currentSourceTruthV3.json"
CONTROL_PLANE = ROOT / "doctrine" / "luhmAiControlPlaneV1.json"
AGENT_DEPLOYMENT = ROOT / "doctrine" / "agentSystemDeploymentV1.json"
ENTERPRISE_SCOPE = ROOT / "doctrine" / "mcpEnterpriseScopeV2.json"
API_SPINE = ROOT / "doctrine" / "apiSpineV1.json"
TRAFFIC_CONTROLLER = ROOT / "doctrine" / "cloudflareAirTrafficControllerV1.json"
HOUSEKEEPING = ROOT / "doctrine" / "belldandyHousekeepingV1.json"
NAMING_NAMESPACE = ROOT / "doctrine" / "namingNamespaceCanonV1.json"
COMMAND_HELP = ROOT / "doctrine" / "commandHelpV1.json"
PRECISION_COMMAND = ROOT / "doctrine" / "chatPrecisionCommandV1.json"
ROUTER = ROOT / "tools" / "lumTaskRouter.py"
ESCALATION_RESOLVER = ROOT / "tools" / "escalationKernel.py"
API_SPINE_RESOLVER = ROOT / "host" / "api" / "luhmApiSpine.py"
ROUTE_KINDS = {
    "direct", "read", "records", "proof", "patch", "build", "external",
    "diagnose", "research", "monitor", "release", "art", "media", "dictation", "asset",
}
TRUTH_SCOPE_KINDS = {"patch", "build", "release"}

SERVER_NAME = "luhm-os"
SERVER_VERSION = "0.5.3-beta"
DEFAULT_PUBLIC_FQDN = "mcp.eggiebagelface.art"
LOCAL_HOST = "127.0.0.1"
LOCAL_PORT = 8788

server = MCPServer(
    SERVER_NAME,
    title="LuHm OS",
    description="Read-only LuHm source-truth, help, escalation planning, agent roster, Belldandy housekeeping, capability-first API spine, Oni routing, proof, and transport tools.",
    version=SERVER_VERSION,
    instructions=(
        "LuHm OS is evidence-gated. AI proposes; policy authorizes; CI proves; human promotes. "
        "Use read-only status, help, escalation planning, roster, Belldandy housekeeping, routing, proof-contract, scope, and transport tools to inspect the current workflow. "
        "Truth-sensitive patch/build/release routing requires explicit taskId, sourceRef, and scopeId. "
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
    agents = control.get("agents", {})
    out: list[dict[str, Any]] = []
    for agent_id, role in agents.items():
        if not isinstance(role, dict):
            continue
        skill_rel = role.get("skillPath", "")
        skill = ROOT / skill_rel if skill_rel else None
        out.append(
            {
                "agentId": agent_id,
                "displayName": role.get("displayName", agent_id),
                "kind": role.get("kind", "UNKNOWN"),
                "defaultAuthority": role.get("defaultAuthority", "UNKNOWN"),
                "skillPath": skill_rel or "UNKNOWN",
                "skillPresent": bool(skill and skill.is_file()),
            }
        )
    return out

def _scope_value(value: Any, max_len: int = 256) -> str:
    text = str(value if value is not None else "").strip()
    if len(text) > max_len:
        raise ValueError("scope value exceeds maximum length")
    return text or "UNKNOWN"


def _scope_payload(
    taskId: str = "UNKNOWN",
    sourceRef: str = "UNKNOWN",
    scopeId: str = "UNKNOWN",
    candidateSha: str = "",
    proofContext: str = "",
) -> dict[str, Any]:
    candidate = _scope_value(candidateSha, 64) if candidateSha else "UNKNOWN"
    if candidate != "UNKNOWN" and not re.fullmatch(r"[0-9a-fA-F]{7,64}", candidate):
        raise ValueError("candidateSha must be a hexadecimal source digest")
    return {
        "schema": "luhm-os.mcp-request-scope.v1",
        "taskId": _scope_value(taskId, 160),
        "sourceRef": _scope_value(sourceRef, 256),
        "scopeId": _scope_value(scopeId, 160),
        "candidateSha": candidate,
        "proofContext": _scope_value(proofContext, 256) if proofContext else "UNKNOWN",
        "sessionOwnsAuthority": False,
        "sessionOwnsSourceTruth": False,
        "greenAuthority": False,
    }


def _require_explicit_scope(scope: dict[str, Any]) -> None:
    missing = [name for name in ("taskId", "sourceRef", "scopeId") if scope.get(name) in (None, "", "UNKNOWN")]
    if missing:
        raise ValueError("explicit request scope required: " + ", ".join(missing))


def _api_spine_payload() -> dict[str, Any]:
    spine = _load_json(API_SPINE)
    traffic = _load_json(TRAFFIC_CONTROLLER)
    return {
        "schema": "luhmOs.mcpApiSpine.v1",
        "spineSchema": spine.get("schema", "UNKNOWN"),
        "spineStatus": spine.get("status", "UNKNOWN"),
        "routing": spine.get("routing", {}),
        "providers": spine.get("providers", {}),
        "resilience": spine.get("resilience", {}),
        "renderSidecar": spine.get("renderSidecar", {}),
        "trafficController": {
            "schema": traffic.get("schema", "UNKNOWN"),
            "status": traffic.get("status", "UNKNOWN"),
            "provider": traffic.get("provider", "UNKNOWN"),
            "role": traffic.get("role", "UNKNOWN"),
            "lanes": traffic.get("lanes", {}),
            "authorityBoundary": traffic.get("authorityBoundary", {}),
        },
        "providerSpecificDetailsVisibleToEndUser": spine.get("publicInterface", {}).get("providerSpecificDetailsVisibleToEndUser", True),
        "greenAuthority": False,
        "crownAuthority": False,
    }


def _vowel_rip(name: str) -> str:
    parts = re.findall(r"[a-z]+|[A-Z][a-z0-9]*|[A-Z]+(?![a-z])|[0-9]+", name)
    out: list[str] = []
    for part in parts:
        if not part:
            continue
        first = part[0]
        rest = "".join(ch for ch in part[1:] if ch.lower() not in "aeiou")
        out.append(first + rest)
    return "".join(out)


def _help_entries() -> list[dict[str, Any]]:
    help_contract = _load_json(COMMAND_HELP)
    precision = _load_json(PRECISION_COMMAND)
    entries: list[dict[str, Any]] = []
    for row in help_contract.get("builtins", []):
        if isinstance(row, dict):
            entries.append(dict(row))
    for row in precision.get("examples", []):
        if not isinstance(row, dict):
            continue
        canonical = str(row.get("camelHump", "")).strip()
        if not canonical:
            continue
        words = re.findall(r"[a-z]+|[A-Z][a-z0-9]*", canonical)
        shorthand = "".join(word[0] for word in words).lower()
        entries.append(
            {
                "canonicalName": canonical,
                "humanMeaning": row.get("humanMeaning", "registered LuHm precision command"),
                "purpose": row.get("humanMeaning", "registered LuHm precision command"),
                "scope": "command",
                "owner": "lum",
                "aliases": {
                    "kebab": row.get("kebab", ""),
                    "dragonTail": row.get("debugVerb", ""),
                    "vowelRipped": _vowel_rip(canonical),
                    "shorthand": shorthand,
                },
                "authorityBoundary": "inherits normal LuHm command authority",
                "examples": [
                    f"luhm help {canonical}",
                    f"luhm help {row.get('kebab', canonical)}",
                    f"luhm help {row.get('debugVerb', canonical)}",
                ],
            }
        )
    return entries


def _help_payload(name: str = "") -> dict[str, Any]:
    naming = _load_json(NAMING_NAMESPACE)
    help_contract = _load_json(COMMAND_HELP)
    term = str(name or "").strip()
    entries = _help_entries()
    if not term:
        return {
            "schema": "luhmOs.mcpHelp.v1",
            "state": "READY",
            "entryPoints": help_contract.get("entryPoints", []),
            "namespaces": naming.get("namespaces", {}),
            "degradation": naming.get("personCenteredDegradation", {}),
            "commands": [
                {
                    "canonicalName": row.get("canonicalName", "UNKNOWN"),
                    "humanMeaning": row.get("humanMeaning", "UNKNOWN"),
                    "aliases": row.get("aliases", {}),
                }
                for row in entries
            ],
            "mutationAuthority": False,
            "greenAuthority": False,
        }

    matches: list[dict[str, Any]] = []
    folded = term.casefold()
    for row in entries:
        values = [str(row.get("canonicalName", ""))]
        aliases = row.get("aliases", {})
        if isinstance(aliases, dict):
            values.extend(str(value) for value in aliases.values())
        if term in values or any(folded == value.casefold() for value in values):
            matches.append(row)

    if len(matches) == 1:
        return {
            "schema": "luhmOs.mcpHelp.v1",
            "state": "FOUND",
            "query": term,
            "entry": matches[0],
            "mutationAuthority": False,
            "greenAuthority": False,
        }

    return {
        "schema": "luhmOs.mcpHelp.v1",
        "state": "VERIFY",
        "query": term,
        "reason": "ambiguousAlias" if len(matches) > 1 else "unknownAlias",
        "candidates": [row.get("canonicalName", "UNKNOWN") for row in matches],
        "mutationAuthority": False,
        "greenAuthority": False,
    }


def _status_payload() -> dict[str, Any]:
    truth = _load_json(SOURCE_TRUTH)
    enterprise = _load_json(ENTERPRISE_SCOPE)
    deployment = _deployment_payload()
    transport = enterprise.get("transport", {})
    plugin = truth.get("pluginLayer", {})
    android = truth.get("androidLayer", {})
    return {
        "schema": "luhmOs.mcpStatus.v3",
        "sourceLaw": truth.get("sourceLaw", "UNKNOWN"),
        "sourceTruthStatus": truth.get("status", "UNKNOWN"),
        "canonicalRepository": truth.get("canonicalRepository", "UNKNOWN"),
        "pluginStatus": plugin.get("status", "UNKNOWN"),
        "apiSpineStatus": truth.get("providerLayer", {}).get("apiSpine", "UNKNOWN"),
        "trafficController": truth.get("networkLayer", {}).get("role", "UNKNOWN"),
        "androidPhysicalProof": android.get("physicalSamsungProof", "UNKNOWN"),
        "mcpTransport": {
            "productionFqdn": transport.get("productionFqdn", "UNKNOWN"),
            "statelessHttp": bool(transport.get("statelessHttp", False)),
            "sessionOwnsAuthority": bool(transport.get("sessionOwnsAuthority", True)),
            "sessionOwnsSourceTruth": bool(transport.get("sessionOwnsSourceTruth", True)),
        },
        "publicationAuthority": bool(truth.get("publicationAuthority", False)),
        "promotion": bool(truth.get("promotion", False)),
        "greenAuthority": False,
    }

def _roster_payload() -> dict[str, Any]:
    control = _load_json(CONTROL_PLANE)
    return {
        "schema": "luhmOs.mcpRoster.v3",
        "boss": control.get("boss", "UNKNOWN"),
        "humanAuthority": control.get("authority", "UNKNOWN"),
        "maxParallelSupportWorkers": control.get("invariants", {}).get("maxParallelSupportWorkers", "UNKNOWN"),
        "helperRecruitment": control.get("invariants", {}).get("helperRecruitment", "UNKNOWN"),
        "roles": _skill_status(),
        "greenAuthority": False,
    }

def _deployment_payload() -> dict[str, Any]:
    deployment = _load_json(AGENT_DEPLOYMENT)
    control = _load_json(CONTROL_PLANE)
    required = deployment.get("requiredAgents", [])
    roles = {role["agentId"]: role for role in _skill_status()}
    return {
        "schema": "luhmOs.mcpAgentDeployment.v1",
        "status": deployment.get("status", "UNKNOWN"),
        "registeredEverywhere": deployment.get("activationLaw", {}).get("registeredEverywhere", False),
        "residentCore": deployment.get("residentCore", []),
        "lazyAgents": deployment.get("globallyAvailableLazyAgents", []),
        "requiredAgentCount": deployment.get("requiredAgentCount", 0),
        "allRequiredPresent": all(agent_id in control.get("agents", {}) for agent_id in required),
        "allSkillsPresent": all(roles.get(agent_id, {}).get("skillPresent", False) for agent_id in required),
        "surfaces": deployment.get("deploymentSurfaces", {}),
        "liveProviderDeploymentProven": False,
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
    deployment = _deployment_payload()
    enterprise = _load_json(ENTERPRISE_SCOPE)
    spine = _load_json(API_SPINE)
    traffic = _load_json(TRAFFIC_CONTROLLER)
    naming = _load_json(NAMING_NAMESPACE)
    help_contract = _load_json(COMMAND_HELP)
    transport = enterprise.get("transport", {})
    auth = enterprise.get("authentication", {})
    if naming.get("schema") != "luhmOs.namingNamespaceCanon.v1":
        raise RuntimeError("RED_NAMING_NAMESPACE_SCHEMA")
    if help_contract.get("schema") != "luhmOs.commandHelp.v1":
        raise RuntimeError("RED_COMMAND_HELP_SCHEMA")
    if help_contract.get("behavior", {}).get("helpMayMutate") is not False:
        raise RuntimeError("RED_COMMAND_HELP_AUTHORITY_LEAK")
    if help_contract.get("behavior", {}).get("allAliasesResolveToCanonical") is not True:
        raise RuntimeError("RED_COMMAND_HELP_RECOVERY_DRIFT")
    if status["sourceLaw"] != "AI proposes. Policy authorizes. CI proves. Human promotes.":
        raise RuntimeError("RED_SOURCE_LAW_DRIFT")
    if not roster["roles"] or not all(role["skillPresent"] for role in roster["roles"]):
        raise RuntimeError("RED_AGENT_SKILL_MISSING")
    if deployment.get("requiredAgentCount") != len(roster["roles"]):
        raise RuntimeError("RED_AGENT_DEPLOYMENT_COUNT_DRIFT")
    if deployment.get("allRequiredPresent") is not True or deployment.get("allSkillsPresent") is not True:
        raise RuntimeError("RED_AGENT_DEPLOYMENT_ROSTER_DRIFT")
    for kind in ("records", "proof"):
        if kind not in ROUTE_KINDS:
            raise RuntimeError("RED_ROUTE_KIND_MISSING")
    if transport.get("statelessHttp") is not True:
        raise RuntimeError("RED_MCP_STATEFUL_HTTP_DRIFT")
    if transport.get("sessionOwnsAuthority") is not False or transport.get("sessionOwnsSourceTruth") is not False:
        raise RuntimeError("RED_MCP_SESSION_AUTHORITY_DRIFT")
    if auth.get("privateOrWriteToolsRequireOauth21") is not True:
        raise RuntimeError("RED_MCP_AUTH_BOUNDARY_DRIFT")
    if auth.get("oauthImplemented") is not False:
        raise RuntimeError("RED_MCP_OAUTH_STATUS_OVERCLAIM")
    if spine.get("schema") != "luhmOs.apiSpine.v1":
        raise RuntimeError("RED_API_SPINE_SCHEMA")
    if spine.get("routing", {}).get("principle") != "capabilityFirstProviderSecond":
        raise RuntimeError("RED_API_SPINE_ROUTING_DRIFT")
    if spine.get("authorityBoundary", {}).get("trafficControllerMayGrantAuthority") is not False:
        raise RuntimeError("RED_TRAFFIC_CONTROLLER_AUTHORITY_LEAK")
    sidecar = spine.get("renderSidecar", {})
    if sidecar.get("sourceAndCiAuthority") != "github":
        raise RuntimeError("RED_RENDER_SOURCE_AUTHORITY_DRIFT")
    if sidecar.get("entitlementLane") != "STRICT_FREE_TIER":
        raise RuntimeError("RED_RENDER_COST_LANE_DRIFT")
    if sidecar.get("renderMayGrantGreen") is not False:
        raise RuntimeError("RED_RENDER_GREEN_AUTHORITY_LEAK")
    if traffic.get("schema") != "luhmOs.cloudflareAirTrafficController.v1":
        raise RuntimeError("RED_TRAFFIC_CONTROLLER_SCHEMA")
    if not API_SPINE_RESOLVER.is_file():
        raise RuntimeError("RED_API_SPINE_RESOLVER_MISSING")
    if not ESCALATION_RESOLVER.is_file():
        raise RuntimeError("RED_ESCALATION_RESOLVER_MISSING")
    if traffic.get("authorityBoundary", {}).get("aiProvider") is not False:
        raise RuntimeError("RED_CLOUDFLARE_AI_PROVIDER_DRIFT")
    mcp_lane = traffic.get("lanes", {}).get("publicChatPluginMcp", {})
    if mcp_lane.get("currentEndpoint") != "https://luhm-os-harness-green.onrender.com/mcp":
        raise RuntimeError("RED_CURRENT_PLUGIN_ENDPOINT_DRIFT")
    if mcp_lane.get("tunnelForThisLane") is not False:
        raise RuntimeError("RED_MCP_TUNNEL_DRIFT")


@server.tool(annotations=READ_ONLY_INTERNAL)
def luhm_status() -> dict[str, Any]:
    """Read current LuHm source-truth and deployment gates without changing anything."""
    return _status_payload()


def _housekeeping_payload() -> dict[str, Any]:
    policy = _load_json(HOUSEKEEPING)
    snapshot = policy.get("currentProtectiveSnapshot", {})
    base = snapshot.get("sourceRef", "UNKNOWN")
    head = "UNKNOWN"
    count: int | str = "UNKNOWN"
    try:
        head = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            text=True,
            timeout=5,
        ).strip()
        if base not in ("", "UNKNOWN"):
            count = int(subprocess.check_output(
                ["git", "rev-list", "--count", f"{base}..{head}"],
                cwd=ROOT,
                text=True,
                timeout=5,
            ).strip())
    except (subprocess.SubprocessError, OSError, ValueError):
        count = "UNKNOWN"

    window = policy.get("commitWindow", {})
    state = "UNKNOWN"
    if isinstance(count, int):
        if count >= int(window.get("hardStopAtCommits", 50)):
            state = "STOP"
        elif count >= int(window.get("warningAtCommits", 40)):
            state = "WARNING"
        elif count >= int(window.get("automaticCheckpointEveryCommits", 25)):
            state = "CHECKPOINT_DUE"
        else:
            state = "CLEAN"

    return {
        "schema": "luhmOs.mcpHousekeeping.v1",
        "owner": policy.get("owner", "belldandySecretary"),
        "sourceRef": head,
        "checkpointSourceRef": base,
        "commitsSinceCheckpoint": count,
        "state": state,
        "commitWindow": window,
        "automaticMerge": False,
        "automaticDelete": False,
        "mutationAuthority": False,
        "greenAuthority": False,
        "crownStatus": "STOP",
    }


@server.tool(annotations=READ_ONLY_INTERNAL)
def luhm_help(name: str = "") -> dict[str, Any]:
    """Explain LuHm commands, canonical names, and registered aliases without changing state."""
    return _help_payload(name)


@server.tool(annotations=READ_ONLY_INTERNAL)
def luhm_agent_roster() -> dict[str, Any]:
    """List canonical Lum/Oni roles and whether each canonical SKILL.md is present."""
    return _roster_payload()


@server.tool(annotations=READ_ONLY_INTERNAL)
def luhm_agent_deployment() -> dict[str, Any]:
    """Return the canonical system-wide agent deployment registry and surface readiness."""
    return _deployment_payload()


@server.tool(annotations=READ_ONLY_INTERNAL)
def luhm_housekeeping_status() -> dict[str, Any]:
    """Return Belldandy's read-only checkpoint and fifty-commit housekeeping state."""
    return _housekeeping_payload()


@server.tool(annotations=READ_ONLY_INTERNAL)
def luhm_validate_scope(
    taskId: str,
    sourceRef: str,
    scopeId: str,
    candidateSha: str = "",
    proofContext: str = "",
) -> dict[str, Any]:
    """Validate an explicit LuHm request-scope packet without changing state or authority."""
    scope = _scope_payload(taskId, sourceRef, scopeId, candidateSha, proofContext)
    _require_explicit_scope(scope)
    return {"valid": True, "scope": scope, "mutationAuthority": False, "greenAuthority": False}


@server.tool(annotations=READ_ONLY_INTERNAL)
def luhm_route_task(
    kind: str,
    truth_sensitive: bool = False,
    contested: bool = False,
    external_fact: bool = False,
    asset_review: bool = False,
    taskId: str = "UNKNOWN",
    sourceRef: str = "UNKNOWN",
    scopeId: str = "UNKNOWN",
    candidateSha: str = "",
    proofContext: str = "",
) -> dict[str, Any]:
    """Compute the deterministic LuHm task route and bounded worker plan without mutating state."""
    if kind not in ROUTE_KINDS:
        raise ValueError(f"unsupported task kind: {kind}")
    scope = _scope_payload(taskId, sourceRef, scopeId, candidateSha, proofContext)
    if truth_sensitive or kind in TRUTH_SCOPE_KINDS:
        _require_explicit_scope(scope)
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
    result["requestScope"] = scope
    result["mcpMutationAuthority"] = False
    return result


@server.tool(annotations=READ_ONLY_INTERNAL)
def luhm_escalation_plan(
    domain: str,
    tier: int = 0,
    outcome: str = "working",
) -> dict[str, Any]:
    """Resolve LuHm's zero-based escalation tier without mutating state or authority."""
    if domain not in {"default", "corporate", "magic", "art", "technology"}:
        raise ValueError("unsupported escalation domain")
    if tier < 0 or tier > 3:
        raise ValueError("tier must be 0..3")
    if outcome not in {"working", "green", "blocked", "unknown", "conflict"}:
        raise ValueError("unsupported escalation outcome")
    completed = subprocess.run(
        [
            sys.executable,
            str(ESCALATION_RESOLVER),
            "--domain", domain,
            "--tier", str(tier),
            "--outcome", outcome,
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        timeout=10,
        env={"PATH": ""},
    )
    result = json.loads(completed.stdout)
    result["mcpMutationAuthority"] = False
    result["greenAuthority"] = False
    result["crownAuthority"] = False
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
        "unknownIsNotGreen": bool(True),
        "sourceLaw": truth.get("sourceLaw", "UNKNOWN"),
        "greenAuthority": False,
    }


@server.tool(annotations=READ_ONLY_INTERNAL)
def luhm_api_spine() -> dict[str, Any]:
    """Return the stable capability-first provider spine and Cloudflare traffic-controller contract."""
    return _api_spine_payload()


@server.tool(annotations=READ_ONLY_INTERNAL)
def luhm_resolve_capability(capabilityId: str, providerHint: str = "") -> dict[str, Any]:
    """Resolve a capability to eligible provider adapters without executing a provider or changing authority."""
    command = [sys.executable, str(API_SPINE_RESOLVER), "--capability", capabilityId]
    if providerHint:
        command.extend(["--provider", providerHint])
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
    result["providerExecutionProven"] = False
    return result


@server.tool(annotations=READ_ONLY_INTERNAL)
def luhm_transport_contract() -> dict[str, Any]:
    """Return the production/local MCP transport and authentication readiness contract."""
    enterprise = _load_json(ENTERPRISE_SCOPE)
    return {
        "schema": enterprise.get("schema", "UNKNOWN"),
        "transport": enterprise.get("transport", {}),
        "requestScope": enterprise.get("requestScope", {}),
        "authentication": enterprise.get("authentication", {}),
        "operations": enterprise.get("operations", {}),
        "greenAuthority": False,
        "publicationAuthority": False,
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
        {"status": "ok", "service": SERVER_NAME, "version": SERVER_VERSION, "role": os.environ.get("LUHM_RENDER_ROLE", "local-runtime"), "costLane": os.environ.get("LUHM_RENDER_COST_LANE", "local"), "githubPrimary": os.environ.get("LUHM_GITHUB_PRIMARY", "false").lower() == "true"},
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

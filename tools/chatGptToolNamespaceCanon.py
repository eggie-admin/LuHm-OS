#!/usr/bin/env python3
"""Read-only LuHmOS namespace boundary audit and exact alias resolver.

External MCP tools, JSON-RPC methods, resource URIs, package slugs, and
historical receipts are not renamed. Internal machine identifiers are camelHump.
An alias lookup is not a tool invocation or permission grant.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "doctrine/chatGptToolNamespaceCanonV1.json"
NAMING = ROOT / "doctrine/namingNamespaceCanonV1.json"
ARCHITECTURE = ROOT / "doctrine/luHmOSFourLayerArchitectureV1.json"
HARNESS = ROOT / "host/mcp/luhmHarness.py"
SQL = ROOT / "host/api/typedLanesV1.sql"

CANONICAL = re.compile(r"^[a-z][A-Za-z0-9]*$")
DRAGON = re.compile(r"^[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)*$")
KEBAB = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
WIRE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
LAYERS = [
    "machineSqlDragonTail",
    "repositoryKebabNamespace",
    "vowelRippedStrictCamelHump",
    "fullHumanCenteredCamelHump",
]
EXPECTED = {
    "connectionStatus": ("luhmConnectionStatus", "siteOnly", None),
    "openCockpit": ("luhm_open_cockpit", "siteAndRender", "ui://luhm-os/cockpit-v2.html"),
    "openMobileCockpit": ("luhm_open_mobile_cockpit", "siteAndRender", "ui://luhm-os/mobile-cockpit-v1.html"),
    "openAntenna": ("luhm_open_antenna", "siteOnly", None),
    "openGodotPlayer": ("luhm_open_godot_player", "renderOnly", "ui://luhm-os/godot-player-v1.html"),
}
TABLES = (
    "streamEvent", "numericStream", "textStream",
    "booleanStream", "aiManifestStream", "artifactPointer",
)
FIELDS = {
    "machineSqlDragonTail": DRAGON,
    "repositoryKebabNamespace": KEBAB,
    "vowelRippedStrictCamelHump": CANONICAL,
    "fullHumanCenteredCamelHump": CANONICAL,
    "externalWireToolName": WIRE,
}


def audit(contract: dict, naming: dict, architecture: dict, harness: str, sql: str) -> list[str]:
    problems = []
    def check(ok: bool, reason: str) -> None:
        if not ok:
            problems.append(reason)

    check(contract.get("schema") == "luhmOs.chatGptToolNamespaceCanon.v1", "CONTRACT_SCHEMA_DRIFT")
    check(contract.get("status") == "SOURCE_CANDIDATE_ONLY", "SOURCE_PROMOTION_DRIFT")
    check(contract.get("authority") == "Professor", "PROFESSOR_AUTHORITY_DRIFT")
    check(contract.get("sourceLaw") == "AI proposes. Policy authorizes. CI proves. Human promotes.", "SOURCE_LAW_DRIFT")
    check(contract.get("packageIdentity") == architecture.get("packageIdentity") == "LuHmOS", "PACKAGE_CANON_DRIFT")
    check(contract.get("canonicalNamespace") == "doctrine/namingNamespaceCanonV1.json", "NAMING_SOURCE_DRIFT")
    check(contract.get("canonicalArchitecture") == "doctrine/luHmOSFourLayerArchitectureV1.json", "ARCHITECTURE_SOURCE_DRIFT")
    check(contract.get("namespaceOrder") == naming.get("namespaceEscalation", {}).get("orderedLayers") == LAYERS, "FOUR_LAYER_ORDER_DRIFT")
    check(contract.get("installedSiteBinding") == "PRESERVE_EXISTING_PRIVATE_SITE_APP_IDENTITY", "SITE_BINDING_REPLACEMENT_FORBIDDEN")
    check(contract.get("renderSource") == "host/mcp/luhmHarness.py", "RENDER_SOURCE_DRIFT")

    authority = contract.get("authorityBoundary", {})
    check(isinstance(authority, dict) and all(authority.get(key) is False for key in (
        "aliasesMayExecute", "aliasesMayGrantPrivileges", "siteBackendChanged",
        "productionMutationAuthorized", "agentWorkersMayResume",
    )) and authority.get("crownStatus") == "STOP", "AUTHORITY_ESCALATION_FORBIDDEN")
    remote = contract.get("remoteProof", {})
    check(isinstance(remote, dict) and all(remote.get(k) == "UNVERIFIED" for k in (
        "siteToolsList", "siteResourcesRead", "chatGptAndroidUiMount", "remoteDeployment",
    )), "REMOTE_PROOF_NOT_ESTABLISHED")

    sql_boundary = contract.get("sqlBoundary", {})
    check(sql_boundary.get("schema") == "host/api/typedLanesV1.sql"
          and sql_boundary.get("tables") == list(TABLES)
          and sql_boundary.get("migrationAuthorized") is False, "SQL_BOUNDARY_DRIFT")
    for table in TABLES:
        check(bool(re.search(r"\bCREATE TABLE IF NOT EXISTS\s+" + re.escape(table) + r"\s*\(", sql)),
              "MISSING_CAMELHUMP_SQL_TABLE:" + table)

    rows = contract.get("bindings")
    if not isinstance(rows, list):
        return problems + ["BINDINGS_NOT_ARRAY"]
    check(len(rows) == len(EXPECTED), "WIRE_BINDING_COUNT_DRIFT")
    seen: dict[str, str] = {}
    canonical_seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            problems.append("INVALID_BINDING_ROW")
            continue
        canonical = row.get("fullHumanCenteredCamelHump")
        if not isinstance(canonical, str) or not CANONICAL.fullmatch(canonical):
            problems.append("NON_CAMELHUMP_MACHINE_ID")
            continue
        check(canonical not in canonical_seen, "DUPLICATE_CANONICAL_ID:" + canonical)
        canonical_seen.add(canonical)
        for field, pattern in FIELDS.items():
            value = row.get(field)
            if not isinstance(value, str) or not pattern.fullmatch(value):
                problems.append("INVALID_NAMESPACE_FIELD:" + canonical + ":" + field)
                continue
            previous = seen.get(value)
            if previous is not None:
                problems.append("AMBIGUOUS_ALIAS:" + value)
            else:
                seen[value] = canonical
        expected = EXPECTED.get(canonical)
        check(expected is not None, "UNREVIEWED_MACHINE_ID:" + canonical)
        if expected:
            wire, source, uri = expected
            check(row.get("externalWireToolName") == wire, "PUBLISHED_TOOL_NAME_CHANGED:" + canonical)
            check(row.get("sourceLane") == source, "SOURCE_LANE_DRIFT:" + canonical)
            check(row.get("resourceUri") == uri, "RESOURCE_URI_CHANGED:" + canonical)
            if source in ("renderOnly", "siteAndRender"):
                check(bool(re.search(r'\bname\s*=\s*["\x27]' + re.escape(wire) + r'["\x27]', harness)),
                      "RENDER_TOOL_NOT_DECLARED:" + canonical)
                check(uri is not None and uri in harness, "RENDER_RESOURCE_NOT_DECLARED:" + canonical)
        check(isinstance(row.get("humanDisplayName"), str) and bool(row["humanDisplayName"].strip()),
              "HUMAN_LABEL_MISSING:" + canonical)
    check(canonical_seen == set(EXPECTED), "REQUIRED_BINDINGS_MISSING")
    return problems


def resolve(contract: dict, name: str) -> dict | None:
    """Exact alias recovery only; does not invoke any tool or grant authority."""
    for row in contract.get("bindings", []):
        if name in (row.get(key) for key in FIELDS):
            return {
                "canonicalMachineId": row["fullHumanCenteredCamelHump"],
                "externalWireToolName": row["externalWireToolName"],
                "humanDisplayName": row["humanDisplayName"],
                "authorityEffect": "none",
                "runtimeVerified": False,
            }
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resolve", metavar="ALIAS", help="Exact pre-registered alias; never dispatches a tool")
    args = parser.parse_args()
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    naming = json.loads(NAMING.read_text(encoding="utf-8"))
    architecture = json.loads(ARCHITECTURE.read_text(encoding="utf-8"))
    problems = audit(contract, naming, architecture, HARNESS.read_text(encoding="utf-8"), SQL.read_text(encoding="utf-8"))
    result = {
        "schema": "luhmOs.chatGptToolNamespaceAudit.v1",
        "status": "GREEN_SOURCE_ONLY" if not problems else "RED_SOURCE_NAMESPACE",
        "bindingCount": len(contract.get("bindings", [])),
        "problems": problems,
        "siteBackendChanged": False,
        "remoteRuntime": "UNVERIFIED",
        "crownStatus": "STOP",
    }
    if args.resolve:
        result["resolution"] = resolve(contract, args.resolve) if not problems else None
    print(json.dumps(result, indent=2, sort_keys=True))
    return int(bool(problems))


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Offline LuHm GitHub/VM/Netplan/SQL/proxy/vendor-rights alignment auditor.

Reads exact repository candidate files only. Does not discover or connect to
VMs, rewrite network configuration, run migrations, change licenses, query
cloud accounts, open tunnels or authorize agents. GitHub CI is source proof,
not an attested physical machine, deployed app or DNS/VM permission.
"""
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from pathlib import Path
from typing import Any, Mapping

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "doctrine/leanVmForgeAlignmentV1.json"
NETPLAN = ROOT / "config/netplan/90-luhm-vm-dhcp.example.yaml"
SOURCE = re.compile(r"[0-9a-f]{40}\Z")
SAFE_ID = re.compile(r"[a-z][A-Za-z0-9]{0,79}\Z")
LANES = ("source", "execution", "transport", "rights")
TIERS = ("localhost", "privateVm", "trustedProxy", "enterpriseCandidate")
EXPECTED_PROVIDER_IDS = ("oracle", "google", "azure", "aws")
REQUIRED_TABLES = frozenset((
    "streamEvent", "numericStream", "textStream", "booleanStream",
    "aiManifestStream", "artifactPointer"
))


class NoDuplicateSafeLoader(yaml.SafeLoader):
    """Safe YAML with duplicate-key detection for network and Render plans."""


def _strict_mapping(loader: NoDuplicateSafeLoader, node: yaml.MappingNode) -> dict:
    result: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=True)
        if not isinstance(key, (str, int, bool)) or key in result:
            raise ValueError("RED_DUPLICATE_OR_UNSUPPORTED_YAML_KEY")
        result[key] = loader.construct_object(value_node, deep=True)
    return result


NoDuplicateSafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _strict_mapping
)


def parse_yaml(source: str) -> Any:
    if not isinstance(source, str) or len(source) > 150000:
        raise ValueError("RED_YAML_SIZE")
    return yaml.load(source, Loader=NoDuplicateSafeLoader)


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf8"))
    if not isinstance(value, dict):
        raise ValueError("RED_CONTRACT_SHAPE")
    return value


def _safe_anchor(path: Any) -> bool:
    return (isinstance(path, str) and len(path) < 200 and
            not Path(path).is_absolute() and ".." not in Path(path).parts and
            (ROOT / path).is_file())


def _is_off(x: Any) -> bool:
    return x is False or x == "off"


def audit() -> dict[str, Any]:
    policy = _json(CONTRACT)
    issues: list[str] = []
    if policy.get("schema") != "luhmOs.leanVmForgeAlignment.v1":
        issues.append("RED_CONTRACT_SCHEMA")
    if policy.get("canonicalRepo") != "eggie-admin/LuHm-OS" or policy.get("canonicalBranch") != "main":
        issues.append("RED_GITHUB_AUTHORITY")
    if [r.get("id") for r in policy.get("fourLanes", [])] != list(LANES):
        issues.append("RED_LANE_COUNT_OR_ORDER")
    if [r.get("id") for r in policy.get("fourLevels", [])] != list(TIERS):
        issues.append("RED_TIER_COUNT_OR_ORDER")
    anchors = policy.get("sourceAnchors")
    if not isinstance(anchors, list) or len(anchors) < 20 or not all(map(_safe_anchor, anchors)):
        issues.append("RED_SOURCE_ANCHOR_MISSING_OR_UNSAFE")
        anchors = []
    observed: list[dict[str, Any]] = []
    for path in anchors:
        payload = (ROOT / path).read_bytes()
        observed.append({
            "path": path,
            "sha256Hex": hashlib.sha256(payload).hexdigest(),
            "bytes": len(payload),
        })

    license_text = (ROOT / "LICENSE").read_text(encoding="utf8", errors="replace")
    if ("GNU GENERAL PUBLIC LICENSE" not in license_text or
            "Version 3, 29 June 2007" not in license_text or
            policy.get("actualRootLicense") != "GPL-3.0"):
        issues.append("RED_ROOT_LICENSE_MISCLASSIFIED")
    if (policy.get("licenseDecision") !=
            "HOLD_FOR_COMPONENT_BY_COMPONENT_COPYRIGHT_AND_LICENSE_REVIEW"):
        issues.append("RED_AUTO_APACHE_RELICENSE")
    if policy.get("desiredSourceLicense") != "Apache-2.0_FOR_INDEPENDENT_ORIGINAL_MODULES_ONLY":
        issues.append("RED_NEW_MODULE_LICENSE_SCOPE")
    if policy.get("sourceLaw") != (
            "AI proposes. Policy authorizes. Deterministic evidence proves. Professor promotes."):
        issues.append("RED_SOURCE_LAW")

    render = parse_yaml((ROOT / "render.yaml").read_text(encoding="utf8"))
    services = render.get("services", []) if isinstance(render, dict) else []
    by_name = {s.get("name"): s for s in services if isinstance(s, dict)}
    targets = ("luhm-os-harness-green", "luhm-os-godot-harness-green")
    for name in targets:
        service = by_name.get(name)
        if (not isinstance(service, dict) or service.get("type") != "web" or
                service.get("runtime") != "python" or
                service.get("repo") != "https://github.com/eggie-admin/LuHm-OS" or
                service.get("branch") != "main" or
                service.get("plan") != "free" or
                service.get("numInstances") != 1 or
                not _is_off(service.get("autoDeployTrigger"))):
            issues.append("RED_RENDER_CANON_SERVICE_" + name)
    if any(not _is_off(s.get("autoDeployTrigger")) for s in services if isinstance(s, dict)):
        issues.append("RED_RENDER_AUTODEPLOY")
    if len(by_name) != len(services):
        issues.append("RED_RENDER_SERVICE_DUPLICATION")

    netplan = parse_yaml(NETPLAN.read_text(encoding="utf8"))
    network = netplan.get("network", {}) if isinstance(netplan, dict) else {}
    if (not isinstance(network, dict) or network.get("version") != 2 or
            network.get("renderer") != "networkd" or
            set(network) != {"version", "renderer", "ethernets"}):
        issues.append("RED_NETPLAN_SCHEMA")
    nic = network.get("ethernets", {}).get("luhmPrimary", {})
    if (nic.get("match") != {"name": "eth0"} or
            nic.get("dhcp4") is not True or nic.get("dhcp6") is not False or
            nic.get("optional") is not True or
            set(nic) != {"match", "dhcp4", "dhcp6", "optional"}):
        issues.append("RED_NETPLAN_EXAMPLE_DRIFT")
    gate = policy.get("netplan", {})
    if (gate.get("mayRunNetplanApply") is not False or
            gate.get("mayReplaceProviderCloudInitConfig") is not False or
            gate.get("status") != "UNAPPLIED_EXAMPLE_ONLY"):
        issues.append("RED_NETPLAN_EXECUTION_AUTHORITY")

    sql_script = (ROOT / "host/api/typedLanesV1.sql").read_text(encoding="utf8")
    try:
        with sqlite3.connect(":memory:") as conn:
            conn.executescript(sql_script)
            tables = {row[0] for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'")}
            if not REQUIRED_TABLES <= tables:
                issues.append("RED_SQLITE_TYPED_SCHEMA")
            for name in REQUIRED_TABLES:
                row = conn.execute(
                    "SELECT sql FROM sqlite_master WHERE name=?", (name,)).fetchone()
                if row is None or not row[0].strip().endswith("STRICT"):
                    issues.append("RED_SQLITE_STRICT_" + name)
    except sqlite3.DatabaseError:
        issues.append("RED_SQLITE_OFFLINE_DDL")
    mdb = (ROOT / "host/api/luhmMariaDbReceiptV1.sql").read_text(encoding="utf8")
    if ("CREATE TABLE IF NOT EXISTS luhm_update_receipt" not in mdb or
            "ENGINE=InnoDB" not in mdb or
            policy.get("sql", {}).get("noProductionDdl") is not True):
        issues.append("RED_MARIADB_POLICY")
    storage = _json(ROOT / "doctrine/storageTopologyV1.json")
    if (storage.get("roles", {}).get("github", {}).get("canonicalSourceAuthority") is not True or
            storage.get("roles", {}).get("googleDrive", {}).get("canonicalBinaryStorage") is not True or
            storage.get("rules", {}).get("databaseMayStoreCanonicalBinary") is not False):
        issues.append("RED_STORAGE_AUTHORITY")

    proxy = policy.get("proxy", {})
    edge = _json(ROOT / "doctrine/cloudflareEdgeHardeningV1.json")
    spine = _json(ROOT / "doctrine/networkSpineV1.json")
    expected_mcp = "https://luhm-os-harness-green.onrender.com/mcp"
    actual = edge.get("lanes", {}).get("chatGptMcp", {}).get("activeOrigin")
    if (proxy.get("currentMcpOrigin") != expected_mcp or actual != expected_mcp or
            spine.get("identityChain", {}).get("proxyLane", {}).get("mcp") !=
            "dnsOnlyDirectRenderManagedTlsUntilStreamingProof"):
        issues.append("RED_MCP_PROXY_SOURCE_DRIFT")
    forbidden_false = (
        "noAutomaticCloudflareProxyOnMcp", "forbidPublicAdmin", "forbidPublicSql",
        "forbidPublicGpu", "forbidBrowserSecrets", "neverCacheMcpOrAuth",
        "noLiveProxyMutation", "avoidAddingApacheHttpdAndNginxTogether"
    )
    if any(proxy.get(k) is not True for k in forbidden_false):
        issues.append("RED_PROXY_PRIVILEGE_OR_CACHE")
    if (proxy.get("privateSqlPorts") != [3306, 5432] or
            proxy.get("privateAdminRoutePrefix") != "/v1/"):
        issues.append("RED_PROXY_PRIVATE_PORTS")

    q = _json(ROOT / "doctrine/companyWideOperationalQuarantineV1.json")
    if q.get("state") != "QUARANTINED" or q.get("activeTaskWorkersAllowed") is not False:
        issues.append("RED_UNEXPECTED_WORKER_QUARANTINE")

    offers = policy.get("freeVmResearch", {})
    providers = offers.get("providers", [])
    if ([p.get("id") for p in providers] != list(EXPECTED_PROVIDER_IDS) or
            any(p.get("gpuFree") is not False or
                p.get("requiresAccountReview") is not True for p in providers) or
            offers.get("gpuComputeForVideoFreeIncluded") is not False or
            offers.get("guaranteesZeroCost") is not False):
        issues.append("RED_FREE_TIER_UNVERIFIED_GPU_OR_COST")

    proof = policy.get("machineProof", {})
    if (proof.get("noAutoMerge") is not True or proof.get("noAutoDeploy") is not True
            or proof.get("noNewSpend") is not True or
            proof.get("companyAgentsQuarantined") is not True or
            proof.get("sourceOnlyCanGrantCrown") is not False or
            policy.get("crownStatus") != "STOP"):
        issues.append("RED_OWNER_PROMOTION_AUTHORITY")

    combined = json.dumps(observed, sort_keys=True, separators=(",", ":")).encode("utf8")
    return {
        "schema": "luhmOs.leanVmForgeAudit.v1",
        "status": "SOURCE_CONSISTENT_NOT_RUNTIME_PROVEN" if not issues else "RED_SOURCE_DRIFT",
        "sourceConsistent": not issues,
        "issues": sorted(set(issues)),
        "sourceFileCount": len(observed),
        "sourceFileDigestSha256": hashlib.sha256(combined).hexdigest(),
        "verifiedSqliteTables": sorted(REQUIRED_TABLES) if "RED_SQLITE_OFFLINE_DDL" not in issues else [],
        "renderCanonicalServiceCount": len(targets),
        "providerFreeTierCandidates": len(providers),
        "rootLicense": "GPL-3.0" if "RED_ROOT_LICENSE_MISCLASSIFIED" not in issues else "UNVERIFIED",
        "apache2MigrationAuthorized": False,
        "netplanApplied": False, "cloudAccountsChecked": False,
        "physicalVmProven": False, "proxyReconfigured": False,
        "databaseMigrationApplied": False, "activeAgents": 0,
        "networkCalls": 0, "costUsd": 0,
        "greenAuthority": False, "crownAuthority": False,
    }


def plan_vm(task_id: str, source_ref: str, scope_id: str, vm_id: str,
            provider_id: str) -> dict[str, Any]:
    for label, value in (("taskId", task_id), ("scopeId", scope_id), ("vmId", vm_id)):
        if type(value) is not str or SAFE_ID.fullmatch(value) is None:
            raise ValueError("invalid " + label)
    if type(source_ref) is not str or SOURCE.fullmatch(source_ref) is None:
        raise ValueError("sourceRef must be exact lowercase 40-hex repository SHA")
    if provider_id not in EXPECTED_PROVIDER_IDS:
        raise ValueError("provider not on researched VM list")
    state = audit()
    if state["issues"]:
        return {
            "state": "STOP_SOURCE_DRIFT",
            "issues": state["issues"],
            "mutationAllowed": False, "crownAuthority": False,
        }
    provider = next(x for x in _json(CONTRACT)["freeVmResearch"]["providers"]
                    if x["id"] == provider_id)
    return {
        "schema": "luhmOs.leanVmForgePlan.v1",
        "taskId": task_id, "sourceRef": source_ref, "scopeId": scope_id,
        "vmId": vm_id, "candidateProvider": provider_id,
        "offerKind": provider["kind"],
        "state": "HOLD_EXTERNAL_VM_ACCOUNT_AND_IDENTITY",
        "sourceRefFormatVerified": True,
        "sourceRefObservedAsCurrentGitHubHead": False,
        "providerOfferCheckedAgainstActualAccount": False,
        "virtualMachineConnected": False,
        "netplanInterfaceObserved": False,
        "proxyAuthenticatedRemotely": False,
        "costEntitlementProven": False,
        "licenseMigrationApproved": False,
        "requiredProof": [
            "exactCurrentSourceAndCi", "providerAccountAndBillingGuard",
            "registeredVmIdentity", "consoleRecoveryAndCloudInitOwnership",
            "observedNetworkInterface", "privateTransportIdentityAndTls",
            "leastPrivilegePolicyAndRollback", "explicitProfessorApprovalForMutation"
        ],
        "networkCalls": 0, "vmActionsExecuted": 0,
        "mutationAllowed": False, "greenAuthority": False, "crownAuthority": False,
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2))

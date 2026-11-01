#!/usr/bin/env python3
"""LuHm remote WMS/VM control-plane planner.

Never connects to a remote endpoint, performs guest actions, or starts workers.
This is an explicit no-network, fail-closed candidate adapter for the ChatGPT
MCP surface. WMS vendor and actual machine identities remain unresolved.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "doctrine" / "remoteWmsMachineBridgeV1.json"
QUARANTINE = ROOT / "doctrine" / "companyWideOperationalQuarantineV1.json"
SOURCE_TRUTH = ROOT / "doctrine" / "currentSourceTruthV3.json"
SPINE = ROOT / "doctrine" / "apiSpineV1.json"
SAFE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,79}\Z")
SOURCE_SHA = re.compile(r"[0-9a-f]{40}\Z")
SAFE_SCOPE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:/-]{0,159}\Z")


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("RED_WMS_CONTRACT_FORMAT")
    return value


def _contracts() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    contract, quarantine, truth = _load(CONTRACT), _load(QUARANTINE), _load(SOURCE_TRUTH)
    if contract.get("schema") != "luhmOs.remoteWmsMachineBridge.v1":
        raise RuntimeError("RED_WMS_CONTRACT_SCHEMA")
    if quarantine.get("schema") != "luhmOs.companyWideOperationalQuarantine.v1":
        raise RuntimeError("RED_WMS_QUARANTINE_SCHEMA")
    if truth.get("schema") != "luhmOs.currentSourceTruth.v3":
        raise RuntimeError("RED_WMS_SOURCE_SCHEMA")
    if _load(SPINE).get("schema") != "luhmOs.apiSpine.v1":
        raise RuntimeError("RED_WMS_API_SPINE_SCHEMA")
    missing = [name for name in contract.get("sourceAnchors", [])
               if not (ROOT / name).is_file()]
    if missing:
        raise RuntimeError("RED_WMS_CANON_ANCHOR_MISSING")
    return contract, quarantine, truth


def _validated_identifiers(task_id: str, source_ref: str, scope_id: str,
                           machine_id: str, operation: str) -> None:
    if not isinstance(task_id, str) or SAFE_ID.fullmatch(task_id) is None:
        raise ValueError("taskId must be a bounded opaque identifier")
    if not isinstance(source_ref, str) or SOURCE_SHA.fullmatch(source_ref) is None:
        raise ValueError("sourceRef must be an exact lowercase 40-character SHA")
    if not isinstance(scope_id, str) or SAFE_SCOPE.fullmatch(scope_id) is None:
        raise ValueError("scopeId must be an explicit bounded identifier")
    if not isinstance(machine_id, str) or SAFE_ID.fullmatch(machine_id) is None:
        raise ValueError("machineId must be a registered opaque identifier")
    if not isinstance(operation, str) or SAFE_ID.fullmatch(operation) is None:
        raise ValueError("operation must be an allowlisted capability")


def status() -> dict[str, Any]:
    contract, hold, truth = _contracts()
    # A ChatGPT tool response is not an authenticated remote-host inventory.
    wms = contract["wms"]
    return {
        "schema": "luhmOs.remoteWmsStatus.v1",
        "state": "CANDIDATE_PLANNER_ONLY",
        "wmsVendor": wms["vendor"],
        "wmsProtocol": wms["protocol"],
        "configuredMachineCount": 0,
        "remoteConnectivityVerified": False,
        "remoteExecutionProven": False,
        "companyQuarantined": hold.get("state") != "RELEASED",
        "sourcePromotionAuthorized": truth.get("promotion") is True,
        "readOnlyPlanningAvailable": True,
        "supportedPlanningOperations": contract["allowedPlanningOperations"],
        "liveRemoteOpsAvailable": False,
        "secretsExposed": False,
        "greenAuthority": False,
        "crownAuthority": False,
    }


def plan(task_id: str, source_ref: str, scope_id: str, machine_id: str,
         operation: str = "status",
         *, env: Mapping[str, str] | None = None,
         registered_machine_ids: frozenset[str] | None = None) -> dict[str, Any]:
    """Plan only. An injected test registry never enables live execution."""
    _validated_identifiers(task_id, source_ref, scope_id, machine_id, operation)
    contract, hold, truth = _contracts()
    if operation not in contract["allowedPlanningOperations"]:
        raise ValueError("requested operation is not on the Canon capability allowlist")
    env = os.environ if env is None else env
    registry = frozenset() if registered_machine_ids is None else registered_machine_ids
    blockers: list[str] = []
    # Inventory/capability discovery is manager-level; everything else needs a VM.
    manager_ops = frozenset(("inventory", "capabilities"))
    if operation in manager_ops:
        if machine_id != "manager":
            blockers.append("MANAGER_ID_REQUIRED")
    elif machine_id not in registry:
        blockers.append("MACHINE_UNREGISTERED")
    if hold.get("state") != "RELEASED" or hold.get("activeTaskWorkersAllowed") is not True:
        blockers.append("COMPANY_QUARANTINE")
    if contract["wms"]["vendor"] == "UNRESOLVED":
        blockers.append("WMS_VENDOR_UNRESOLVED")
    if contract["wms"]["remoteConnectivityVerified"] is not True:
        blockers.append("REMOTE_CONNECTION_UNVERIFIED")
    if not env.get("LUHM_WMS_SOURCE_REF"):
        blockers.append("SOURCE_RECEIPT_MISSING")
    elif env["LUHM_WMS_SOURCE_REF"] != source_ref:
        blockers.append("SOURCE_RECEIPT_MISMATCH")
    if operation in contract["mutationOnlyAsPlans"]:
        blockers.append("REMOTE_WRITE_NOT_AUTHORIZED")
    # Deliberately no URL, request body, shell command or auth token in the plan.
    return {
        "schema": "luhmOs.remoteWmsPlan.v1",
        "taskId": task_id,
        "sourceRef": source_ref,
        "scopeId": scope_id,
        "machineId": machine_id,
        "operation": operation,
        "capabilityId": "remoteWms." + operation,
        "status": "BLOCKED_NOT_PROVEN" if blockers else "PLAN_ONLY",
        "blockingConditions": blockers,
        "requiredProof": contract["ownerNextProof"],
        "escalationTier": 0,
        "fourBeat": contract["fourBeat"],
        "machineConnectionVerified": False,
        "remoteExecutionProven": False,
        "networkCalls": 0,
        "estimatedCostUsd": None,
        "mutationAuthority": False,
        "greenAuthority": False,
        "crownAuthority": False,
    }


if __name__ == "__main__":
    print(json.dumps(status(), indent=2))

#!/usr/bin/env python3
"""No-network source and policy auditor for LuHm's 4x4 headless VM matrix.

The 4x4 is a *planning* matrix. It never detects actual Raspberry Pi hardware,
runs a hypervisor, probes a camera, downloads content, or invokes an agent.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "doctrine" / "headlessUniversalVmMatrixV1.json"
QUARANTINE = ROOT / "doctrine" / "companyWideOperationalQuarantineV1.json"
EXPECTED_LANES = ("foundation", "virtualization", "emulationMedia", "captureMotion")
STAGES = ("R1", "R2", "R3", "R4")
NAME = re.compile(r"[a-z][A-Za-z0-9]{0,79}\Z")
SOURCE = re.compile(r"[0-9a-f]{40}\Z")
URL = re.compile(r"https://[A-Za-z0-9.-]+/(?:[^\s]*)\Z")


def load() -> dict[str, Any]:
    value = json.loads(MATRIX.read_text(encoding="utf8"))
    if not isinstance(value, dict):
        raise ValueError("RED_4X4_SCHEMA_SHAPE")
    return value


def audit_schema(canon: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Source schema validation is not a runtime/hardware proof."""
    data = load() if canon is None else canon
    problems: list[str] = []
    if data.get("schema") != "luhmOs.headlessUniversalVmMatrix.v1":
        problems.append("RED_SCHEMA")
    if data.get("status") != "PROPOSED_READ_ONLY_CANDIDATE":
        problems.append("RED_CANDIDATE_LANE")
    dimensions = data.get("dimensions") or {}
    if (dimensions.get("lanes"), dimensions.get("cells"), dimensions.get("stages")) != (
        4, 16, list(STAGES)
    ):
        problems.append("RED_DIMENSIONS")
    rows = data.get("matrix")
    if not isinstance(rows, list) or len(rows) != 4:
        problems.append("RED_ROW_COUNT")
        rows = []
    if tuple(row.get("lane") for row in rows if isinstance(row, dict)) != EXPECTED_LANES:
        problems.append("RED_LANE_ORDER")
    cell_ids: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            problems.append("RED_ROW_SHAPE")
            continue
        cells = row.get("stages")
        if not isinstance(cells, list) or len(cells) != 4:
            problems.append("RED_STAGE_COUNT")
            continue
        if [cell.get("stage") for cell in cells if isinstance(cell, dict)] != list(STAGES):
            problems.append("RED_STAGE_ORDER")
        for idx, cell in enumerate(cells):
            if not isinstance(cell, dict):
                problems.append("RED_CELL_SHAPE")
                continue
            cid = cell.get("id")
            if not isinstance(cid, str) or cid in cell_ids:
                problems.append("RED_DUPLICATE_CELL")
            cell_ids.add(cid)
            if (cid != row["lane"] + STAGES[idx] or
                cell.get("tier") != idx or
                cell.get("localProofState") != "UNKNOWN" or
                cell.get("liveExecution") is not False or
                not isinstance(cell.get("requiredEvidence"), list) or
                len(cell["requiredEvidence"]) < 3):
                problems.append("RED_CELL_PROOF_BOUNDARY")
    for path in data.get("sourceAnchors", []):
        if not isinstance(path, str) or path.startswith("/") or ".." in Path(path).parts or not (ROOT / path).is_file():
            problems.append("RED_CANON_ANCHOR")
    sources = data.get("sourceReferences") or []
    if len(sources) < 10 or any(not isinstance(r, dict) or
                                      not isinstance(r.get("url"), str) or
                                      not URL.fullmatch(r["url"]) for r in sources):
        problems.append("RED_UPSTREAM_REFERENCES")
    q = json.loads(QUARANTINE.read_text(encoding="utf8"))
    if q.get("state") != "QUARANTINED" or q.get("activeTaskWorkersAllowed") is not False:
        # Changes to the hold require their own authorization and source review.
        problems.append("RED_UNEXPECTED_QUARANTINE_STATE")
    if data.get("security", {}).get("vmProvisionAllowed") is not False:
        problems.append("RED_VM_PROVISION_AUTHORITY")
    if data.get("security", {}).get("cameraOpenAllowed") is not False:
        problems.append("RED_CAMERA_AUTHORITY")
    if data.get("security", {}).get("romOrFirmwareDistributionAllowed") is not False:
        problems.append("RED_ROM_FIRMWARE_RIGHTS")
    if data.get("crownStatus") != "STOP":
        problems.append("RED_CROWN_AUTHORITY")
    return {
        "schema": "luhmOs.headless4x4Audit.v1",
        "sourceConsistent": not problems,
        "observedCandidateCells": len(cell_ids),
        "issues": sorted(set(problems)),
        "physicalMachineVerified": False,
        "guestRunningVerified": False,
        "sourceCodeProvesHardware": False,
        "remoteNetworkCalls": 0,
        "greenAuthority": False,
        "crownAuthority": False,
    }


def plan(task_id: str, source_ref: str, scope_id: str, lane: str) -> dict[str, Any]:
    for value in (task_id, scope_id):
        if not isinstance(value, str) or NAME.fullmatch(value) is None:
            raise ValueError("bounded camelHump task/scope required")
    if not isinstance(source_ref, str) or SOURCE.fullmatch(source_ref) is None:
        raise ValueError("exact lowercase forty-digit source SHA required")
    if lane not in EXPECTED_LANES:
        raise ValueError("unknown capability lane")
    verification = audit_schema()
    if not verification["sourceConsistent"]:
        return {
            "status": "STOP_SOURCE_DRIFT", "taskId": task_id,
            "sourceRef": source_ref, "scopeId": scope_id, "lane": lane,
            "issues": verification["issues"], "greenAuthority": False,
            "crownAuthority": False,
        }
    row = next(r for r in load()["matrix"] if r["lane"] == lane)
    stages = row["stages"]
    return {
        "schema": "luhmOs.headless4x4Plan.v1",
        "taskId": task_id, "sourceRef": source_ref, "scopeId": scope_id,
        "lane": lane, "state": "HOLD_R1_EXTERNAL_PROOF",
        "firstUnverifiedGate": "R1",
        "stagePlan": [
            {"stage": s["stage"], "tier": s["tier"], "objective": s["objective"],
             "requiredEvidence": s["requiredEvidence"],
             "verifiedMachineState": "UNKNOWN"}
            for s in stages
        ],
        "maxPasses": 4,
        "actualPassesExecuted": 0,
        "companyAgentsQuarantined": True,
        "physicalRuntimeProven": False, "vmConnected": False,
        "mediaRightsProven": False, "userCameraConsentProven": False,
        "liveWorkPerformed": False,
        "greenAuthority": False, "crownAuthority": False,
    }


def simulate_continue_on_green(states: tuple[str, ...]) -> dict[str, Any]:
    """Pure test-only dry-run for the conditional loop; NEVER consumes real receipts."""
    if not isinstance(states, tuple) or len(states) > 4:
        raise ValueError("four or fewer synthetic states required")
    seen: list[str] = []
    stop = "HOLD"
    for i, step in enumerate(STAGES):
        result = states[i] if i < len(states) else "UNKNOWN"
        if result not in ("PASS", "HOLD", "STOP", "UNKNOWN"):
            raise ValueError("invalid synthetic test state")
        seen.append(step)
        if result != "PASS":
            stop = "STOP" if result == "STOP" else "HOLD"
            break
    else:
        stop = "HOLD_FOR_PROFESSOR"
    return {
        "simulated": True, "passesVisited": seen, "state": stop,
        "realProofAccepted": False, "liveWorkerExecution": False,
        "greenAuthority": False, "crownAuthority": False,
    }


if __name__ == "__main__":
    print(json.dumps(audit_schema(), indent=2))

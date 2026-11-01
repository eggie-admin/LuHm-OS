#!/usr/bin/env python3
"""Deterministic Lum + mini-agent two-lane evidence planning, no active agents.

This module reuses the canonical typed SQLite stub and eight-note doctrine.
It may record two *logical* checkpoint labels in private SQLite; it never runs
LLMs, invokes an actual mini-agent, talks to a VM, or calls paid APIs.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sqlite3
import threading
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "doctrine" / "lumTwoLaneFastApiOrchestrationV1.json"
EIGHTH = ROOT / "doctrine" / "eighthNoteAgentScopeV1.json"
QUARANTINE = ROOT / "doctrine" / "companyWideOperationalQuarantineV1.json"
TRUTH = ROOT / "doctrine" / "currentSourceTruthV3.json"
ROSTER = ROOT / "doctrine" / "agentSystemDeploymentV1.json"
TYPED = ROOT / "tools" / "typedSqlStub.py"
SHA256 = re.compile(r"^[0-9a-f]{64}$")
MAX_GOAL_CHARS = 2048


def _load(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError("RED_ORCHESTRATION_CONTRACT_SHAPE")
    return data


def _sql_stub() -> Any:
    spec = importlib.util.spec_from_file_location("typedSqlStub", TYPED)
    if spec is None or spec.loader is None:
        raise RuntimeError("RED_CANON_SQL_MISSING")
    stub = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(stub)
    return stub


def _assert_contract() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    contract, eighth, quarantine = _load(CONTRACT), _load(EIGHTH), _load(QUARANTINE)
    if contract.get("schema") != "luhmOs.lumTwoLaneFastApiOrchestration.v1":
        raise RuntimeError("RED_ORCHESTRATION_SCHEMA")
    if eighth.get("schema") != "luhmOs.eighthNoteAgentScope.v1":
        raise RuntimeError("RED_EIGHTH_NOTE_SCHEMA")
    if quarantine.get("schema") != "luhmOs.companyWideOperationalQuarantine.v1":
        raise RuntimeError("RED_QUARANTINE_SCHEMA")
    if _load(TRUTH).get("schema") != "luhmOs.currentSourceTruth.v3":
        raise RuntimeError("RED_SOURCE_SCHEMA")
    agents = _load(ROSTER).get("requiredAgents", [])
    if not all(lane["roleLabel"] in agents for lane in contract["logicalLanes"]):
        raise RuntimeError("RED_UNKNOWN_CANON_ROLE")
    if [n["name"] for n in eighth["notes"]] != contract["workflow"]["eighthNoteSequence"]:
        raise RuntimeError("RED_EIGHTH_NOTE_DRIFT")
    if contract["workflow"]["activeAgentThreads"] != 0:
        raise RuntimeError("RED_UNAUTHORIZED_AGENT_THREADS")
    return contract, eighth, quarantine


def _validate(task_id: str, source_ref: str, scope_id: str, goal: str, tier: int) -> None:
    stub = _sql_stub()
    for value in (task_id, scope_id):
        stub.boundedName(value)
    if type(source_ref) is not str or not stub.SHA.fullmatch(source_ref):
        raise ValueError("exact 40-character Git commit SHA required")
    if type(goal) is not str or not 1 <= len(goal.strip()) <= MAX_GOAL_CHARS:
        raise ValueError("goal must be nonempty and at most 2048 characters")
    if type(tier) is not int or not 0 <= tier <= 3:
        raise ValueError("escalation tier outside Canon 0..3")


def plan(task_id: str, source_ref: str, scope_id: str,
         goal: str, tier: int = 0) -> dict[str, Any]:
    _validate(task_id, source_ref, scope_id, goal, tier)
    contract, eighth, hold = _assert_contract()
    # Stable compact canonical encoding, avoiding raw goal in receipts or SQL.
    data = json.dumps({
        "taskId": task_id, "sourceRef": source_ref, "scopeId": scope_id,
        "goal": goal.strip(), "tier": tier,
    }, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    request_sha256 = hashlib.sha256(data).hexdigest()
    blockers = ["ACTIVE_AGENTS_QUARANTINED"] if (
        hold.get("state") != "RELEASED" or
        hold.get("activeTaskWorkersAllowed") is not True
    ) else []
    blockers.append("PROVIDER_RUNTIME_UNVERIFIED")
    return {
        "schema": "luhmOs.lumTwoLanePlan.v1",
        "taskId": task_id,
        "sourceRef": source_ref,
        "scopeId": scope_id,
        "requestSha256": request_sha256,
        "sourceRefHex": source_ref,
        "escalationTier": tier,
        "status": "PLAN_ONLY",
        "blockingConditions": blockers,
        "logicalLanes": [
            {"laneId": lane["id"], "roleLabel": lane["roleLabel"],
             "eighthNote": lane["eighthNote"], "state": "NO_AGENT_EXECUTION"}
            for lane in contract["logicalLanes"]
        ],
        "eighthNotes": [item["name"] for item in eighth["notes"]],
        "fourBeat": contract["workflow"]["beats"],
        "networkCalls": 0,
        "runningAgentThreads": 0,
        "actualAgentExecutionProven": False,
        "sourceCommitVerifiedAgainstGitHub": False,
        "mutationAuthority": False,
        "greenAuthority": False,
        "crownAuthority": False,
    }


def _event_id(plan_data: dict[str, Any], lane_id: str) -> str:
    material = "|".join((
        plan_data["taskId"], plan_data["sourceRef"], plan_data["scopeId"], lane_id,
    )).encode("utf-8")
    return "evt" + hashlib.sha256(material).hexdigest()[:32]


class CheckpointLedger:
    """Private local SQLite receipt ledger, in-memory unless host passes a path."""

    def __init__(self, path: str = ":memory:") -> None:
        if type(path) is not str or not path or path.startswith("file:"):
            raise ValueError("SQLite URI mode forbidden")
        self._lock = threading.RLock()
        self._db: sqlite3.Connection = _sql_stub().openStub(path)
        self.persistent = path != ":memory:"

    def close(self) -> None:
        with self._lock:
            self._db.close()

    def checkpoint(self, task_id: str, source_ref: str, scope_id: str,
                   goal: str, tier: int = 0) -> dict[str, Any]:
        packet = plan(task_id, source_ref, scope_id, goal, tier)
        stub = _sql_stub()
        lanes = packet["logicalLanes"]
        with self._lock:
            self._db.execute("BEGIN IMMEDIATE")
            try:
                existing = [self._db.execute(
                    "SELECT se.eventId, ts.textValue FROM streamEvent se "
                    "JOIN textStream ts ON ts.eventId=se.eventId "
                    "WHERE se.eventId=? AND ts.fieldName='requestHash'",
                    (_event_id(packet, lane["laneId"]),)
                ).fetchone() for lane in lanes]
                if any(row is not None for row in existing):
                    if not all(row is not None and row["textValue"] == packet["requestSha256"]
                               for row in existing):
                        raise ValueError("RED_TASK_IDENTITY_REPLAY_CONFLICT")
                    self._db.commit()
                    return {**packet, "checkpoint": "IDEMPOTENT_REPLAY",
                            "eventsRecorded": 2, "sqlLedger": "PRIVATE_LOCAL_ONLY"}
                base = int(self._db.execute(
                    "SELECT COALESCE(MAX(sequenceId),0) FROM streamEvent"
                ).fetchone()[0])
                for offset, lane in enumerate(lanes, start=1):
                    event_id = _event_id(packet, lane["laneId"])
                    stub.addEvent(self._db, event_id, task_id, source_ref, scope_id,
                                  lane["roleLabel"], base + offset, lane["eighthNote"],
                                  "2026-11-01T00:00:00Z")
                    # The timestamp is replaced by an observed current UTC clock below.
                    stub.putText(self._db, event_id, "requestHash", packet["requestSha256"])
                    stub.putText(self._db, event_id, "laneLabel", lane["laneId"])
                    stub.putBoolean(self._db, event_id, "workerActive", False)
                    stub.putBoolean(self._db, event_id, "sourceVerified", None)
                    stub.putNumeric(self._db, event_id, "escalationTier", "integer", tier)
                    stub.putManifest(self._db, event_id, {
                        "schema": "luhmOs.aiTaskManifest.v2",
                        "taskId": task_id, "sourceRef": source_ref, "scopeId": scope_id,
                        "status": "PLAN_ONLY",
                        "providerId": "deterministicLocal",
                        "capabilityId": "scopeReview",
                        "inputRefs": [packet["requestSha256"]],
                        "requiredOutputSchema": "luhmOs.lumTwoLanePlan.v1",
                        "budget": {"maxRequests": 0, "maxParallel": 0, "maxPasses": 1},
                        "stopConditions": packet["blockingConditions"],
                        "authority": {"mutation": False, "green": False, "crown": False},
                    })
                self._db.commit()
            except Exception:
                self._db.rollback()
                raise
        return {**packet, "checkpoint": "TWO_PLANNING_EVENTS_ATOMIC",
                "eventsRecorded": 2, "sqlLedger": "PRIVATE_LOCAL_ONLY"}

    def events(self, task_id: str, source_ref: str, scope_id: str,
               limit: int = 30) -> dict[str, Any]:
        _validate(task_id, source_ref, scope_id, "ledgerQuery", 0)
        if type(limit) is not int or not 1 <= limit <= 100:
            raise ValueError("event limit out of bounds")
        with self._lock:
            records = _sql_stub().orderedEvents(
                self._db, task_id, source_ref, scope_id, limit)
        return {
            "schema": "luhmOs.lumTwoLaneLedger.v1",
            "taskId": task_id, "sourceRef": source_ref, "scopeId": scope_id,
            "records": records,
            "activeAgentThreads": 0,
            "greenAuthority": False,
            "crownAuthority": False,
        }


if __name__ == "__main__":
    print(json.dumps(plan("demoTask", "a" * 40, "localScope",
                          "Inspect candidate Canon"), indent=2))

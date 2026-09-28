#!/usr/bin/env python3
"""Deterministic Oni pet activity snapshot builder.

This module mirrors observed LuHm task envelopes and receipts into a tiny UI-safe
snapshot. It does not run agents, poll providers, or imply hidden background work.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

ALLOWED_PHASES = frozenset({
    "INTAKE", "RESOLVE", "ROUTE", "OBSERVE", "MUTATE", "VERIFY",
    "ADJUDICATE", "REPORT", "CROWN_STOP",
})
ALLOWED_STATES = frozenset({
    "IDLE", "QUEUED", "ACTIVE", "WAITING", "VERIFYING", "SUCCESS", "ERROR", "PARKED",
})
ROLE_IDS = frozenset({
    "lum", "fumi", "drNao", "tetsu", "kaji", "kiri", "momo", "shiori",
    "kugi", "yume", "koe", "sumi",
})
MAX_SUPPORT = 3


@dataclass(frozen=True)
class WorkerActivity:
    id: str
    state: str
    label: str = ""
    evidence_ref: str = ""

    def normalized(self) -> "WorkerActivity":
        worker_id = self.id.strip()
        state = self.state.strip().upper()
        if worker_id not in ROLE_IDS:
            raise ValueError(f"unknown Oni role: {worker_id}")
        if state not in ALLOWED_STATES:
            raise ValueError(f"unknown Oni activity state: {state}")
        return WorkerActivity(
            worker_id,
            state,
            _safe_text(self.label, 54),
            _safe_text(self.evidence_ref, 120),
        )


def _safe_text(value: object, limit: int) -> str:
    text = str(value or "").replace("<", "").replace(">", "").strip()
    return text[:limit]


def build_snapshot(
    *,
    task_id: str,
    source_ref: str,
    phase: str,
    workers: Iterable[WorkerActivity],
) -> dict:
    task_id = _safe_text(task_id, 96)
    source_ref = _safe_text(source_ref or "UNKNOWN", 96) or "UNKNOWN"
    phase = _safe_text(phase, 24).upper()
    if not task_id:
        raise ValueError("taskId required")
    if phase not in ALLOWED_PHASES:
        raise ValueError(f"unknown Lum phase: {phase}")

    normalized = [worker.normalized() for worker in workers]
    ids = [worker.id for worker in normalized]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate Oni worker activity")

    if "lum" not in ids:
        lum_state = "WAITING" if phase == "CROWN_STOP" else ("IDLE" if phase == "REPORT" else "ACTIVE")
        normalized.insert(0, WorkerActivity("lum", lum_state, "orchestrating"))

    support = [w for w in normalized if w.id != "lum" and w.state != "PARKED"]
    if len(support) > MAX_SUPPORT:
        raise ValueError("visible support-worker cap exceeded")

    return {
        "schema": "luhm-os.oni-pet-activity-snapshot.v2",
        "taskId": task_id,
        "sourceRef": source_ref,
        "phase": phase,
        "workers": [
            {
                "id": worker.id,
                "state": worker.state,
                "label": worker.label,
                **({"evidenceRef": worker.evidence_ref} if worker.evidence_ref else {}),
            }
            for worker in normalized
        ],
        "backgroundAutonomy": False,
    }


def from_task_envelope(envelope: Mapping[str, object], worker_states: Mapping[str, str]) -> dict:
    """Build a snapshot from an already-observed V2 task envelope.

    `worker_states` must come from the orchestrator/tool layer. Missing workers are not
    guessed into existence. Unknown status is rendered as WAITING rather than success.
    """
    task_id = _safe_text(envelope.get("taskId"), 96)
    source_ref = _safe_text(envelope.get("sourceRef") or "UNKNOWN", 96)
    phase = _safe_text(envelope.get("phase") or "OBSERVE", 24).upper()
    workers = []
    for worker_id, state in worker_states.items():
        if worker_id == "lum":
            workers.append(WorkerActivity("lum", state, "orchestrating"))
        else:
            workers.append(WorkerActivity(worker_id, state, _safe_text(envelope.get("intent"), 54)))
    return build_snapshot(task_id=task_id, source_ref=source_ref, phase=phase, workers=workers)

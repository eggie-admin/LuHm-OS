#!/usr/bin/env python3
"""Read-only, finite human-centered demo queue. No work execution or mutation."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / "game" / "demo" / "demoAssetPriorityV1.json"


def resolve(document: dict[str, Any]) -> dict[str, Any]:
    bounded = document["boundedWork"]
    queue = bounded["queue"]
    if len(queue) != bounded["maxQueueItems"] or bounded["generateNewTasksWhenEmpty"]:
        raise ValueError("RED_UNBOUNDED_DEMO_QUEUE")
    by_id = {row["id"]: row for row in queue}
    if len(by_id) != len(queue):
        raise ValueError("RED_DUPLICATE_TASKS")
    allowed_states = {"PENDING", "BLOCKED", "DONE"}
    for row in queue:
        if row["state"] not in allowed_states:
            raise ValueError("RED_UNKNOWN_TASK_STATE")
        if row["state"] == "DONE" and not row.get("evidenceRefs"):
            raise ValueError("RED_FAKE_COMPLETION")
        if not row.get("proof"):
            raise ValueError("RED_MISSING_PROOF_CONTRACT")
        if any(parent not in by_id for parent in row["dependsOn"]):
            raise ValueError("RED_UNKNOWN_DEPENDENCY")
    visited: set[str] = set()
    visiting: set[str] = set()

    def visit(task_id: str) -> None:
        if task_id in visiting:
            raise ValueError("RED_CYCLIC_DEMO_QUEUE")
        if task_id in visited:
            return
        visiting.add(task_id)
        for parent in by_id[task_id]["dependsOn"]:
            visit(parent)
        visiting.remove(task_id)
        visited.add(task_id)
    for task_id in by_id:
        visit(task_id)

    ready = [
        row["id"] for row in queue if row["state"] == "PENDING"
        and all(by_id[parent]["state"] == "DONE" for parent in row["dependsOn"])
    ]
    waiting = [
        row["id"] for row in queue if row["state"] != "DONE" and row["id"] not in ready
    ]
    done = [row["id"] for row in queue if row["state"] == "DONE"]
    return {
        "schema": "luhmOs.finiteDemoQueueReceipt.v1",
        "status": "READ_ONLY_PROPOSALS",
        "readyNow": ready,
        "waitingForProofOrDependency": waiting,
        "completedWithEvidence": done,
        "terminal": len(done) == len(queue),
        "newTasksGenerated": 0,
        "automaticExecution": False,
        "publicPublication": False,
        "productCrown": "STOP",
    }


if __name__ == "__main__":
    doc = json.loads(DEFAULT.read_text(encoding="utf-8"))
    print(json.dumps(resolve(doc), indent=2))

#!/usr/bin/env python3
"""LuHm milestone continuity planner. Pure/read-only; never acts on a host.

Observed evidence must be supplied fresh by the invoking ChatGPT Task or reviewer.
This script cannot turn historical GREEN receipts into new runtime proof.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "doctrine" / "milestoneTaskQueueV1.json"
HEX_SHA = re.compile(r"^[a-f0-9]{40}$")
OBSERVED_STATES = frozenset({"PROVEN", "SOFT_RED", "HARD_RED", "AMBER", "WATCH", "UNKNOWN"})
HUMAN_LANES = frozenset({"physicalDevice", "androidApk", "finalAcceptance"})
FORBIDDEN_AUTOMATIONS = frozenset({
    "BYPASS_BRANCH_RULES", "UNQUARANTINE_AGENTS", "ROTATE_OR_REQUEST_SECRET_VALUES",
    "PUBLISH_PRIVATE_MEDIA", "CREATE_PAID_SERVICE", "AUTOMATIC_PUBLIC_APK_RELEASE",
    "DEVICE_LOCK_OUT", "INVENT_PHYSICAL_PROOF"
})


def validate(queue: dict) -> None:
    if queue.get("schema") != "luhmOs.milestoneTaskQueue.v1":
        raise ValueError("QUEUE_SCHEMA")
    if queue.get("authority") != "Professor" or queue.get("status") != "CROWNED_SCOPED_CONTINUITY":
        raise ValueError("QUEUE_AUTHORITY")
    if queue.get("sourceTruth") != "doctrine/currentSourceTruthV3.json":
        raise ValueError("QUEUE_SOURCE_TRUTH")
    if queue.get("scheduler", {}).get("runnerCount") != 1:
        raise ValueError("MULTIPLE_SCHEDULED_RUNNERS")
    law = queue.get("taskLaw", {})
    if not law.get("onlyOneMutationLane") or law.get("hardRedScope") != "BLOCK_AFFECTED_TASK_NOT_ENTIRE_INDEPENDENT_QUEUE":
        raise ValueError("GLOBAL_STOP_OR_RACE")
    if not 1 <= law.get("maxRetryBeforeEscalation", 0) <= 3:
        raise ValueError("UNBOUNDED_RETRIES")
    if not 1 <= law.get("boundedAttemptsPerTick", 0) <= 2:
        raise ValueError("UNBOUNDED_TICK")
    if law.get("noGlobalStopOnUnrelatedHardRed") is not True:
        raise ValueError("HARD_RED_CASCADE")
    if not FORBIDDEN_AUTOMATIONS.issubset(set(law.get("forbidden", []))):
        raise ValueError("MISSING_SAFETY_FENCES")
    if queue.get("security", {}).get("runtimeWorkerActivationAllowed") is not False or not queue["security"].get("registeredAgentsStillQuarantined"):
        raise ValueError("AGENT_QUARANTINE_BYPASS")
    if queue.get("security", {}).get("userOriginalArtOnPublicHost") is not False or not queue["security"].get("noNewPaidServices"):
        raise ValueError("PRIVATE_MEDIA_OR_SPEND")
    if queue.get("productCrown") != "NOT_PROVEN_FROM_QUEUE_ONLY":
        raise ValueError("FALSE_PRODUCT_CROWN")

    tasks = queue.get("tasks", [])
    ids = [t.get("id") for t in tasks]
    if not 1 <= len(ids) <= 24 or len(ids) != len(set(ids)):
        raise ValueError("INVALID_TASK_IDS")
    known = set(ids)
    if not all(re.fullmatch("[a-z][A-Za-z0-9]{2,64}", x or "") for x in ids):
        raise ValueError("BAD_TASK_NAMING")
    for t in tasks:
        if t.get("id") in t.get("dependsOn", []) or not set(t.get("dependsOn", [])).issubset(known):
            raise ValueError("BAD_DEPENDENCY")
        if not isinstance(t.get("priority"), int) or not t.get("next") or not t.get("evidenceRequired"):
            raise ValueError("INCOMPLETE_TASK")
        if t.get("initialState") not in {"WATCH", "UNKNOWN", "SOFT_RED", "AMBER", "WAIT_DEPENDENCY"}:
            raise ValueError("INITIAL_STATE_IS_NOT_PROOF")
    seen, visiting = set(), set()
    by_id = {t["id"]: t for t in tasks}

    def visit(key: str) -> None:
        if key in visiting:
            raise ValueError("CYCLIC_MILESTONES")
        if key in seen:
            return
        visiting.add(key)
        for parent in by_id[key]["dependsOn"]:
            visit(parent)
        visiting.remove(key)
        seen.add(key)

    for key in known:
        visit(key)


def evaluate(queue: dict, observations: dict, source_ref: str) -> dict:
    """A deterministic *plan*, never approval or mutation."""
    validate(queue)
    if not HEX_SHA.fullmatch(source_ref):
        raise ValueError("SOURCE_REF_NOT_EXACT")
    if not isinstance(observations, dict) or set(observations) - {t["id"] for t in queue["tasks"]}:
        raise ValueError("UNKNOWN_TASK_OBSERVATION")
    by_id = {t["id"]: t for t in queue["tasks"]}
    results = {}
    visiting = set()

    def resolve(key: str) -> dict:
        if key in results:
            return results[key]
        if key in visiting:
            raise ValueError("CYCLIC_MILESTONES")
        visiting.add(key)
        task = by_id[key]
        parents = [resolve(p) for p in task["dependsOn"]]
        obs = observations.get(key, {})
        if not isinstance(obs, dict):
            raise ValueError("INVALID_OBSERVATION")
        state = obs.get("state", "UNKNOWN")
        if state not in OBSERVED_STATES:
            raise ValueError("INVALID_OBSERVED_STATE")
        evidence = obs.get("evidenceRefs", [])
        if not isinstance(evidence, list) or len(evidence) > 20 or any(
            not isinstance(x, str) or len(x) > 300 for x in evidence
        ):
            raise ValueError("INVALID_EVIDENCE")
        checked = obs.get("checkedAt", "")
        observed_source = obs.get("sourceRef", "")
        exact = observed_source == source_ref and bool(HEX_SHA.fullmatch(str(observed_source)))
        fresh_proof = exact and bool(checked) and bool(evidence)
        if state == "PROVEN":
            if any(p["state"] != "DONE" for p in parents):
                raise ValueError("DEPENDENCY_NOT_PROVEN:" + key)
            # A source-verified claim is still NOT automatically phone/owner proof.
            if task["lane"] in HUMAN_LANES and obs.get("ownerReceipt") is not True:
                raise ValueError("OWNER_RECEIPT_REQUIRED:" + key)
            if not fresh_proof:
                raise ValueError("UNPROVEN_MILESTONE:" + key)
            result = "DONE"
        elif state == "HARD_RED":
            if obs.get("reason") not in queue["taskLaw"]["hardRedReasons"] or not evidence:
                raise ValueError("HARD_RED_NEEDS_CAUSE_AND_EVIDENCE")
            result = "HARD_RED"
        elif any(p["state"] != "DONE" for p in parents):
            result = "WAIT_DEPENDENCY"
        elif state == "SOFT_RED":
            result = "REPAIR"
        elif state == "WATCH":
            result = "WATCH"
        elif state == "AMBER":
            result = "ADVANCE"
        else:
            result = "INSPECT"
        record = {
            "taskId": key, "state": result, "priority": task["priority"],
            "dependencies": task["dependsOn"], "issue": task["issue"],
            "nextAction": task["next"],
            "proofScope": "EXACT_SOURCE" if fresh_proof else "UNVERIFIED_OR_PENDING",
            "reason": obs.get("reason", "") if result == "HARD_RED" else ""
        }
        results[key] = record
        visiting.remove(key)
        return record

    for task in queue["tasks"]:
        resolve(task["id"])
    ordered = sorted(results.values(), key=lambda t: (t["priority"], t["taskId"]))
    actionable = [t for t in ordered if t["state"] in {"REPAIR", "ADVANCE", "INSPECT", "WATCH"}]
    stopped = [t for t in ordered if t["state"] == "HARD_RED"]
    done = [t for t in ordered if t["state"] == "DONE"]
    return {
        "schema": "luhmOs.milestoneTaskPlan.v1",
        "sourceRef": source_ref,
        "mode": "READ_ONLY_NEXT_ACTION_PLANNER",
        "status": "CONTINUE" if actionable else ("BLOCKED_BY_HARD_RED" if stopped else "WAIT_FOR_DEPENDENCIES_OR_FINISHED"),
        "nextExecutable": actionable[0]["taskId"] if actionable else None,
        "remainingExecutable": [t["taskId"] for t in actionable],
        "hardRedTasks": [t["taskId"] for t in stopped],
        "completedTasks": [t["taskId"] for t in done],
        "tasks": ordered,
        "executionAuthorizedByThisPlan": False,
        "humanProductCrownGranted": False
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="Fresh actual canonical main SHA")
    parser.add_argument("--observations", help="Fresh sanitized task observation JSON file")
    args = parser.parse_args()
    q = json.loads(QUEUE.read_text(encoding="utf-8"))
    observations = json.loads(Path(args.observations).read_text(encoding="utf-8")) if args.observations else {}
    print(json.dumps(evaluate(q, observations, args.source), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

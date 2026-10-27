#!/usr/bin/env python3
"""Read-only Skuld/Lum task-array planner around the existing single-use CAST gate.

This is not an agent scheduler, source mutator, database service, or build launcher.
Each eventual artifact build requires its own exact-scoped Professor CAST.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

repoRoot = Path(__file__).resolve().parents[1]
sha40Pattern = re.compile(r"[0-9a-f]{40}\Z")
scopePattern = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}\Z")


def readJson(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Expected object: " + str(path))
    return data


def loadCanon(root: Path = repoRoot) -> dict:
    documents = {
        "orchestra": readJson(root / "doctrine/castTaskArrayV1.json"),
        "queue": readJson(root / "doctrine/milestoneTaskQueueV1.json"),
        "twins": readJson(root / "doctrine/forgeTwinsV3.json"),
        "escalation": readJson(root / "doctrine/escalationKernelV1.json"),
        "operating": readJson(root / "doctrine/fourTierOperatingModelV1.json"),
        "release": readJson(root / "doctrine/pluginBetaFourLaneV1.json"),
        "sql": readJson(root / "doctrine/typedFourLaneSqlV1.json"),
        "agents": readJson(root / "doctrine/agentSystemDeploymentV1.json"),
    }
    contract = documents["orchestra"]
    expected = {
        "escalation": [x["id"] for x in documents["escalation"]["tierSemantics"]],
        "operating": [x["id"] for x in documents["operating"]["tiers"]],
        "release": [x["id"] for x in documents["release"]["lanes"]],
        "sql": [x["id"] for x in documents["sql"]["lanes"]],
    }
    if contract["fourIndependentAxes"] != expected:
        raise ValueError("Four orthogonal Canon axes drifted")
    if contract["sourceForge"] != "tetsu" or contract["compileForge"] != "kaji":
        raise ValueError("Forge identity drift")
    twins = documents["twins"]["twins"]
    if twins["Tetsu"]["role"] != "SOURCE_FORGE" or twins["Kaji"]["role"] != "COMPILE_FORGE":
        raise ValueError("Forge permissions drift")
    if twins["Kaji"]["compileAuthorityRequiresCast"] is not True:
        raise ValueError("Kaji CAST constraint missing")
    envelope = documents["twins"]["castEnvelope"]
    if "singleUse" not in envelope.get("requiredFields", []):
        raise ValueError("CAST single-use envelope field missing")
    if envelope["consumedOnAttempt"] is not True or envelope["persistentAuthorizationAllowed"] is not False:
        raise ValueError("CAST must be consumed per task on attempt")
    budget = documents["agents"]["activationLaw"]
    if budget["maxParallelSupportWorkers"] != 3 or budget["oneMutableSourceLane"] is not True:
        raise ValueError("Staffing budget drift")
    if budget["recursiveRecruitment"] is not False or budget["residentCoreHiddenAsync"] is not False:
        raise ValueError("Unbounded worker activation prohibited")
    if contract["workerBudget"]["hiddenAsyncExecution"] is not False:
        raise ValueError("Planner must not claim hidden asynchronous workers")
    if contract["workerBudget"]["parallelSupportMaximum"] != 3 or contract["workerBudget"]["mutableSourceLanes"] != 1:
        raise ValueError("Planner budget drift")
    if contract["castArrayLaw"]["taskArrayNeverDispatchesBuild"] is not True:
        raise ValueError("A queued item must not dispatch a build")
    if contract["castArrayLaw"]["eachBuildRequiresOwnCast"] is not True:
        raise ValueError("Batch CAST prohibited")
    if contract["promotion"] is not False or contract["crownStatus"] != "STOP":
        raise ValueError("Candidate cannot self-promote")
    return documents


def compilePreview(
    taskIds: list[str],
    *,
    sourceRef: str,
    scopeId: str,
    escalationTier: int = 0,
    root: Path = repoRoot,
) -> dict:
    if not sha40Pattern.fullmatch(sourceRef):
        raise ValueError("Exact 40-character lowercase sourceRef required")
    if not scopePattern.fullmatch(scopeId):
        raise ValueError("Invalid or unbounded scopeId")
    if type(escalationTier) is not int or escalationTier not in range(4):
        raise ValueError("Escalation tier must be an integer 0..3")
    if not taskIds or len(taskIds) > 8 or any(not isinstance(x, str) for x in taskIds):
        raise ValueError("Task array must contain 1..8 named tasks")
    if len(set(taskIds)) != len(taskIds):
        raise ValueError("Duplicate task ID in array")
    canon = loadCanon(root)
    queueItems = canon["queue"]["tasks"]
    byId = {x["id"]: x for x in queueItems}
    if len(byId) != len(queueItems):
        raise ValueError("Canonical task queue repeats an id")
    unknown = [x for x in taskIds if x not in byId]
    if unknown:
        raise ValueError("Unknown canonical tasks: " + ",".join(unknown))
    if any(x not in byId for item in queueItems for x in item.get("dependsOn", [])):
        raise ValueError("Canonical dependency references an unknown task")
    items = []
    for taskId in sorted(taskIds, key=lambda x: (byId[x]["priority"], x)):
        task = byId[taskId]
        items.append({
            "taskId": taskId,
            "sourceRef": sourceRef,
            "scopeId": scopeId,
            "escalationTier": escalationTier,
            "tierId": canon["orchestra"]["fourIndependentAxes"]["escalation"][escalationTier],
            "priority": task["priority"],
            "dependsOn": task.get("dependsOn", []),
            "ownerLane": task["lane"],
            "intent": task["mode"],
            "smallestNextAction": task["next"],
            "evidenceRequired": task["evidenceRequired"],
            "state": "QUEUED_FOR_INSPECTION_NOT_DISPATCHED",
            "buildRequiresSeparateSingleUseCast": True,
            "snapshotAndRollbackRequiredBeforeMutation": True,
            "buildDispatched": False,
            "sourceMutated": False,
            "workerActivated": False,
        })
    return {
        "schema": "luhmOs.castTaskArrayPreview.v1",
        "contractStage": "SOURCE_CANDIDATE_NOT_EXECUTING",
        "sourceRef": sourceRef,
        "scopeId": scopeId,
        "taskCount": len(items),
        "tasks": items,
        "castEnvelopesGranted": 0,
        "buildsDispatched": 0,
        "agentWorkersStarted": 0,
        "sqlExecuted": False,
        "hostMountVerified": False,
        "publicationAuthorized": False,
        "crownGranted": False,
        "crownStatus": "STOP",
        "nextBoundary": "Obtain exact per-task independent proof and explicit one-use Professor CAST for any needed build",
    }


def selfTest() -> None:
    canon = loadCanon()
    ref = "a" * 40
    ids = [task["id"] for task in canon["queue"]["tasks"]]
    assert ids
    preview = compilePreview(ids[:2], sourceRef=ref, scopeId="cathedral/first-cast", escalationTier=2)
    assert preview["taskCount"] == min(len(ids), 2)
    assert preview["castEnvelopesGranted"] == 0 and preview["buildsDispatched"] == 0
    assert all(not item["buildDispatched"] and item["tierId"] == "specialist" for item in preview["tasks"])
    assert all(item["sourceRef"] == ref and item["scopeId"] == "cathedral/first-cast" for item in preview["tasks"])
    for badIds, kwargs in [
        ([ids[0], ids[0]], {}),
        (["notRegistered"], {}),
        ([ids[0]], {"escalationTier": 4}),
        ([ids[0]], {"escalationTier": True}),
        ([ids[0]], {"sourceRef": "main"}),
        ([ids[0]], {"scopeId": ";DROP TABLE"}),
    ]:
        options = {"sourceRef": ref, "scopeId": "cathedral/first-cast", **kwargs}
        try:
            compilePreview(badIds, **options)
        except ValueError:
            pass
        else:
            raise AssertionError("Unsafe or unknown task intent unexpectedly accepted")
    print("CAST_TASK_ARRAY_READ_ONLY_SELF_TEST_GREEN")


def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only existing milestone queue inspection; never invokes CAST or workers")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--tasks", help="Comma-separated IDs from canonical milestone task queue")
    parser.add_argument("--source-ref", dest="sourceRef")
    parser.add_argument("--scope-id", dest="scopeId")
    parser.add_argument("--tier", type=int, default=0)
    args = parser.parse_args()
    if args.self_test:
        selfTest()
    if args.tasks:
        if args.sourceRef is None or args.scopeId is None:
            parser.error("--source-ref and --scope-id required with --tasks")
        tasks = [s.strip() for s in args.tasks.split(",")]
        print(json.dumps(compilePreview(tasks, sourceRef=args.sourceRef, scopeId=args.scopeId, escalationTier=args.tier), indent=2))
    elif not args.self_test:
        parser.error("Choose --self-test or --tasks")


if __name__ == "__main__":
    main()

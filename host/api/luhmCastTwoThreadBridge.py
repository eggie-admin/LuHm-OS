#!/usr/bin/env python3
"""LuHm CAST Bridge two-thread, four-lane, four-tier *source-only* projection.

Not a second ChatGPT conversation, hosted mini-agent, message queue, worker,
process or deployer. Builds two clearly labeled timelines for a trusted UI,
without granting credibility to submitted receipts or persisting raw goals.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "doctrine" / "castTwoThreadBridgeV1.json"
TYPED = ROOT / "doctrine" / "typedFourLaneSqlV1.json"
ESCALATION = ROOT / "doctrine" / "escalationKernelV1.json"
COVENANT = ROOT / "doctrine" / "everlastingCovenantV1.json"
QUARANTINE = ROOT / "doctrine" / "companyWideOperationalQuarantineV1.json"
SOURCE = ROOT / "doctrine" / "currentSourceTruthV3.json"
ORCHESTRATION = ROOT / "host" / "api" / "luhmCanonOrchestration.py"
LANES = ("numericStream", "textStream", "booleanStream", "aiManifestStream")
THREADS = ("professorLum", "lumMesh")
STAGES = ("sanityCheck", "audit", "ingest", "mutation", "test", "apply",
          "continue", "deploy")
HEARTBEATS = ("hear", "resolve", "act", "verify")
EXACT_SHA = re.compile(r"[0-9a-f]{40}\Z")
DIGEST = re.compile(r"[0-9a-f]{64}\Z")
IDENT = re.compile(r"[a-z][A-Za-z0-9]{0,79}\Z")
MAX_RECEIPTS = 8


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf8"))
    if not isinstance(value, dict):
        raise ValueError("RED_CAST_CONTRACT_NOT_OBJECT")
    return value


def _source_orchestration() -> Any:
    spec = importlib.util.spec_from_file_location("luhmCanonOrchestration", ORCHESTRATION)
    if spec is None or spec.loader is None:
        raise RuntimeError("RED_CAST_BASE_MODULE")
    control = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(control)
    return control


def source_audit() -> dict[str, Any]:
    p = _load(CONTRACT)
    typed = _load(TYPED)
    escalation = _load(ESCALATION)
    covenant = _load(COVENANT)
    q = _load(QUARANTINE)
    truth = _load(SOURCE)
    issues: list[str] = []
    if p.get("schema") != "luhmOs.castTwoThreadBridge.v1":
        issues.append("RED_CAST_SCHEMA")
    identity = p.get("identity", {})
    if (identity.get("source") != "eggie-admin/LuHm-OS"
            or identity.get("controller") != "lum" or
            identity.get("authority") != "Professor" or
            identity.get("product") != "LuHm-OS"):
        issues.append("RED_CAST_IDENTITY")
    anchors = p.get("anchors", [])
    if not isinstance(anchors, list) or len(anchors) != 10 or not all(
            (ROOT / path).is_file() and
            (ROOT / path).resolve().is_relative_to(ROOT.resolve())
            for path in anchors if isinstance(path, str)):
        issues.append("RED_CAST_ANCHORS")
    if ([x.get("id") for x in p.get("visualThreads", [])] != list(THREADS)
            or any(not isinstance(x.get("label"), str) or not x.get("label")
                   for x in p.get("visualThreads", []))):
        issues.append("RED_CAST_THREADS")
    if ([x.get("id") for x in p.get("fourTypedDataLanes", [])] != list(LANES)
            or [x.get("id") for x in typed.get("lanes", [])] != list(LANES)):
        issues.append("RED_CAST_TYPED_LANES")
    if ([x.get("id") for x in p.get("tiers", [])] != list(range(4))
            or [x.get("tier") for x in escalation.get("tierSemantics", [])] != list(range(4))):
        issues.append("RED_CAST_TIERS")
    if (p.get("canonicalStates") != list(STAGES)
            or covenant.get("guardRail", {}).get("orderedStates") != list(STAGES)
            or escalation.get("fourByFourModel", {}).get("horizontalBeats") != list(HEARTBEATS)):
        issues.append("RED_CAST_STATE_MACHINE")
    for m in p.get("professorLanguage", []):
        if not isinstance(m.get("mapsTo"), list) or any(
                state not in STAGES and state != "postDeployBridgeSmoke"
                for state in m["mapsTo"]):
            issues.append("RED_CAST_LANGUAGE_MAP")
    if len(p.get("professorLanguage", [])) != 6:
        issues.append("RED_CAST_LANGUAGE_COUNT")
    rules = p.get("receiptRules", {})
    for key in (
        "stageOrderStrict", "resumeAcrossChangedSource", "goalStoredAsHashOnly",
        "twoLogicalThreadsDoesNotMeanTwoExecutingAgents", "noParallelSourceMutators",
        "neverClaimGreenFromSourceOnly", "sameTaskScopeForBothThreads"
    ):
        if rules.get(key) is not (False if key == "resumeAcrossChangedSource" else True):
            issues.append("RED_CAST_RECEIPT_AUTHORITY")
            break
    if (rules.get("requiredIdentity") !=
            ["taskId", "sourceRef", "scopeId", "stage", "evidenceSha256"]):
        issues.append("RED_CAST_RECEIPT_FIELDS")
    runtime = p.get("runtime", {})
    if (runtime.get("activeMiniAgents") != 0 or
            runtime.get("backgroundWorkers") != 0 or
            runtime.get("clientThreadCreation") is not False or
            runtime.get("castExecuted") is not False or
            runtime.get("productionDeployed") is not False):
        issues.append("RED_CAST_FAKE_LIVE_THREAD")
    if (q.get("state") != "QUARANTINED" or q.get("activeTaskWorkersAllowed") is not False
            or truth.get("promotion") is not False
            or p.get("crownStatus") != "STOP"):
        issues.append("RED_CAST_SOURCE_QUARANTINE")
    for k in ("companyQuarantine", "noAutoMerge", "noAutoDeploy",
              "noSelfApproval", "noNewPaidProvider", "readOnlyMcp"):
        if p.get("policy", {}).get(k) is not True:
            issues.append("RED_CAST_RUNTIME_PERMISSION")
            break
    return {
        "schema": "luhmOs.castTwoThreadSourceAudit.v1",
        "status": "SOURCE_CONSISTENT_ONLY" if not issues else "RED_SOURCE_DRIFT",
        "issues": sorted(set(issues)),
        "threadCount": len(p.get("visualThreads", [])),
        "dataLaneCount": len(p.get("fourTypedDataLanes", [])),
        "escalationTierCount": len(p.get("tiers", [])),
        "matrixCells": 4 * 4,
        "activeAgentThreads": 0, "hostConnected": False,
        "chatGptSecondConversationCreated": False,
        "networkCalls": 0, "sqlWrites": 0,
        "productionDeployed": False, "greenAuthority": False,
        "crownAuthority": False,
    }


def _receipt_review(receipts: Any, identity: Mapping[str, Any]) -> dict[str, Any]:
    if receipts is None:
        receipts = []
    if not isinstance(receipts, list) or len(receipts) > MAX_RECEIPTS:
        raise ValueError("RED_CAST_RECEIPT_LIST")
    seen: set[str] = set()
    reviewed = []
    for i, x in enumerate(receipts):
        if not isinstance(x, Mapping) or set(x) != {
            "taskId", "sourceRef", "scopeId", "stage", "evidenceSha256"}:
            raise ValueError("RED_CAST_RECEIPT_SHAPE")
        if any(x[field] != identity[field] for field in
               ("taskId", "sourceRef", "scopeId")):
            raise ValueError("RED_CAST_RECEIPT_IDENTITY_CONFLICT")
        stage = x["stage"]
        if type(stage) is not str or stage not in STAGES or stage in seen:
            raise ValueError("RED_CAST_RECEIPT_STAGE")
        if i != STAGES.index(stage):
            raise ValueError("RED_CAST_RECEIPT_ORDER_OR_SKIP")
        evidence = x["evidenceSha256"]
        if type(evidence) is not str or DIGEST.fullmatch(evidence) is None:
            raise ValueError("RED_CAST_RECEIPT_DIGEST")
        seen.add(stage)
        reviewed.append({
            "stage": stage, "claimDigestSha256": evidence,
            "claimSourceMatched": True, "provenByCiOrTrustedHost": False,
            "disposition": "UNTRUSTED_CLAIM_NEEDS_ACTUAL_RECEIPT",
        })
    return {
        "claimsSubmitted": len(reviewed),
        "claimFormatConsistent": True,
        "proofOriginTrusted": False,
        "claimedStages": reviewed,
        "latestClaimedStage": reviewed[-1]["stage"] if reviewed else None,
    }


def plan(task_id: str, source_ref: str, scope_id: str, goal: str,
         tier: int = 0, requested_stage: str = "sanityCheck",
         evidence_claims: Any = None) -> dict[str, Any]:
    if any(type(v) is not str or IDENT.fullmatch(v) is None
           for v in (task_id, scope_id)):
        raise ValueError("RED_CAST_TASK_SCOPE")
    if type(source_ref) is not str or EXACT_SHA.fullmatch(source_ref) is None:
        raise ValueError("RED_CAST_SOURCE_SHA")
    if type(goal) is not str or not 1 <= len(goal.strip()) <= 2048:
        raise ValueError("RED_CAST_GOAL_BOUND")
    if type(tier) is not int or tier not in range(4):
        raise ValueError("RED_CAST_TIER")
    if type(requested_stage) is not str or requested_stage not in STAGES:
        raise ValueError("RED_CAST_STAGE")
    check = source_audit()
    if check["issues"]:
        return {"status": "STOP_SOURCE_DRIFT", "issues": check["issues"],
                "greenAuthority": False, "crownAuthority": False}
    control = _source_orchestration()
    base = control.plan(task_id, source_ref, scope_id, goal, tier)
    if (base.get("status") != "PLAN_ONLY" or base.get("runningAgentThreads") != 0
            or len(base.get("logicalLanes", [])) != 2):
        raise RuntimeError("RED_CAST_BASE_ORCHESTRATION_DRIFT")
    ident = {"taskId": task_id, "sourceRef": source_ref, "scopeId": scope_id}
    review = _receipt_review(evidence_claims, ident)
    digest = base["requestSha256"]
    stage_i = STAGES.index(requested_stage)
    source_action = "VERIFY_EXACT_SOURCE_WITH_GITHUB_CI"
    next_action = ("VERIFY_EACH_PRIOR_STAGE_AT_SAME_SOURCE_THEN_REQUEST_OWNER_REVIEW"
                   if stage_i else source_action)
    # Thread 1 is user-facing conversation content, thread 2 is an explicitly
    # SOURCE-ONLY orchestration projection. Neither creates a ChatGPT thread.
    threads = [
        {
            "threadId": "professorLum", "title": "Professor ↔ Lum",
            "transport": "IN_CHAT_PRESENTATION_ONLY",
            "messages": [
                {"actor": "Professor", "kind": "intentDigest",
                 "sha256Hex": digest, "state": "USER_GOAL_HASHED"},
                {"actor": "lum", "kind": "coordination",
                 "stage": requested_stage, "tier": tier,
                 "nextAction": next_action, "state": "PLAN_ONLY"},
            ], "liveAgent": False,
        },
        {
            "threadId": "lumMesh", "title": "Lum ↔ orchestration",
            "transport": "DETERMINISTIC_RECEIPT_PROJECTION_ONLY",
            "messages": [
                {"actor": "lum", "kind": "handoff",
                 "taskId": task_id, "sourceRef": source_ref,
                 "scopeId": scope_id, "requestSha256": digest,
                 "state": "SOURCE_CANDIDATE"},
                {"actor": "urdDoctorGoddess", "kind": "evidenceReview",
                 "claimedEvidenceCount": review["claimsSubmitted"],
                 "proofOriginTrusted": False, "state": "HOLD_EXTERNAL_PROOF"},
            ], "liveAgent": False,
        }
    ]
    lanes = [
        {"id": "numericStream", "tier": tier, "stageOrdinal": stage_i,
         "maxLogicalLanes": 2, "activeWorkers": 0},
        {"id": "textStream", "taskId": task_id, "sourceRef": source_ref,
         "scopeId": scope_id, "requestSha256": digest},
        {"id": "booleanStream", "sourceVerified": None,
         "ciExactHeadVerified": None, "runtimeWorkerActive": False,
         "castBridgeTestProven": False, "ownerAuthorized": False},
        {"id": "aiManifestStream", "capability": "castBridgeSourcePlan",
         "roleLabels": [lane["roleLabel"] for lane in base["logicalLanes"]],
         "sourceOnly": True, "mutationAuthority": False,
         "greenAuthority": False},
    ]
    matrix = [
        {"tier": t, "lanes": [
            {"dataLane": lane, "state": "HOLD_SOURCE_OR_RUNTIME_EVIDENCE",
             "verified": False} for lane in LANES
        ]} for t in range(4)
    ]
    canonical = [
        {"stage": stage, "ordinal": i,
         "state": "UNVERIFIED_SOURCE_CANDIDATE" if i == 0
                  else "HOLD_PREDECESSOR_PROOF",
         "actualExecutionProven": False}
        for i, stage in enumerate(STAGES)
    ]
    return {
        "schema": "luhmOs.castTwoThreadBridgePlan.v1",
        **ident, "requestSha256": digest,
        "state": "HOLD_EXTERNAL_CI_HOST_AND_OWNER_RECEIPTS",
        "requestedStage": requested_stage, "tier": tier,
        "threads": threads, "typedLanes": lanes,
        "matrix4x4": matrix,
        "canon": canonical, "professorStageMap": _load(CONTRACT)["professorLanguage"],
        "evidenceReview": review, "nextAction": next_action,
        "bridgeSmokeState": "NOT_RUN",
        "sourceCommitVerifiedAgainstGitHub": False,
        "appSecondThreadCreated": False,
        "actualMeshAgentsStarted": 0,
        "networkCalls": 0, "databaseWrites": 0,
        "runtimeMutation": False, "productionDeployment": False,
        "greenAuthority": False, "crownAuthority": False,
    }


if __name__ == "__main__":
    print(json.dumps(plan("sampleCast", "a" * 40, "studioScope",
                          "Produce an exact-source plan"), indent=2))

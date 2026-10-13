#!/usr/bin/env python3
"""Fail-closed LuHm orchestra candidate gate: never invokes providers or writes source."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    "doctrine/lumOrchestraHardeningV1.json",
    "doctrine/currentSourceTruthV3.json",
    "doctrine/luhmAiControlPlaneV1.json",
    "doctrine/agentSystemDeploymentV1.json",
    "doctrine/everlastingCovenantV1.json",
    "doctrine/apiSpineV1.json",
    "doctrine/googleAiDeveloperEntitlementsV1.json",
]
SHA = re.compile(r"[0-9a-f]{40}\Z")
ROUTES = {
    "read": {"lum", "kiri"},
    "research": {"lum", "skuldResearch"},
    "proof": {"lum", "urdDoctorGoddess"},
    "patch": {"lum", "kugi", "urdDoctorGoddess"},
    "build": {"lum", "kugi", "tetsu", "kaji", "urdDoctorGoddess"},
}
SUPPORT = {
    "kiri", "momo", "shiori", "fumi", "yume", "koe", "sumi",
    "urdDoctorGoddess", "belldandySecretary", "skuldResearch",
}

def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("RED_DUPLICATE_JSON_KEY")
        result[key] = value
    return result

def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)

def source_sha(root):
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()

def policy_check(root):
    data = {name: load_json(root / name) for name in FILES}
    cfg, truth, control, registry, covenant, api, googleEntitlements = (data[name] for name in FILES)
    errors = []
    def need(condition, code):
        if not condition:
            errors.append(code)
    need(cfg.get("schema") == "luhmOs.lumOrchestraHardening.v1", "RED_SCHEMA")
    need(cfg.get("status") == "PROPOSED_CANDIDATE_ONLY", "RED_CANDIDATE_BOUNDARY")
    need(cfg.get("stageOrder") == covenant.get("guardRail", {}).get("orderedStates"), "RED_COVENANT_STAGE_DRIFT")
    need(cfg.get("boss") == control.get("boss") == "lum", "RED_BOSS_DRIFT")
    need(cfg.get("roster") == FILES[3], "RED_DEPLOYMENT_POINTER")
    agents = control.get("agents", {})
    required = registry.get("requiredAgents", [])
    need(len(required) == registry.get("requiredAgentCount") == 15, "RED_ROSTER_COUNT")
    need(set(required) == set(agents) and len(set(required)) == 15, "RED_ROSTER_IDENTITY")
    need(cfg.get("canonicalAgents") == required, "RED_ORCHESTRA_ROSTER_DRIFT")
    for agent in required:
        row = agents.get(agent, {})
        skill = row.get("skillPath")
        valid_path = isinstance(skill, str) and skill.startswith("agents/") and ".." not in Path(skill).parts
        need(valid_path and (root / skill).is_file() and not (root / skill).is_symlink() if valid_path else False,
             "RED_MISSING_SKILL_" + agent)
        need(row.get("mayRecruit") is False and row.get("maySelfApprove") is False, "RED_AGENT_AUTHORITY_" + agent)
    inv = control.get("invariants", {})
    need(inv.get("maxParallelSupportWorkers") == cfg.get("maxParallelSupportWorkers") == 3, "RED_PARALLEL_LIMIT")
    need(inv.get("oneMutableSourceLane") is True and cfg.get("oneMutableSourceLane") is True, "RED_SOURCE_LANE")
    need(inv.get("hiddenAsyncExecution") is False and inv.get("selfApproval") is False, "RED_HIDDEN_OR_SELF_APPROVAL")
    need(truth.get("crownStatus") == cfg.get("crownStatus") == "STOP", "RED_CROWN_DRIFT")
    need(truth.get("workingDoctrineLane", {}).get("status") == "PROPOSED_ONLY", "RED_PROPOSED_LANE")
    guard = covenant.get("guardRail", {})
    need(guard.get("automaticMerge") is False and guard.get("automaticPublication") is False, "RED_COVENANT_AUTO_AUTHORITY")
    google = api.get("providers", {}).get("googleAi", {})
    need(google.get("adapterId") == "bigBrother" and google.get("readiness") == "RECEIPT_REQUIRED",
         "RED_GOOGLE_ADAPTER")
    gc = cfg.get("googleAi", {})
    need(gc.get("apiInvocationDefault") == "DENY" and gc.get("reviewOnly") is True,
         "RED_GOOGLE_REVIEW_BOUNDARY")
    need(gc.get("consumerSubscriptionGrantsApiAccess") is False and gc.get("requiresBillingAndQuotaProof") is True,
         "RED_GOOGLE_BILLING_GATE")
    axes = googleEntitlements.get("entitlementAxes", {})
    pro = axes.get("consumerSubscription", {})
    benefit = axes.get("developerProgramBenefits", {})
    dev = axes.get("developerApi", {})
    billing = axes.get("cloudBilling", {})
    execution = googleEntitlements.get("executionLaw", {})
    need(googleEntitlements.get("schema") == "luhmOs.googleAiDeveloperEntitlements.v1"
         and googleEntitlements.get("status") == "PROPOSED_CANDIDATE_NO_LIVE_API"
         and googleEntitlements.get("crownStatus") == "STOP", "RED_GOOGLE_ENTITLEMENT_SCHEMA")
    need(googleEntitlements.get("providerId") == "googleAi"
         and googleEntitlements.get("adapterId") == google.get("adapterId")
         and googleEntitlements.get("capabilityRoute") == "doctrine/apiSpineV1.json#providers/googleAi",
         "RED_GOOGLE_PROVIDER_ROUTE")
    need(pro.get("product") == "googleAiPro" and pro.get("evidenceState") == "HISTORICAL_SUBSCRIPTION_EMAIL_2026_09"
         and all(pro.get(field) is False for field in
                 ("grantsDeveloperApi", "grantsCloudBilling", "grantsVertexQuota")),
         "RED_GOOGLE_CONSUMER_TO_API_ESCALATION")
    need(benefit.get("potentialMonthlyCloudCreditUsd") == 10
         and benefit.get("activationState") == "UNKNOWN_NO_ACCOUNT_BOUND_RECEIPT"
         and benefit.get("creditBalanceState") == "UNKNOWN_NO_ACCOUNT_BOUND_RECEIPT"
         and benefit.get("grantApiExecution") is False,
         "RED_GOOGLE_UNREDEEMED_CREDIT_AUTHORITY")
    need(dev.get("automatedConsumerGeminiForbidden") is True
         and dev.get("apiEnabledState") == "UNKNOWN"
         and dev.get("iamState") == "UNKNOWN"
         and dev.get("modelAndQuotaState") == "UNKNOWN"
         and dev.get("authorizedSmokeState") == "UNKNOWN",
         "RED_GOOGLE_DEVELOPER_API_CLAIM")
    need(billing.get("historicalWarning") == "UNRESOLVED_PAYMENT_WARNING_2026_10_01"
         and billing.get("currentResolutionState") == "UNKNOWN"
         and billing.get("paidCallsAllowed") is False
         and billing.get("existingCreditsAloneAuthorizeSpend") is False,
         "RED_GOOGLE_BILLING_WARNING_SUPPRESSED")
    need(execution.get("defaultAction") == "DENY"
         and execution.get("failClosedOnUnknown") is True
         and execution.get("structuralReceiptDoesNotEstablishEntitlement") is True
         and execution.get("noGithubPrOidcOrSecrets") is True
         and execution.get("separateProfessorScopeRequiredForBillableCall") is True
         and execution.get("noProviderCanGrantGreen") is True
         and execution.get("noAutomaticMerge") is True
         and execution.get("noAutomaticDeploy") is True
         and execution.get("noAutomaticCrown") is True,
         "RED_GOOGLE_EXECUTION_AUTHORITY")
    need(len(googleEntitlements.get("authenticatedEvidenceRequirements", [])) >= 8,
         "RED_GOOGLE_ACCOUNT_BOUND_EVIDENCE_CONTRACT")
    gh = cfg.get("github", {})
    need(gh.get("usesSecretsInPrAudit") is False and gh.get("oidcEnabledByThisWorkflow") is False,
         "RED_PR_SECRET_OR_OIDC")
    need(cfg.get("automation", {}).get("automaticProductionDeploy") is False, "RED_AUTO_DEPLOY")
    hashes = {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in FILES}
    return sorted(set(errors)), cfg, hashes

def contains_secret_keys(value):
    if isinstance(value, dict):
        for key, val in value.items():
            if re.search(r"(api.?key|secret|token|password|private.?key|credentials?)", str(key), re.I):
                return True
            if contains_secret_keys(val):
                return True
    if isinstance(value, list):
        return any(contains_secret_keys(v) for v in value)
    return False

def assess(packet, current_sha, cfg):
    """Check candidate shape, not external receipt authenticity or permission."""
    errors = []
    def need(condition, code):
        if not condition:
            errors.append(code)
    if not isinstance(packet, dict):
        return ["RED_TASK_PACKET_SHAPE"], "STOP"
    need(not contains_secret_keys(packet), "RED_CREDENTIAL_FIELD")
    allowed = {"schema", "taskId", "scopeId", "sourceRef", "kind", "requestedStage",
               "providerId", "workers", "budget", "receipts", "authority"}
    need(set(packet) <= allowed, "RED_UNKNOWN_PACKET_FIELD")
    need(packet.get("schema") == "luhmOs.lumOrchestraTask.v1", "RED_TASK_SCHEMA")
    for key in ("taskId", "scopeId"):
        value = packet.get(key)
        need(isinstance(value, str) and bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{2,100}", value)),
             "RED_" + key.upper())
    ref = packet.get("sourceRef")
    need(isinstance(ref, str) and SHA.fullmatch(ref) is not None and ref == current_sha, "RED_SOURCE_MISMATCH")
    steps = cfg.get("stageOrder", [])
    stage = packet.get("requestedStage")
    need(stage in steps, "RED_UNKNOWN_STAGE")
    need(packet.get("providerId") in ("deterministicLocal", "githubCopilot", "googleAi"),
         "RED_PROVIDER_ID")
    kind = packet.get("kind")
    need(kind in ROUTES, "RED_TASK_KIND")
    budget = packet.get("budget")
    need(isinstance(budget, dict) and set(budget) == {"maxRequests", "maxParallel", "maxPasses"} and
         all(type(budget[key]) is int for key in budget) and
         1 <= budget["maxRequests"] <= 10 and 1 <= budget["maxParallel"] <= 3 and
         1 <= budget["maxPasses"] <= 10, "RED_TASK_BUDGET")
    workers = packet.get("workers")
    need(isinstance(workers, list) and all(isinstance(w, str) for w in workers) and
         len(workers) == len(set(workers)) and set(workers) == ROUTES.get(kind, {"lum"}) and
         len(set(workers) & SUPPORT) <= 3 and
         set(workers) <= set(cfg.get("canonicalAgents", [])), "RED_WORKER_ROUTE")
    need(packet.get("authority") == {"mutation": False, "green": False, "crown": False},
         "RED_UNTRUSTED_AUTHORITY")
    receipts = packet.get("receipts")
    need(isinstance(receipts, list) and len(receipts) <= len(steps), "RED_RECEIPT_SHAPE")
    if isinstance(receipts, list) and stage in steps:
        completed = steps[:steps.index(stage)]
        observed = []
        for item in receipts:
            if not isinstance(item, dict) or set(item) != {
                "stage", "taskId", "scopeId", "sourceRef", "status", "evidenceRefs",
            }:
                errors.append("RED_RECEIPT_FORMAT")
                continue
            observed.append(item["stage"])
            need(item["taskId"] == packet.get("taskId") and
                 item["scopeId"] == packet.get("scopeId") and item["sourceRef"] == current_sha,
                 "RED_RECEIPT_IDENTITY")
            refs = item["evidenceRefs"]
            need(item["status"] == "GREEN" and isinstance(refs, list) and bool(refs) and
                 all(isinstance(v, str) and re.fullmatch(r"sha256:[0-9a-f]{64}", v) for v in refs),
                 "RED_UNPROVED_RECEIPT")
        need(observed == completed, "RED_RECEIPT_ORDER_OR_GAP")
    if errors:
        return sorted(set(errors)), "STOP"
    if stage in ("mutation", "test", "apply", "continue", "deploy"):
        return ["AMBER_EXTERNAL_AUTHENTICATED_EXECUTOR_REQUIRED"], "STOP"
    if packet.get("providerId") == "googleAi":
        return ["AMBER_GOOGLE_DEVELOPER_API_BILLING_QUOTA_AND_IDENTITY_UNVERIFIED"], "REVIEW_ONLY"
    return [], "STRUCTURAL_CANDIDATE_ONLY"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    errors, cfg, hashes = policy_check(ROOT)
    sha = source_sha(ROOT)
    findings, decision = ([], "STRUCTURAL_CANDIDATE_ONLY")
    if args.packet is not None:
        findings, decision = assess(load_json(args.packet), sha, cfg)
    if errors:
        decision = "STOP"
    report = {
        "schema": "luhmOs.lumOrchestraAudit.v1",
        "status": "RED" if errors or any(v.startswith("RED_") for v in findings) else "AMBER_CANDIDATE",
        "decision": decision,
        "sourceRef": sha,
        "contractErrors": errors,
        "taskFindings": findings,
        "contractSha256": hashes,
        "googleDeveloperApiInvoked": False,
        "githubMutation": False,
        "renderDeployment": False,
        "providerEntitlementProven": False,
        "promotion": False,
        "crownStatus": "STOP",
    }
    output = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
    print(output, end="")
    return 1 if report["status"] == "RED" else 0

if __name__ == "__main__":
    raise SystemExit(main())

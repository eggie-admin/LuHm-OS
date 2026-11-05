"""CAST Bridge API alignment: source-only policy checks for Google/GitHub/Cloudflare.

No provider API invocation, deployment, DNS mutation, or cost approval.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = {
    "spine": "doctrine/apiSpineV1.json",
    "edge": "doctrine/cloudflareAirTrafficControllerV1.json",
    "google": "doctrine/googleAiProxyDeploymentV1.json",
    "sidecar": "doctrine/githubRenderSidecarV1.json",
    "quarantine": "doctrine/companyWideOperationalQuarantineV1.json",
}

def audit_contracts(root=ROOT):
    docs = {key: json.loads((Path(root) / path).read_text(encoding="utf-8"))
            for key, path in FILES.items()}
    issues = []
    def need(condition, name):
        if not condition:
            issues.append(name)
    spine, edge, google, sidecar, hold = (docs[x] for x in FILES)
    need(spine.get("routing", {}).get("principle") == "capabilityFirstProviderSecond",
         "CAPABILITY_FIRST")
    need(spine.get("providers", {}).get("googleAi", {}).get("adapterId") == "bigBrother",
         "GOOGLE_ADAPTER")
    need(google.get("automaticProviderCalls") is False and
         google.get("billingApproval") == "NOT_GRANTED", "GOOGLE_COST_GATE")
    need(google.get("runtimeAgentWorkerActivation") is False, "GOOGLE_WORKER_GATE")
    need(sidecar.get("githubPrimary", {}).get("canonicalRepository") ==
         "eggie-admin/LuHm-OS", "GITHUB_CANON")
    need(sidecar.get("renderSidecar", {}).get("autoDeployCanonical") is False,
         "RENDER_AUTO_DEPLOY")
    need(edge.get("authorityBoundary", {}).get("crownAuthority") is False,
         "CLOUDFLARE_CROWN")
    need(hold.get("state") == "QUARANTINED", "COMPANY_QUARANTINE")
    return {"schema": "luhmOs.castApiAlignment.v1",
            "status": "GREEN" if not issues else "RED",
            "issues": issues,
            "googleRuntimeVerified": False, "cloudflareAccountVerified": False,
            "githubCiVerified": False, "renderRuntimeVerified": False,
            "authorityGranted": False, "crownStatus": "STOP"}

def route_plan(capability):
    allowed = {
        "source": ("github", "readOnlySource"),
        "ci": ("github", "exactHeadEvidence"),
        "reasoning": ("googleAi", "requiresAuthenticatedEntitlementReceipt"),
        "conversation": ("chatGpt", "frontEndOnly"),
        "dns": ("cloudflare", "planOnly"),
        "runtime": ("render", "existingSidecar"),
    }
    if capability not in allowed:
        return {"status": "BLOCKED", "reason": "UNKNOWN_CAPABILITY"}
    provider, operation = allowed[capability]
    return {"status": "PLAN_ONLY", "capability": capability,
            "provider": provider, "operation": operation,
            "executed": False, "authorityGranted": False}

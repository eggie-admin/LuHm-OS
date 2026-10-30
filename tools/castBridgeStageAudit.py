#!/usr/bin/env python3
"""Offline fail-closed CAST stage audit. No network calls, release or mutation."""
from __future__ import annotations
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def audit(root=ROOT, stage=None):
    def read(path):
        return json.loads((root / path).read_text(encoding="utf-8"))
    p = stage if stage is not None else read("doctrine/castBridgeStageGateV1.json")
    bridge = read("doctrine/PROFESSOR_CAST_BRIDGE_V1.json")
    quarantine = read("doctrine/companyWideOperationalQuarantineV1.json")
    pipeline = read("doctrine/featureMutationPipelineV1.json")
    universal = read("doctrine/universalFourLaneV1.json")
    checks = {}
    def ck(key, condition):
        checks[key] = bool(condition)
    ck("schema", p.get("schema") == "luhmOs.castBridgeStageGate.v1")
    ck("sourceOnly", p.get("status") == "STAGED_FOR_CAST_REVIEW_SOURCE_ONLY")
    ck("repo", p.get("canonicalRepository") == "eggie-admin/LuHm-OS")
    ck("mainSha", re.fullmatch(r"[0-9a-f]{40}", str(p.get("baselineMainSha", ""))) is not None)
    ck("upstreamSha", re.fullmatch(r"[0-9a-f]{40}", str(p.get("upstreamHeadSha", ""))) is not None)
    ck("stack", p.get("upstreamPr") == 454 and p.get("stack") == list(range(447, 455)))
    source = p.get("sourceEvidence", {})
    ck("observedUpstreamCi", source.get("upstreamWorkflowCountObserved") == 20 and source.get("upstreamWorkflowsCompletedSuccessAtPinnedSha") is True)
    ck("stageCiNotInvented", source.get("stageHeadExactCI") == "PENDING_INDEPENDENT_VERIFICATION")
    ck("sourceIsNotRuntime", source.get("sourceBuildIsDeviceProof") is False and source.get("sourceBuildIsDeployProof") is False)
    host = p.get("hostEvidence", {})
    ck("hostScoped", host.get("tool") == "luhm_open_cockpit" and host.get("currentChatToolResponse") == "OBSERVED_IN_INTERACTIVE_CHAT_UNBOUND_TO_REVIEWED_SOURCE")
    ck("siteUnproven", all(host.get(x) == "UNVERIFIED" for x in ("visualMcpAppMount", "mobileAcceptance", "siteBackendVersionMatchesStage")))
    ck("castNotGreen", host.get("chatGptPluginCastGreen") is False)
    owner = p.get("ownerCast", {})
    ck("bridgeRef", owner.get("dispatchContract") == "doctrine/PROFESSOR_CAST_BRIDGE_V1.json")
    ck("noForgedCast", owner.get("milestoneSelected") is None and owner.get("ownerGitHubCommentProvided") is False and owner.get("dispatchTriggered") is False)
    ck("mainOnlyBuild", owner.get("buildRefIsCurrentMainNotThisCandidate") is True)
    trigger = bridge["trigger"]
    ck("ownerOnly", trigger["exactMainMatch"] is True and trigger["requiredActor"] == "github.repository_owner")
    ck("castSyntax", trigger["syntax"] == owner.get("requiredSyntax") and len(trigger["allowedMilestones"]) == 3)
    deployment = p.get("deployment", {})
    ck("workspaceGate", deployment.get("renderWorkspaceSelection") == "REQUIRES_OWNER_CONFIRMATION")
    ck("noDeployOrMerge", all(deployment.get(x) is False for x in ("renderDeployTriggered", "cloudflareChanged", "androidSigned", "publicArtifactPublished", "productionMerge", "agentQuarantineLifted")))
    ck("quarantine", quarantine["activeTaskWorkersAllowed"] is False and quarantine["state"] == "QUARANTINED")
    ck("pipelineNoAuto", pipeline["mutationControls"]["autoMerge"] is False and pipeline["mutationControls"]["autoDeployProduction"] is False)
    ck("mainSafe", universal["safety"]["mergeMain"] is False)
    ck("crownStop", p.get("crownStatus") == "STOP")
    failed = sorted(name for name, valid in checks.items() if not valid)
    return {"schema": "luhmOs.castBridgeStageAudit.v1", "checks": len(checks), "passed": len(checks)-len(failed), "errors": failed, "state": "SOURCE_STAGE_GATE_PASS_NOT_CAST_GREEN" if not failed else "FAIL_CLOSED", "crown": "STOP"}


if __name__ == "__main__":
    result = audit()
    print(json.dumps(result, indent=2))
    sys.exit(1 if result["errors"] else 0)

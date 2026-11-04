#!/usr/bin/env python3
"""Read-only LuHm OpenAI plugin Canon and staged-snapshot AMBER triage."""
from __future__ import annotations
import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = "doctrine/openAiCanonEscalationSnapshotV1.json"

def load(root, path):
    data = json.loads((root / path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("non-object doctrine: " + path)
    return data

def adjudicate(root, ledger, sha):
    truth = load(root, "doctrine/currentSourceTruthV3.json")
    project = load(root, "doctrine/projectChatCanonV1.json")
    quarantine = load(root, "doctrine/companyWideOperationalQuarantineV1.json")
    provider = load(root, "doctrine/openAiDeploymentV3.json")
    portable = load(root, "plugins/luhm-os/plugin.json")
    mcp = load(root, "plugins/luhm-os/mcp.json")
    chat = load(root, "doctrine/inChatExperienceV1.json")
    receipt = load(root, "doctrine/chatGptPluginRuntimeReceiptV1.json")
    harness = (root / "host/mcp/luhmHarness.py").read_text(encoding="utf-8")
    source, ext, snap = ledger.get("source", {}), ledger.get("externalObservations", {}), ledger.get("snapshot", {})
    failed = []
    def require(valid, label):
        if not valid: failed.append(label)
    require(ledger.get("schema") == "luhmOs.openAiCanonEscalationSnapshot.v1", "snapshotSchema")
    require(ledger.get("promotion") is False and ledger.get("crownStatus") == "STOP", "snapshotCrownBoundary")
    require(ledger.get("status") == "SOURCE_CANDIDATE_SNAPSHOT_STAGED", "snapshotStatusOverclaim")
    require(truth.get("schema") == "luhmOs.currentSourceTruth.v3", "canonSchema")
    require(truth.get("status") == "AMBER_PROPOSED_SEAL_OF_TRUTH", "globalGreenOverclaim")
    require(truth.get("crownStatus") == "STOP" and truth.get("promotion") is False, "globalCrownBoundary")
    require(truth.get("canonicalRepository") == source.get("repository") == "eggie-admin/LuHm-OS", "sourceAuthority")
    require(bool(re.fullmatch("[0-9a-f]{40}", source.get("baseMain", ""))), "missingBaseSHA")
    require(project.get("developmentIdentity", {}).get("machineName") == "projectPremonition", "projectIdentity")
    require(quarantine.get("state") == "QUARANTINED"
            and quarantine.get("registeredCount") == 15
            and quarantine.get("activeTaskWorkersAllowed") is False, "quarantineDrift")
    require(provider.get("architecture", {}).get("providerSideWorkersProven") is False, "providerWorkerOverclaim")
    require(portable.get("version") == source.get("portablePluginVersion"), "portableVersionDrift")
    require(mcp.get("mcpServers", {}).get("luhm", {}).get("url") == source.get("mcpUrl"), "mcpEndpointDrift")
    source_uri = chat.get("runtime", {}).get("resourceUri")
    require(source_uri == source.get("sourceResource"), "sourceResourceDrift")
    require(('UI_RESOURCE_URI = "' + str(source_uri) + '"') in harness, "sourceToolResourceDrift")
    require('APP_MIME_TYPE = "text/html;profile=mcp-app"' in harness, "mcpAppHtmlMimeDrift")
    require('"ui": {"resourceUri": UI_RESOURCE_URI' in harness, "mcpAppToolMetadataDrift")
    require('"openai/outputTemplate": UI_RESOURCE_URI' in harness, "openAiCompatAliasDrift")
    require(ext.get("connectedPluginBridge") == "REACHABLE_READ_ONLY", "bridgeClaimMismatch")
    require(ext.get("differentPluginIdentities") is True, "sitePackageIdentityConflated")
    require(ext.get("visualMount") == "UNVERIFIED", "fabricatedVisualMountProof")
    render = ext.get("renderHarness", {})
    require(render.get("deploymentState") == "LIVE"
            and bool(re.fullmatch("[0-9a-f]{40}", render.get("liveSourceRef", ""))),
            "missingRenderDeploymentEvidence")
    require(render.get("matchesGitHubMain") is False and render.get("redeploymentAuthorized") is False,
            "fabricatedRenderEquivalenceOrAuthority")
    require(snap.get("scope") == "GITHUB_REFS_ONLY_NOT_COMPLETE_BACKUP", "fabricatedFullBackup")
    refs = snap.get("verifiedBranches", [])
    require(isinstance(refs, list) and len(refs) == 3, "threeRepoSnapshotRequired")
    required = ["eggie-admin/LuHm-OS", "eggie-admin/hydra-shell-android", "eggie-admin/vue-headless-cms"]
    require([v.get("repo") for v in refs] == required, "snapshotRepoSetDrift")
    require(all(bool(re.fullmatch("[0-9a-f]{40}", v.get("sha", ""))) and
                v.get("ref", "").startswith("snapshot/openai-canon-escalation-pre-20261104-")
                for v in refs), "snapshotRefMissingExactIdentity")
    require(refs[0].get("sha") == source.get("baseMain"), "canonicalSnapshotBaseMismatch")
    require(snap.get("restoreTest") == "NOT_DONE", "falseRestoreProof")
    r = []
    def amber(code, classification, reason, next_step):
        r.append({"id":code,"class":classification,"reason":reason,
                  "nextAction":next_step,"autoFixPermitted":False})
    if source_uri != ext.get("connectedToolResource"):
        amber("siteResourceDrift","HOST_EVIDENCE",
              "Connected Site response resource differs from current GitHub Canon",
              "Verify actual deployed tool descriptors, resource fetch and UI mount before proposing a patch.")
    if receipt.get("source", {}).get("mainCommit") != source.get("baseMain"):
        amber("historicalRuntimeReceipt","HISTORICAL_EVIDENCE",
              "Runtime receipt source is historical; not today's exact main.",
              "Collect current Render deploy/source proof; do not rewrite historical receipt.")
    if render.get("liveSourceRef") != source.get("baseMain"):
        amber("renderLiveSourceLag","RUNTIME_DRIFT",
              "Render LIVE deploy is not the current GitHub main; autoDeploy disabled",
              "Run exact-source compatibility tests and request separate scoped redeploy approval.")
    amber("sourceTruthAmber","CANON_GATE","Current Canon status remains AMBER",
          "Document exact blockers; do not promote global source truth.")
    amber("hostRender","HOST_EVIDENCE","Tool data response is not UI display/touch evidence",
          "Test both ChatGPT desktop and Samsung UI, resource and CSP.")
    amber("openAiProvider","EXTERNAL_EVIDENCE","API entitlement/provider agents unverified",
          "Verify owner entitlement and authenticated scoped invocation separately.")
    amber("sqlCandidate","CANDIDATE_REVIEW","LamoS SQL authority PR #516 is draft and unmerged",
          "Independently audit PR #516 and DB backup/permissions before any merge or migration.")
    amber("privateBackup","RECOVERY_GATE","GitHub refs are not full backup and restore proof",
          "Owner-controlled encrypted local/Drive/plugin/host capture and isolated restore test.")
    amber("agentQuarantine","HUMAN_CROWN","15 workers deliberately held",
          "Use supervised proof and explicit Professor release, never automatic activation.")
    return {"schema":"luhmOs.openAiCanonEscalationEvidence.v1",
            "sourceRef":sha,"baseMain":source.get("baseMain"),
            "status":"RED_SOURCE_GATE" if failed else "AMBER_EXTERNAL_GATES_SOURCE_AUDITED",
            "sourceErrors":failed,"amberFindings":r,
            "sourceCockpitResource":source_uri,
            "observedSiteResource":ext.get("connectedToolResource"),
            "externalProofNotRerunInCi":True,
            "snapshotRefs":refs,"fullBackupVerified":False,
            "openAiInternalSystemsAudited":False,"livePluginUpdated":False,
            "autoRepairExecuted":False,"deployExecuted":False,"sqlTouched":False,
            "companyQuarantinePreserved":True,"crownStatus":"STOP"}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",default="build/openAiCanonEscalation/evidence.json")
    args=parser.parse_args()
    sha=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
    report=adjudicate(ROOT,load(ROOT,LEDGER),sha)
    path=ROOT / args.output
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":report["status"],"sourceRef":sha,
                      "errors":report["sourceErrors"],
                      "amber":[r["id"] for r in report["amberFindings"]],
                      "crownStatus":"STOP"},indent=2))
    return int(bool(report["sourceErrors"]))

if __name__=="__main__":
    raise SystemExit(main())

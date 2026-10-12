#!/usr/bin/env python3
"""Operation Titan 7: truth-preserving current-canon audit of every doctrine JSON.

Source audit only. This inventory does not promote any unproven behavior.
"""
from __future__ import annotations
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRUTH = "doctrine/currentSourceTruthV3.json"
LEDGER = "doctrine/titan7CurrentCanonReconciliationV1.json"
EXPECTED_OLD_MAIN = "dae5c07210a8a3599a202ed2a62acf430fb3a952"
PROPOSAL_MARKERS = ("PROPOSED", "CANDIDATE", "PENDING", "AMBER", "UNVERIFIED", "STAGED")
SHA = re.compile(r"^[0-9a-f]{40}$")

def load(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))

def validate(truth: dict, ledger: dict, plugin: dict, mcp: dict, titan: dict, agent: dict) -> list[str]:
    errors = []
    def check(condition, message):
        if not condition: errors.append(message)
    l = ledger
    a = l.get("auditBasis", {})
    r = l.get("runtimeEvidence", {})
    b = l.get("canonBoundaries", {})
    p = truth.get("titan7CurrentCanonReconciliation", {})
    check(truth.get("schema") == "luhmOs.currentSourceTruth.v3", "sourceTruthSchema")
    check(truth.get("status") == "AMBER_PROPOSED_SEAL_OF_TRUTH", "sourceTruthStillAmber")
    check(truth.get("promotion") is False and truth.get("crownStatus") == "STOP", "globalCrownGuard")
    check(l.get("schema") == "luhmOs.titan7CurrentCanonReconciliation.v1", "ledgerSchema")
    check(l.get("status") == "CANONICAL_AUDIT_INDEX_ONLY", "scopedAuditCanon")
    check(a.get("observedMain") == EXPECTED_OLD_MAIN, "observedMainDrift")
    check(a.get("snapshotRef") == "snapshot/titan7-current-canon-20261012-dae5c072", "snapshotRefDrift")
    check(a.get("crossRepoSnapshotVerifiedThisSession") is False, "noInventedCrossRepoProof")
    check(p.get("contract") == LEDGER and p.get("auditedBaseMain") == EXPECTED_OLD_MAIN, "sourcePointerDrift")
    check(p.get("allProposedChangesPromoted") is False, "noBulkPromotion")
    check(l.get("promotedScope", {}).get("allProposedRuntimeMutationsPromoted") is False, "noRuntimePromotion")
    check(l.get("promotion") is False and l.get("releaseAuthority") is False
          and l.get("publicationAuthority") is False and l.get("productionSigningAuthority") is False, "noReleaseAuthority")
    check(l.get("crownStatus") == "STOP" and p.get("crownStatus") == "STOP", "crownStop")
    check(plugin.get("version") == r.get("pluginVersion") == "0.5.2", "pluginVersion")
    check(mcp.get("mcpServers", {}).get("luhm", {}).get("url") == r.get("pluginMcpEndpoint")
          == "https://luhm-os-harness-green.onrender.com/mcp", "oneCurrentMcpEndpoint")
    check(r.get("pluginExactMainArtifactSourceRef") == EXPECTED_OLD_MAIN
          and r.get("renderMcpDeployedSourceRef") == EXPECTED_OLD_MAIN, "runtimeSourceIdentity")
    for field in ("chatGptHostMount", "installedPluginRefresh", "androidSamsungTouch",
                  "godotInChatRuntimeInput"):
        check(r.get(field) == "UNVERIFIED", "externalHostProofGuard:" + field)
    check(r.get("publicMcpProbeScope") == "EXTERNAL_MCP_ONLY_NOT_HOST", "probeScope")
    check(titan.get("status") == b.get("titanFinalFormSourceStatus") == "STAGED_CANDIDATE", "titanSourceBoundary")
    check(b.get("titanFinalFormExecutionModes") == ["system", "apply", "test", "all"], "titanModes")
    check(b.get("separateCastRequired") is True and b.get("noAutomaticBuild") is True, "castGuard")
    check(agent.get("requiredAgentCount") == b.get("agentRosterDefinitionCount") == 15, "agentRoster")
    check(agent.get("workingLane") == b.get("proposedWorkingLane") == "PROPOSED_ONLY", "providerPromotionGuard")
    check(agent.get("promotion") is False and agent.get("crownStatus") == "STOP", "agentGuard")
    check(b.get("liveProviderWorkerClaim") is False, "noImaginaryAgents")
    claims = l.get("openPullRequests", {})
    prs = claims.get("items", [])
    check(claims.get("count") == 11 and len(prs) == 11, "openPrCount")
    check(len({x.get("number") for x in prs}) == len(prs), "duplicatePr")
    check({x.get("number") for x in prs} == {241,236,234,216,215,214,210,209,208,207,203}, "openPrSet")
    for pr in prs:
        check(bool(SHA.fullmatch(str(pr.get("headSha", "")))), "prHeadIdentity:" + str(pr.get("number")))
        check(pr.get("mergeAuthority") is False, "noAutoMerge:" + str(pr.get("number")))
        check(pr.get("disposition","").startswith("DRAFT_"), "noUnsupportedPrPromotion:" + str(pr.get("number")))
    return errors

def proposal_fields(node, key=""):
    found = []
    if isinstance(node, dict):
        for k, v in node.items():
            path = f"{key}.{k}" if key else k
            if k in {"status", "workingLane", "runtimeProof", "crownStatus"} and isinstance(v, str):
                if any(marker in v.upper() for marker in PROPOSAL_MARKERS):
                    found.append({"key": path, "value": v})
            if isinstance(v, (dict, list)):
                found.extend(proposal_fields(v, path))
    elif isinstance(node, list):
        for index, entry in enumerate(node):
            found.extend(proposal_fields(entry, f"{key}[{index}]"))
    return found

def run() -> int:
    truth,ledger,plugin,mcp,titan,agent = (
        load(TRUTH),load(LEDGER),load("plugins/luhm-os/plugin.json"),
        load("plugins/luhm-os/mcp.json"),
        load("doctrine/operationTitan7FinalFormV1.json"),
        load("doctrine/agentSystemDeploymentV1.json"))
    errors = validate(truth, ledger, plugin, mcp, titan, agent)
    files = sorted((ROOT/"doctrine").glob("*.json"))
    inventory = []
    for file in files:
        rel = file.relative_to(ROOT).as_posix()
        try:
            payload = json.loads(file.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append("invalidDoctrineJson:" + rel + ":" + type(exc).__name__)
            continue
        signals = proposal_fields(payload)
        if signals:
            inventory.append({"file": rel,
                "sha256": hashlib.sha256(file.read_bytes()).hexdigest(),
                "rootStatus":payload.get("status") if isinstance(payload,dict) else None,
                "signals":signals[:30],"signalCount":len(signals)})
    head=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
    report={"schema":"luhmOs.titan7CurrentCanonAuditReceipt.v1",
            "auditedSourceRef":head,
            "historicalBaseline":EXPECTED_OLD_MAIN,
            "status":"GREEN_SCOPED_CANON_INDEX" if not errors else "RED_SCOPED_CANON_INDEX",
            "scope":"doctrineInventoryAndCanonicalEvidenceBoundariesOnly",
            "doctrineJsonScanned":len(files),
            "proposalBearingDoctrineFiles":len(inventory),
            "proposalInventory":inventory,
            "openPrCount":len(ledger["openPullRequests"]["items"]),
            "globalProjectGreen":False,
            "runtimeHostGreen":False,
            "castAuthorized":False,
            "releaseAuthority":False,
            "crownStatus":"STOP",
            "contractErrors":errors}
    output=ROOT/"build/titan7-current-canon/audit.json"
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({key:value for key,value in report.items() if key!="proposalInventory"},indent=2))
    return int(bool(errors))

if __name__=="__main__":
    raise SystemExit(run())

#!/usr/bin/env python3
"""Finite, fail-closed 5/12-audit observer for existing LuHm machine 4x4 + Titan7.
Fixed local source audit commands only. NEVER merges, dispatches CAST, deploys, kills
processes, trains models, opens Cloudflare/SQL, or grants agent/Crown authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
POLICY = "doctrine/machineEscalationFourByFourV1.json"
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SCRIPTS = (
    ("escalationKernel", "tools/escalationKernelAudit.py"),
    ("networkSpine", "tools/networkSpineAudit.py"),
    ("gitGovernanceSource", "tools/githubSourceGovernanceAudit.py"),
    ("quarantinedAgentContract", "tools/agentSystemDeploymentAudit.py"),
    ("operationTitan7FinalForm", "tools/operationTitan7FinalFormAudit.py"),
    ("cloudflareEdgeSource", "tools/cloudflareEdgeHardeningAudit.py"),
    ("storageTopology", "tools/storageTopologyAudit.py"),
    ("pluginPublicationSource", "tools/pluginPublicationAudit.py"),
    ("renderSidecarSource", "tools/renderEdgeStackAudit.py"),
    ("tenPassSource", "tools/tenPassHardeningAudit.py"),
    ("titan7CanonInventory", "tools/titan7CurrentCanonAudit.py"),
    ("twoHundredHardAudit", "tools/hardSystemAudit200.py"),
)
ROW_IDS = ("sanity", "propose", "reconcile", "deploy")
MATRIX_IDS = (
    ("pinSource", "readCanon", "guardAuthority", "auditDepth"),
    ("smallestCause", "candidateDiff", "rollbackPoint", "prReview"),
    ("exactHeadCi", "titanAdjudication", "noContradictions", "humanMerge"),
    ("castScope", "deployReceipt", "negativeSmoke", "professorCrown"),
)
EXTERNAL_KINDS = ("EXTERNAL_REVIEW", "HUMAN_GATED", "EXTERNAL_RUNTIME")


def read_json(path: str) -> dict:
    full = ROOT / path
    if not full.is_file() or full.is_symlink():
        raise ValueError("missing or symlink policy: " + path)
    obj = json.loads(full.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError("non-object JSON: " + path)
    return obj


def validate_policy(policy: dict, docs: dict) -> None:
    def require(ok, reason):
        if not ok:
            raise ValueError(reason)
    truth, project, covenant, machine, kernel, titan, quarantine, feature = (
        docs[k] for k in ("truth", "project", "covenant", "machine",
                          "kernel", "titan", "quarantine", "feature"))
    require(policy.get("schema") == "luhmOs.machineEscalationFourByFour.v1", "schema")
    require(policy.get("status") == "SOURCE_CANDIDATE_AUDIT_ONLY", "not candidate only")
    require(policy.get("sourceLaw") == truth.get("sourceLaw"), "source law drift")
    require(truth.get("status") == "AMBER_PROPOSED_SEAL_OF_TRUTH"
            and truth.get("promotion") is False
            and truth.get("crownStatus") == "STOP", "false global promotion")
    require(project.get("developmentIdentity", {}).get("machineName") == "projectPremonition"
            and project["developmentIdentity"].get("formerName") == "Project Hydra", "project alias drift")
    require(policy.get("target") == "Project Premonition"
            and policy.get("historicalAlias") == "Project Hydra", "new project identity drift")
    require(covenant.get("guardRail", {}).get("orderedStates") == policy.get("guardRail"),
            "eight-step covenant changed")
    require(machine.get("fourBeats") == policy.get("existingMachineAudit", {}).get("originalBeats")
            and machine.get("lanes") == policy["existingMachineAudit"].get("originalLanes")
            and machine.get("cells") == 16
            and policy["existingMachineAudit"].get("reuseWithoutModification") is True,
            "original machine 4x4 overwritten")
    require(kernel.get("fourByFourModel", {}).get("verticalTiers") == [0, 1, 2, 3], "kernel escalation tier drift")
    require(titan.get("escalationTierMap") == policy.get("titan7", {}).get("tiers")
            and titan.get("buildVersion") == 7
            and policy["titan7"].get("auditIntensityNotAuthority") is True
            and policy["titan7"].get("noFleet") is True, "Titan7 authority drift")
    require(quarantine.get("state") == "QUARANTINED"
            and quarantine.get("registeredCount") == 15
            and quarantine.get("activeTaskWorkersAllowed") is False, "agent quarantine lifted")
    controls = feature.get("mutationControls", {})
    require(controls.get("autoMerge") is False
            and controls.get("autoDeployProduction") is False
            and controls.get("autoLiftQuarantine") is False, "unsafe feature automation")
    approval = policy.get("approval", {})
    require(set(approval) == {"gitHubMainMerge","productionDeploy","cloudflareMutation","sqlDDL",
              "certIssue","modelExecution","autoBuild","cast","sign","publish","unquarantine","crown"}
            and all(x is False for x in approval.values()), "authority acquired")
    require(policy.get("promotion") is False and policy.get("crownStatus") == "STOP"
            and policy.get("externalStatus") == "UNVERIFIED_LIVE_HOST_AND_DEVICE", "false external proof")
    matrix = policy.get("releaseMatrix", {})
    rows = matrix.get("rows", [])
    require(len(rows) == 4 and tuple(x.get("id") for x in rows) == ROW_IDS
            and matrix.get("columns") == ["identity", "doctrine", "evidence", "gate"]
            and matrix.get("cells") == 16, "not four-by-four")
    for ix, row in enumerate(rows):
        cells = row.get("cells", [])
        require(len(cells) == 4 and tuple(c.get("id") for c in cells) == MATRIX_IDS[ix],
                "missing release escalation cell")
        for cell in cells:
            require(cell.get("kind") in ("SOURCE", "SOURCE_AUDIT", *EXTERNAL_KINDS)
                    and isinstance(cell.get("rule"), str) and len(cell["rule"]) >= 10,
                    "unclassified escalation cell")
    kinds = [x["kind"] for row in rows for x in row["cells"]]
    require(kinds[11] == "HUMAN_GATED" and kinds[15] == "HUMAN_GATED"
            and kinds[12] == "HUMAN_GATED" and kinds[13] == "EXTERNAL_RUNTIME", "merge/deploy release gate bypass")
    require(policy.get("auditBundles", {}).get("five", {}).get("count") == 5
            and policy["auditBundles"].get("twelve", {}).get("count") == 12
            and len(SCRIPTS) == 12, "audit count drift")
    require(policy.get("reaperStop", {}).get("status") == "PROPOSED_OPERATOR_ALIAS_NOT_EXISTING_CANON"
            and all(policy["reaperStop"].get(k) is True for k in
                    ("noKillProcess","noDeleteArtifacts","noProductionShutdown","noForcePush")),
            "reaper phrase granted destructive power")
    require(policy.get("fineTuning", {}).get("modelWeightsChange") is False
            and policy["fineTuning"].get("providerAgentActivation") is False,
            "AI tuning became provider execution")
    for _, script in SCRIPTS:
        p = ROOT / script
        require(p.is_file() and not p.is_symlink(), "missing or symlink audit source:" + script)
    require(SHA40.fullmatch(policy.get("baseMain", "")) is not None, "missing exact baseline")


def load_current() -> tuple[dict, dict]:
    policy = read_json(POLICY)
    entries = {
        "truth": "doctrine/currentSourceTruthV3.json",
        "project": "doctrine/projectChatCanonV1.json",
        "covenant": "doctrine/everlastingCovenantV1.json",
        "machine": "doctrine/machineCanonFourLoopV1.json",
        "kernel": "doctrine/escalationKernelV1.json",
        "titan": "doctrine/operationTitan7ChatTriggerV2.json",
        "quarantine": "doctrine/companyWideOperationalQuarantineV1.json",
        "feature": "doctrine/featureMutationPipelineV1.json",
    }
    docs = {k: read_json(v) for k, v in entries.items()}
    validate_policy(policy, docs)
    return policy, docs


def git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                   text=True, timeout=10).strip()


def execute(script: str, source_ref: str) -> dict:
    env = {**os.environ, "LUHM_SOURCE_REF": source_ref}
    try:
        run = subprocess.run([sys.executable, script], cwd=ROOT, env=env,
                             capture_output=True, text=True, timeout=90, check=False)
        fingerprint = hashlib.sha256((run.stdout + "\n" + run.stderr).encode("utf-8")).hexdigest()
        return {"status":"PASS" if run.returncode == 0 else "FAIL",
                "exitCode": run.returncode, "outputSha256":fingerprint}
    except (OSError, subprocess.TimeoutExpired) as e:
        return {"status":"UNKNOWN", "failureKind":type(e).__name__}


def audit(source_ref: str, depth: str, tier: int, policy: dict, runner=execute, head_reader=git_head) -> dict:
    if SHA40.fullmatch(source_ref) is None or depth not in ("five","twelve") or tier not in (0,1,2,3):
        raise ValueError("invalid source identity, depth or Titan tier")
    if head_reader() != source_ref:
        raise ValueError("exact checkout drift before audits")
    selected = SCRIPTS[:5 if depth == "five" else 12]
    results = []
    for name, script in selected:
        if head_reader() != source_ref:
            results.append({"name":name,"sourcePath":script,"status":"SOURCE_CHANGED"})
            break
        evidence = runner(script, source_ref)
        if not isinstance(evidence, dict) or evidence.get("status") not in ("PASS","FAIL","UNKNOWN"):
            raise ValueError("invalid auditor result")
        results.append({"name":name,"sourcePath":script,**evidence})
    passed = len(results)==len(selected) and all(x["status"]=="PASS" for x in results) and head_reader()==source_ref
    matrix = []
    for row in policy["releaseMatrix"]["rows"]:
        cells = []
        for cell in row["cells"]:
            # CI can only prove source checks. It must never independently validate
            # an external review, merge, provider deployment or physical device.
            state = ("PASS_SOURCE_ONLY" if passed else "BLOCKED_SOURCE") if cell["kind"] in ("SOURCE","SOURCE_AUDIT") else "WAIT_EXTERNAL_EVIDENCE"
            cells.append({"id":cell["id"],"state":state,"rule":cell["rule"],
                          "evidenceScope":"SOURCE_ONLY" if cell["kind"].startswith("SOURCE") else "EXTERNAL_REQUIRED"})
        matrix.append({"id":row["id"],"title":row["title"],"cells":cells})
    return {
        "schema":"luhmOs.machineEscalationFourByFourReceipt.v1",
        "taskId":"machineEscalationFourByFour",
        "sourceRef":source_ref,
        "baseMain":policy["baseMain"],
        "auditDepth":depth,
        "titanTier":tier,
        "titanMode":policy["titan7"]["tiers"][str(tier)],
        "titanEscalationDoesNotAuthorizeAction":True,
        "countExpected":len(selected),"countExecuted":len(results),
        "countPassed":sum(x["status"]=="PASS" for x in results),
        "auditResults":results,
        "matrix":matrix,
        "status":"GREEN_SOURCE_ONLY_EXTERNAL_HOLD" if passed else "RED_OR_UNKNOWN_SOURCE_STOP",
        "reaperStop":"HOLD_FOCUSSED_CANDIDATE_PRESERVE_EVIDENCE" if not passed else "NOT_INVOKED",
        "sourceGreen":passed,"mergedToMain":False,"runtimeDeployed":False,
        "cloudflareChanged":False,"aiFineTuned":False,"agentQuarantineReleased":False,
        "deviceProven":False,"publicRightsApproved":False,"crownStatus":"STOP"
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--source-ref", required=True)
    p.add_argument("--depth", choices=("five","twelve"), default="five")
    p.add_argument("--titan-tier", type=int, choices=(0,1,2,3), default=0)
    p.add_argument("--output", default="build/machine-escalation-four-by-four/evidence.json")
    args = p.parse_args()
    try:
        if git_head()!=args.source_ref:
            raise ValueError("source/head mismatch")
        dirty = subprocess.run(["git","status","--porcelain","--untracked-files=normal"],cwd=ROOT,
                               capture_output=True,text=True,check=True,timeout=10)
        if dirty.stdout.strip():
            raise ValueError("dirty checkout")
        policy,_ = load_current()
        result = audit(args.source_ref,args.depth,args.titan_tier,policy)
        dst = ROOT / args.output
        dst.parent.mkdir(parents=True,exist_ok=True)
        dst.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        print(json.dumps({"sourceRef":args.source_ref,"depth":args.depth,
              "status":result["status"],"countPassed":result["countPassed"],
              "countExpected":result["countExpected"],"crownStatus":"STOP"},indent=2))
        return 0 if result["sourceGreen"] else 1
    except (OSError, ValueError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        print(json.dumps({"status":"RED_SOURCE_PRECONDITION","errorType":type(exc).__name__,
                          "deployed":False,"crownStatus":"STOP"}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

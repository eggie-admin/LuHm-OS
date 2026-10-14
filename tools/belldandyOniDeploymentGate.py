#!/usr/bin/env python3
"""Deterministic Belldandy Oni deploy gate: report source configuration, never launch an agent."""
from __future__ import annotations
import argparse
import copy
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHA = re.compile(r"[0-9a-f]{40}\\Z")


def read(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def validate(policy: dict, deployment: dict, truth: dict,
             company: dict, personal: dict, plane: dict) -> list[str]:
    errors = []
    def need(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)
    need(policy.get("schema") == "luhmOs.belldandyOniDeploymentGuard.v1", "schema")
    need(policy.get("canonId") == "belldandySecretary", "identity")
    need(policy.get("boss") == "lum", "boss")
    need(policy.get("evidenceAdjudicator") == "urdDoctorGoddess", "evidence doctor")
    need(policy.get("scribe") == "koe" and policy.get("registrar") == "fumi"
         and policy.get("deterministicExecutor") == "kugi", "bounded helpers")
    need(policy.get("crownStatus") == "STOP" and not policy.get("liveOniExecutionProven")
         and policy.get("promotion") is False, "promotion drift")
    need(policy.get("taskEnvelope") == ["taskId","sourceRef","scopeId"], "envelope drift")
    need(policy.get("companyHold") == "doctrine/companyWideOperationalQuarantineV1.json"
         and policy.get("individualHold") == "doctrine/belldandyOperationalQuarantineV1.json",
         "quarantine pointers")
    need(deployment.get("requiredAgentCount") == 15 and
         "belldandySecretary" in deployment.get("requiredAgents", []), "roster")
    need(plane.get("agents", {}).get("belldandySecretary", {}).get("defaultAuthority") == "READ_ONLY",
         "agent control plane authority")
    need(truth.get("agentLayer", {}).get("belldandyOniDeploymentGuard") ==
         "doctrine/belldandyOniDeploymentGuardV1.json", "truth binding")
    need(truth.get("agentLayer", {}).get("liveProviderDeploymentProven") is False,
         "provider deployment overclaim")
    need(company.get("state") == "QUARANTINED" and
         company.get("activeTaskWorkersAllowed") is False, "company hold bypass")
    need(personal.get("state") == "QUARANTINED" and
         personal.get("verifiedDeployment") is False, "individual hold bypass")
    need(personal.get("release", {}).get("urdEvidenceReceipt") is None and
         personal.get("release", {}).get("professorApprovalReceipt") is None,
         "fictional release receipts")
    resume = policy.get("resumeRequirements", [])
    need(set(company.get("resumeBlockedUntil", [])).issubset(set(resume)),
         "company resume evidence missing")
    need("individualUrdEvidenceReceipt" in resume and
         "individualProfessorApprovalReceipt" in resume, "individual resume proof missing")
    held = policy.get("whileQuarantined", {})
    need(held.get("activeWorkers") == 0 and held.get("secretaryWork") == "DENIED"
         and held.get("agentRecruitment") is False
         and held.get("backgroundMonitoring") is False, "Oni execution leaked")
    safe = policy.get("safety", {})
    for field in ("noRecursiveRecruitment","ciGreenIsSourceOnly","renderLiveIsNotChatGptHostProof",
                  "browserVideoIsNotAppProof","noAutoMerge","noAutoDelete","noAutoPublish",
                  "noSelfCrown","privateKeysAndTokensNotCollected"):
        need(safe.get(field) is True, "missing safety: " + field)
    need(safe.get("maxParallelSupportWorkers") == 3 and
         safe.get("oneMutableSourceLane") is True, "agent budget")
    need(policy.get("deploymentSurfaces", {}).get("chatGptHost", {}).get("mayExecute") is False,
         "ChatGPT host claim")
    for surface, item in policy.get("deploymentSurfaces", {}).items():
        need(item.get("mayExecute") is False, "unproved worker activation:" + surface)
    for file in ("agents/belldandyQualityOni/SKILL.md",
                 "plugins/luhm-os/skills/belldandy-housekeeping/SKILL.md",
                 "plugins/luhm-os/skills/luhm-agent-workflow/SKILL.md"):
        body = (ROOT / file).read_text(encoding="utf-8")
        need("belldandyOniDeploymentGuardV1.json" in body, "skill canon drift:" + file)
    return errors


def packet_errors(packet: dict) -> list[str]:
    errors = []
    for key in ("taskId","scopeId"):
        if not isinstance(packet.get(key), str) or not packet[key].strip():
            errors.append("missing:" + key)
    if not isinstance(packet.get("sourceRef"), str) or not SHA.fullmatch(packet["sourceRef"]):
        errors.append("notExactSourceRef")
    if packet.get("requestedAction") not in ("inspect","audit","supervisedProbe","handoff"):
        errors.append("untrustedAction")
    if packet.get("requestedAction") == "supervisedProbe" and packet.get("mode") != "readOnly":
        errors.append("supervisedProbeMustBeReadOnly")
    for key in ("startWorkers","allowBackground","mayMutate","mayPublish","mayCrown","recruitHelpers"):
        if packet.get(key) is not False:
            errors.append("executionDenied:" + key)
    if packet.get("producer") != "lumFallback":
        errors.append("quarantinedAgentMayNotProduceActivePacket")
    if packet.get("claimedStatus") not in ("AMBER","UNKNOWN","CONFLICT"):
        errors.append("cannotGrantGreenWhileHeld")
    return errors


def self_test() -> None:
    base = {"taskId":"testA","sourceRef":"a"*40,"scopeId":"belldandyReadOnly",
            "requestedAction":"inspect","producer":"lumFallback","claimedStatus":"AMBER",
            "startWorkers":False,"allowBackground":False,"mayMutate":False,
            "mayPublish":False,"mayCrown":False,"recruitHelpers":False}
    assert packet_errors(base) == []
    for key, value in [("startWorkers", True),("mayMutate", True),("mayPublish", True),
                       ("recruitHelpers", True),("producer", "belldandySecretary"),
                       ("claimedStatus", "GREEN"),("sourceRef","main"),
                       ("requestedAction", "deploy")]:
        altered = copy.deepcopy(base)
        altered[key] = value
        assert packet_errors(altered), "forged action accepted:" + key
    print("GREEN_BELLDANDY_ONI_DEPLOY_GUARD_NEGATIVE_CONTROLS")


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--self-test",action="store_true")
    parser.add_argument("--packet",type=Path)
    args=parser.parse_args()
    if args.self_test:
        self_test()
    policy=read("doctrine/belldandyOniDeploymentGuardV1.json")
    errors=validate(policy,read("doctrine/agentSystemDeploymentV1.json"),
        read("doctrine/currentSourceTruthV3.json"),
        read("doctrine/companyWideOperationalQuarantineV1.json"),
        read("doctrine/belldandyOperationalQuarantineV1.json"),
        read("doctrine/luhmAiControlPlaneV1.json"))
    if args.packet:
        errors.extend(packet_errors(json.loads(args.packet.read_text(encoding="utf-8"))))
    for kind in ("direct","read","records","proof","patch","build","external","diagnose",
                 "research","monitor","release","art","media","mediaFactory","dictation","asset"):
        run=subprocess.run([sys.executable,str(ROOT/"tools/lumTaskRouter.py"),kind],
                           cwd=ROOT,capture_output=True,text=True,check=True)
        routed=json.loads(run.stdout)
        if routed.get("workers") or routed.get("activeResidentCabinet") or routed.get("activeOni"):
            errors.append("active worker under company quarantine:" + kind)
    print(json.dumps({"schema":"luhmOs.belldandyOniDeployAudit.v1",
        "status":"RED_SOURCE_CONTRACT" if errors else "GREEN_SOURCE_DEPLOY_GUARDS_ONLY",
        "activeOniWorkers":0,"providerRuntimeProven":False,"quarantine":"QUARANTINED",
        "checkedRouteKinds":16,"issues":errors,"crownStatus":"STOP"},indent=2))
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())

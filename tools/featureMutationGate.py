#!/usr/bin/env python3
"""Source-only feature pipeline audit. Never executes a proposed feature."""
from __future__ import annotations
import argparse
import copy
import json
import re
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SHA=re.compile("[0-9a-f]{40}")

def load(path):
    return json.loads((ROOT/path).read_text(encoding="utf-8"))

def validate(policy,truth,agents,company,personal):
    errors=[]
    def need(test,description):
        if not test: errors.append(description)
    need(policy.get("schema")=="luhmOs.featureMutationPipeline.v1","schema mismatch")
    need(policy.get("status")=="STAGED_SOURCE_ONLY","fake workflow activation")
    need(policy.get("sourceTruth")=="doctrine/currentSourceTruthV3.json","source truth mismatch")
    need(policy.get("sourceLaw")=="AI proposes. Policy authorizes. CI proves. Human promotes.","governance drift")
    need(policy.get("stages")==["sanityCheck","audit","ingest","mutation","test","apply","continue","deploy"],"covenant stage drift")
    need(set(policy.get("featurePacketRequired",[]))=={"featureId","taskId","scopeId","sourceRef","lane","targetSurface","proofRefs","crownDecision"},"packet contract drift")
    need(policy.get("canonicalRepo")=="eggie-admin/LuHm-OS","repository mismatch")
    need(truth.get("schema")=="luhmOs.currentSourceTruth.v3","source truth invalid")
    need(truth.get("agentLayer",{}).get("deployment")=="doctrine/agentSystemDeploymentV1.json","agent registry drift")
    need(agents.get("requiredAgentCount")==15,"agent count drift")
    need(company.get("state")=="QUARANTINED" and personal.get("state")=="QUARANTINED","quarantine missing")
    need(policy.get("crownStatus")=="STOP" and policy.get("liveRuntimeClaim") is False and policy.get("publicReleaseClaim") is False,"fabricated rollout")
    controls=policy.get("mutationControls",{})
    for key in ("oneMutableSourceLane","requireExact40Sha","noHiddenAsync","requiredNegativeTests"):
        need(controls.get(key) is True,"missing gate "+key)
    for key in ("autoMerge","autoDeployProduction","autoPublish","autoSignProduction","autoEnableOni","autoLiftQuarantine","automaticReleasePromotion","secretBytesInGit"):
        need(controls.get(key) is False,"consequential action shortcut "+key)
    need(controls.get("maxParallelSupportWorkers")==3,"parallel budget")
    need(controls.get("defaultLane")=="proposed","default lane")
    need(set(policy.get("supportedSurfaces",[]))==set(policy.get("scopeProofs",{})),"surface/proof drift")
    need(policy.get("lanes",{}).get("proposed",{}).get("publish") is False,"proposed public leak")
    need(policy.get("lanes",{}).get("release",{}).get("prohibitDebugCertificate") is True,"release debug signer")
    need(policy.get("completionMeaning")=="SOURCE_MUTATION_WORKFLOW_STAGED_ONLY","false full release")
    need(all(x.get("status")!="GREEN" for x in policy.get("futureFeatureQueue",[])),"future feature fictitious green")
    for reference in policy.get("governingContracts",[]):
        need(reference.startswith("doctrine/") and (ROOT/reference).is_file(),"missing canon:"+str(reference))
    return errors

def packet_errors(packet,policy):
    errors=[]
    for key in policy["featurePacketRequired"]:
        if key not in packet: errors.append("missing:"+key)
    for key in ("taskId","scopeId","featureId"):
        if not isinstance(packet.get(key),str) or not packet[key].strip(): errors.append("invalid:"+key)
    if not isinstance(packet.get("sourceRef"),str) or not SHA.fullmatch(packet.get("sourceRef","")):
        errors.append("exact source SHA missing")
    if packet.get("targetSurface") not in policy.get("supportedSurfaces",[]):
        errors.append("target surface not registered")
    if packet.get("lane")!="proposed": errors.append("nonproposed lane requires separate promotion")
    if packet.get("crownDecision")!="STOP":errors.append("automatic Crown prohibited")
    if packet.get("proofRefs") is None or not isinstance(packet.get("proofRefs"),list):
        errors.append("proofRefs list required")
    for key in ("mutateSecrets","enableWorkers","publicPublish","autoMerge","releaseSign"):
        if packet.get(key) is not False:errors.append("forbidden consequence:"+key)
    return errors

def negative_tests(policy):
    base={"featureId":"test","taskId":"t","scopeId":"s","sourceRef":"a"*40,
          "lane":"proposed","targetSurface":"source","proofRefs":[],"crownDecision":"STOP",
          "mutateSecrets":False,"enableWorkers":False,"publicPublish":False,
          "autoMerge":False,"releaseSign":False}
    assert not packet_errors(base,policy)
    for key,val in [("sourceRef","main"),("lane","release"),("targetSurface","other"),
                    ("crownDecision","PROMOTE"),("enableWorkers",True),
                    ("publicPublish",True),("autoMerge",True),("releaseSign",True)]:
        fake=copy.deepcopy(base);fake[key]=val
        assert packet_errors(fake,policy),"forged "+key+" accepted"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--self-test",action="store_true")
    ap.add_argument("--packet",type=Path)
    args=ap.parse_args()
    p=load("doctrine/featureMutationPipelineV1.json")
    errors=validate(p,load("doctrine/currentSourceTruthV3.json"),load("doctrine/agentSystemDeploymentV1.json"),
        load("doctrine/companyWideOperationalQuarantineV1.json"),load("doctrine/belldandyOperationalQuarantineV1.json"))
    if args.self_test:negative_tests(p)
    if args.packet:errors.extend(packet_errors(json.loads(args.packet.read_text(encoding="utf-8")),p))
    ref=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
    out={"schema":"luhmOs.featureMutationAudit.v1","sourceRef":ref,
         "status":"RED_CONTRACT" if errors else "GREEN_SOURCE_PIPELINE_STAGED",
         "featureExecutionProven":False,"publicReleaseProven":False,
         "quarantine":"QUARANTINED","errors":errors,"crownStatus":"STOP"}
    print(json.dumps(out,indent=2))
    raise SystemExit(1 if errors else 0)
if __name__=="__main__":main()

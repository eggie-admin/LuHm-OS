#!/usr/bin/env python3
"""Static LuHm architecture coherence gate. Runtime is an independent receipt."""
from __future__ import annotations
import argparse
import copy
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def load(p):
    return json.loads((ROOT/p).read_text(encoding="utf-8"))

def review(base, truth, mutation, agent, hold):
    errors=[]
    def require(value, message):
        if not value:errors.append(message)
    require(base.get("schema")=="luhmOs.systemArchitectureBaseline.v1","baseline schema")
    require(base.get("canonicalSourceTruth")=="doctrine/currentSourceTruthV3.json","source pointer")
    require(truth.get("canonicalRepository")=="eggie-admin/LuHm-OS","source repository")
    require(truth.get("architectureBaseline",{}).get("contract")=="doctrine/systemArchitectureBaselineV1.json","source truth architecture link")
    require(truth.get("featureMutation",{}).get("contract")=="doctrine/featureMutationPipelineV1.json","source truth mutation link")
    require(truth.get("agentLayer",{}).get("belldandyOniDeploymentGuard")=="doctrine/belldandyOniDeploymentGuardV1.json","Oni truth pointer")
    require(agent.get("belldandyOniDeployment",{}).get("contract")=="doctrine/belldandyOniDeploymentGuardV1.json","agent registry pointer")
    require(mutation.get("status")=="STAGED_SOURCE_ONLY","mutation activation")
    require(hold.get("state")=="QUARANTINED" and hold.get("activeTaskWorkersAllowed") is False,"agents wrongly activated")
    require(base.get("noFakeGreen") is True and base.get("noRuntimeClaimFromSourceCi") is True,"fabricated source authority")
    require(base.get("noAutoPublicRelease") is True and base.get("crownStatus")=="STOP","Crown drift")
    for name, layer in base.get("layers",{}).items():
        canon=layer.get("canon")
        require(isinstance(canon,str) and canon.startswith("doctrine/") and (ROOT/canon).is_file(),"missing subsystem canon:"+name)
        guard=layer.get("guard")
        if guard:require((ROOT/guard).is_file(),"missing subsystem guard:"+name)
    require(base.get("layers",{}).get("publicDistribution",{}).get("truth")=="AMBER_RELEASE_HOLD","false publication")
    require(base.get("layers",{}).get("agentMesh",{}).get("truth")=="QUARANTINED_REGISTERED","false agent execution")
    require(base.get("layers",{}).get("android",{}).get("truth")=="DEBUG_BUILD_GREEN_PHYSICAL_INSTALL_PENDING","false device install")
    return errors

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--self-test",action="store_true")
    args=ap.parse_args()
    baseline=load("doctrine/systemArchitectureBaselineV1.json")
    truth=load("doctrine/currentSourceTruthV3.json")
    mutation=load("doctrine/featureMutationPipelineV1.json")
    agent=load("doctrine/agentSystemDeploymentV1.json")
    hold=load("doctrine/companyWideOperationalQuarantineV1.json")
    issues=review(baseline,truth,mutation,agent,hold)
    if args.self_test:
        for field,new in [("noFakeGreen",False),("noAutoPublicRelease",False)]:
            bad=copy.deepcopy(baseline);bad[field]=new
            if not review(bad,truth,mutation,agent,hold):issues.append("negative control failed:"+field)
        bad=copy.deepcopy(hold);bad["activeTaskWorkersAllowed"]=True
        if not review(baseline,truth,mutation,agent,bad):issues.append("negative control failed:workerHold")
    result={"schema":"luhmOs.systemArchitectureAudit.v1","status":"RED_CONTRACT" if issues else "GREEN_SOURCE_ARCHITECTURE_STAGED","sourceRuntimeNotEquated":True,"publicReleased":False,"issues":issues,"crownStatus":"STOP"}
    print(json.dumps(result,indent=2))
    raise SystemExit(1 if issues else 0)

if __name__=="__main__":main()

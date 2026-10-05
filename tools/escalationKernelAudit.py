#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

root=Path(__file__).resolve().parents[1]
errors=[]

def need(ok,msg):
    if not ok:
        errors.append(msg)

def load(rel):
    return json.loads((root/rel).read_text(encoding="utf-8"))

kernel=load("doctrine/escalationKernelV1.json")
truth=load("doctrine/currentSourceTruthV3.json")
control=load("doctrine/luhmAiControlPlaneV1.json")
founder=load("doctrine/founderEscalationLadderV1.json")
corporate=load("doctrine/corporateEscalationProfileV1.json")
magic=load("doctrine/magicEscalationProfileV1.json")
art=load("doctrine/yumeCreativeEscalationV1.json")
titan=load("doctrine/operationTitan7ChatTriggerV2.json")

need(kernel.get("schema")=="luhmOs.escalationKernel.v1","kernel schema drift")
need([x.get("tier") for x in kernel.get("tierSemantics",[])]==[0,1,2,3],"kernel tier shape drift")
need(kernel.get("fastPathLaw",{}).get("automaticMachineContinuation") is True,"FAST_PATH continuation drift")
need(kernel.get("routing",{}).get("defaultProfile")=="doctrine/founderEscalationLadderV1.json","default profile drift")
need(kernel.get("routing",{}).get("corporateProfile")=="doctrine/corporateEscalationProfileV1.json","corporate profile drift")
need(kernel.get("routing",{}).get("magicProfile")=="doctrine/magicEscalationProfileV1.json","magic profile drift")
need(kernel.get("routing",{}).get("artProfile")=="doctrine/yumeCreativeEscalationV1.json","art profile drift")
need(kernel.get("routing",{}).get("technologyProfile")=="doctrine/operationTitan7ChatTriggerV2.json","technology profile drift")

need(founder.get("kernel")=="doctrine/escalationKernelV1.json" and founder.get("profileId")=="default","founder kernel binding drift")
need(corporate.get("kernel")=="doctrine/escalationKernelV1.json","corporate kernel binding drift")
need(magic.get("kernel")=="doctrine/escalationKernelV1.json","magic kernel binding drift")
need(art.get("kernel")=="doctrine/escalationKernelV1.json" and art.get("profileId")=="art","art kernel binding drift")
need(titan.get("kernel")=="doctrine/escalationKernelV1.json" and titan.get("profileId")=="technology","technology kernel binding drift")

es=truth.get("escalationSystem",{})
need(es.get("kernel")=="doctrine/escalationKernelV1.json","source truth kernel pointer missing")
need(es.get("resolver")=="tools/escalationKernel.py","source truth resolver pointer missing")
need(es.get("tierCount")==4 and es.get("zeroBased") is True,"source truth tier model drift")

need(control.get("inherits",{}).get("escalationKernel")=="doctrine/escalationKernelV1.json","control-plane kernel pointer missing")
need(control.get("escalation",{}).get("profiles")==["default","corporate","magic","art","technology"],"control-plane profile list drift")
need(control.get("invariants",{}).get("escalationTierDoesNotExpandAuthority") is True,"authority invariant missing")
need(control.get("invariants",{}).get("escalationPreservesTaskSourceScope") is True,"scope identity invariant missing")

resolver=root/"tools/escalationKernel.py"
need(resolver.is_file(),"resolver missing")

domains=("default","corporate","magic","art","technology")
for domain in domains:
    for tier in range(4):
        for outcome in ("working","green","blocked","unknown","conflict"):
            cp=subprocess.run(
                [sys.executable,str(resolver),"--domain",domain,"--tier",str(tier),"--outcome",outcome],
                cwd=root,capture_output=True,text=True
            )
            if cp.returncode!=0:
                errors.append(f"resolver failed: {domain}/{tier}/{outcome}: {cp.stderr.strip()}")
                continue
            payload=json.loads(cp.stdout)
            need(payload.get("domain")==domain,f"resolver domain drift: {domain}")
            need(payload.get("currentTier")==tier,f"resolver tier drift: {domain}/{tier}")
            auth=payload.get("authorityBoundary",{})
            need(auth.get("tierChangesAuthority") is False,f"tier authority leak: {domain}/{tier}")
            need(auth.get("providerMayGrantGreen") is False,f"provider GREEN leak: {domain}/{tier}")
            need(auth.get("professorRetainsCrown") is True,f"Crown drift: {domain}/{tier}")

            if outcome=="blocked":
                expected=min(3,tier+1)
                need(payload.get("nextTier")==expected,f"blocked escalation drift: {domain}/{tier}")
            elif outcome in ("unknown","conflict"):
                need(payload.get("nextTier")==tier,f"uncertain hold drift: {domain}/{tier}")
            elif outcome=="green":
                expected=max(0,tier-1) if tier>0 else 0
                need(payload.get("nextTier")==expected,f"green de-escalation drift: {domain}/{tier}")

print(json.dumps({
  "schema":"luhmOs.escalationKernelAudit.v1",
  "status":"GREEN_ESCALATION_KERNEL_CANDIDATE" if not errors else "RED_ESCALATION_KERNEL_CANDIDATE",
  "domains":list(domains),
  "tiersPerDomain":4,
  "resolverCases":len(domains)*4*5,
  "errors":errors,
  "crownStatus":"STOP"
},indent=2))
raise SystemExit(1 if errors else 0)

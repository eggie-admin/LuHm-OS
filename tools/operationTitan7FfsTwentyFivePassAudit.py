#!/usr/bin/env python3
import json
from pathlib import Path
root=Path(".")
inv=json.loads((root/"doctrine/operationTitan7InvocationV1.json").read_text())
esc=json.loads((root/"doctrine/operationTitan7EscalationV1.json").read_text())
checks=[]
def add(name,ok,detail): checks.append({"pass":len(checks)+1,"name":name,"state":"GREEN" if ok else "RED","detail":detail})
ffs=esc["tiers"]["ffs"]
add("explicitPlugin",inv["defaultWorkflow"] is False,"Titan7 is not default")
add("normalMesh",inv["normalWorkflow"]=="luhmAgentMesh","normal mesh preserved")
add("escalationContract",inv["escalationContract"]=="doctrine/operationTitan7EscalationV1.json","tier contract bound")
add("ffsPhrase",ffs["booleanPhrase"]=="For Fuck Sake!","boolean phrase sealed")
add("ffsPassCount",ffs["hardPasses"]==25,"25 hard passes")
add("ffsMode",ffs["mode"]=="sanestApproachFirstTierEscalatedAudit","first escalation mode")
add("ffsNonDestructive",ffs["autoDestructive"] is False,"audit escalation is non-destructive")
add("passMustExecute",inv["passPolicy"]["passMustExecute"] is True,"configured count is not receipt")
add("tierOwnsPassCount",inv["passPolicy"]["tierOwnsPassCount"] is True,"pass count belongs to tier")
add("unknownNotGreen",esc["escalationLaw"]["unknownIsNotGreen"] is True,"unknown stays unknown")
for p in [
 "agents/shared/ONI_PROTOCOL_V2.md","agents/lum/SKILL.md","agents/tourniquetWorkflow/SKILL.md",
 "agents/witchingHourCoding/SKILL.md","agents/urdMutationOni/SKILL.md","agents/belldandyQualityOni/SKILL.md",
 "agents/shioriCriticOni/SKILL.md","agents/kugiToolOni/SKILL.md","doctrine/aiApiBossCapabilitySpineV1.json",
 "doctrine/workflowPluginRegistryV1.json","doctrine/finalGoalMutationDirectorV1.json",
 "doctrine/codingRoleplayDirectorV1.json"
]: add("exists:"+p,(root/p).is_file(),"canonical path")
shared=(root/"agents/shared/ONI_PROTOCOL_V2.md").read_text()
add("professorCrown","Professor holds Crown" in shared,"human final authority")
add("noRecursiveRecruitment","do not recursively recruit" in shared,"bounded helper graph")
add("pluginEntry",inv["workflowPlugin"]["entryPoint"]=="$.operationTitan7","jQuery plugin entrypoint")
assert len(checks)==25, len(checks)
reds=[x for x in checks if x["state"]=="RED"]
out=root/"build/titan7-ffs-25pass/report.json";out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps({"schema":"luhmOs.operationTitan7.ffs25PassReceipt.v1","tier":"ffs","executedPasses":25,"green":25-len(reds),"red":len(reds),"passes":checks},indent=2)+"\n")
print(json.dumps({"tier":"ffs","executedPasses":25,"red":len(reds),"redNames":[x["name"] for x in reds]}))
raise SystemExit(2 if reds else 0)

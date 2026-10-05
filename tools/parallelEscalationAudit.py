#!/usr/bin/env python3
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
errors=[]

def need(ok,msg):
    if not ok:
        errors.append(msg)

titan=json.loads((root/"doctrine/operationTitan7ChatTriggerV2.json").read_text(encoding="utf-8"))
rooms=json.loads((root/"doctrine/escalationWorkflowRoomsV1.json").read_text(encoding="utf-8"))
yume=json.loads((root/"doctrine/yumeCreativeEscalationV1.json").read_text(encoding="utf-8"))
pipeline=json.loads((root/"doctrine/yumeCreativePipelineV1.json").read_text(encoding="utf-8"))

focus=titan.get("technologyAuditFocus",{})
need(focus.get("defaultTier")==0,"Titan default tier drift")
need(focus.get("fastPathFirst") is True,"Titan FAST_PATH-first drift")
need(titan.get("tierZero",{}).get("id")=="technologyFastPath","Titan tier-zero id drift")
need(titan.get("escalationTierMap",{})=={
    "technologyFastPath":0,
    "forFuckSake":1,
    "scorchedEarth":2,
    "finalForm":3
},"Titan tier map drift")
need("fineArtJudgment" in focus.get("notPrimaryFor",[]),"Titan creative-domain boundary missing")
need(titan.get("promotion") is False,"Titan promotion authority leak")
need(titan.get("crownStatus")=="STOP","Titan Crown drift")

room0=rooms.get("defaultFastPathRoom",{})
need(room0.get("tier")==0,"FAST_PATH room tier drift")
need(room0.get("id")=="technologyFastPath","FAST_PATH room id drift")
need(room0.get("required")==[],"FAST_PATH should summon nobody by default")
need(room0.get("maxParallelSupportWorkers")==3,"FAST_PATH parallelism drift")
need(room0.get("exit")=="GREEN_FOR_SCOPE_OR_ESCALATE_TO_FFS","FAST_PATH exit drift")

need(yume.get("schema")=="luhmOs.yumeCreativeEscalation.v1","Yume creative escalation schema drift")
tiers=yume.get("tiers",[])
need([x.get("tier") for x in tiers]==[0,1,2,3],"Yume creative tier numbering drift")
need([x.get("id") for x in tiers]==[
    "fineArtDevelopment",
    "commercialArtDevelopment",
    "creativeToolResearchAndDevelopment",
    "provedShowcaseAndReleaseCandidate"
],"Yume creative tier order drift")
need(tiers[0].get("lead")=="yume","fine-art lead drift")
need(tiers[1].get("lead")=="yume","commercial-art lead drift")
need(tiers[2].get("lead")=="skuldResearch" and tiers[2].get("creativeLead")=="yume","tool R&D leadership drift")
need(tiers[3].get("chair")=="lum","showcase chair drift")
need(tiers[3].get("requiredGoddesses")==["urdDoctorGoddess","skuldResearch","belldandySecretary"],"final creative cabinet drift")
need(tiers[3].get("mayPublish") is False,"Yume publish authority leak")
need(yume.get("crownStatus")=="STOP","Yume Crown drift")

parallel=yume.get("parallelToTechnologyAudit",{})
need(parallel.get("technologyTier0")=="technologyFastPath","parallel tier0 drift")
need(parallel.get("technologyTier1")=="forFuckSake","parallel tier1 drift")
need(parallel.get("technologyTier2")=="scorchedEarth","parallel tier2 drift")
need(parallel.get("technologyTier3")=="finalForm","parallel tier3 drift")

need(pipeline.get("creativeEscalation")=="doctrine/yumeCreativeEscalationV1.json","Yume pipeline escalation pointer missing")
need(pipeline.get("creativeTierDefault")==0,"Yume pipeline default tier drift")

print(json.dumps({
  "schema":"luhmOs.parallelEscalationAudit.v1",
  "status":"GREEN_PARALLEL_ESCALATION_CANDIDATE" if not errors else "RED_PARALLEL_ESCALATION_CANDIDATE",
  "technologyTiers":4,
  "creativeTiers":4,
  "errors":errors,
  "crownStatus":"STOP"
},indent=2))
raise SystemExit(1 if errors else 0)

#!/usr/bin/env python3
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
errors=[]

def need(ok,msg):
    if not ok: errors.append(msg)

model=json.loads((root/"doctrine/fourTierOperatingModelV1.json").read_text(encoding="utf-8"))
control=json.loads((root/"doctrine/luhmAiControlPlaneV1.json").read_text(encoding="utf-8"))
truth=json.loads((root/"doctrine/currentSourceTruthV3.json").read_text(encoding="utf-8"))
training=json.loads((root/"doctrine/openingDayStaffTrainingV1.json").read_text(encoding="utf-8"))
yume=json.loads((root/"doctrine/yumeCreativePipelineV1.json").read_text(encoding="utf-8"))
lum=(root/"agents/lum/SKILL.md").read_text(encoding="utf-8")
yskill=(root/"agents/yumeArtOni/SKILL.md").read_text(encoding="utf-8")

need(model.get("schema")=="luhmOs.fourTierOperatingModel.v1","schema drift")
tiers=model.get("tiers",[])
need([x.get("id") for x in tiers]==[
  "mythicRitualLayer",
  "corporateResearchAndGameDevelopment",
  "yumeProofStudio",
  "partnerPublicShowcase"
],"tier order drift")

t1,t2,t3,t4=tiers
need(t1.get("lead")=="lum","tier1 Lum lead drift")
need(t1.get("lumTitle",{}).get("ritualTitle")=="supremePriestess","Lum supreme-priestess drift")
need(t1.get("lumTitle",{}).get("mythicRank")=="supremeWitch","Lum supreme-witch drift")
need(t2.get("lead")=="lum","tier2 Lum lead drift")
need(t2.get("lumTitle",{}).get("corporateTitle")=="president","Lum president drift")
need(t3.get("lead")=="yume" and t3.get("reportsTo")=="lum","Yume studio reporting drift")
need(t3.get("mayPublish") is False,"Yume publish authority leak")
need(t3.get("mayGrantGreen") is False,"Yume GREEN authority leak")
need(t4.get("lead")=="lum" and t4.get("creativePresenter")=="yume","partner showcase leadership drift")
need(t4.get("legalInvestorClaim") is False,"legal investor overclaim")
need(t4.get("partnerFeedbackMayChangeAuthority") is False,"partner feedback authority leak")
need(t4.get("publicReleaseRequiresSeparateGate") is True,"public release gate missing")

need(model.get("lumContinuity",{}).get("sameAgentAcrossAllTiers") is True,"Lum continuity drift")
need(model.get("lumContinuity",{}).get("authorityDoesNotMultiplyByTier") is True,"tier authority multiplication")
need(model.get("yumeContinuity",{}).get("proofRule")=="visualizationMayExplainEvidenceButNeverReplaceEvidence","Yume proof rule drift")

need(control.get("inherits",{}).get("fourTierOperatingModel")=="doctrine/fourTierOperatingModelV1.json","control pointer missing")
need(control.get("invariants",{}).get("oneAuthorityChainAcrossFourTiers") is True,"one-chain invariant missing")
need(truth.get("agentLayer",{}).get("fourTierOperatingModel")=="doctrine/fourTierOperatingModelV1.json","source truth pointer missing")
need(training.get("advancedLecture",{}).get("fourTierOperatingModel")=="doctrine/fourTierOperatingModelV1.json","training pointer missing")
need(yume.get("fourTierOperatingModel")=="doctrine/fourTierOperatingModelV1.json","Yume pipeline pointer missing")
need("Four-tier operating continuity" in lum,"Lum skill missing four-tier section")
need("Proof-of-concept studio role" in yskill,"Yume skill missing proof-studio section")

print(json.dumps({
  "schema":"luhmOs.fourTierOperatingModelAudit.v1",
  "status":"GREEN_FOUR_TIER_OPERATING_MODEL_CANDIDATE" if not errors else "RED_FOUR_TIER_OPERATING_MODEL_CANDIDATE",
  "tiers":4,
  "errors":errors,
  "crownStatus":"STOP"
},indent=2))
raise SystemExit(1 if errors else 0)

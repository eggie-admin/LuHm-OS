#!/usr/bin/env python3
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
errors=[]

def load(rel):
    return json.loads((root/rel).read_text(encoding="utf-8"))

def need(ok,msg):
    if not ok:
        errors.append(msg)

sync=load("doctrine/fourTierEscalationSyncV1.json")
kernel=load("doctrine/escalationKernelV1.json")
founder=load("doctrine/founderEscalationLadderV1.json")
corporate=load("doctrine/corporateEscalationProfileV1.json")
magic=load("doctrine/magicEscalationProfileV1.json")
art=load("doctrine/yumeCreativeEscalationV1.json")
titan=load("doctrine/operationTitan7ChatTriggerV2.json")
rooms=load("doctrine/escalationWorkflowRoomsV1.json")
operating=load("doctrine/fourTierOperatingModelV1.json")
opening=load("doctrine/openingDayStaffTrainingV1.json")
truth=load("doctrine/currentSourceTruthV3.json")
control=load("doctrine/luhmAiControlPlaneV1.json")
bel=(root/"agents/belldandyQualityOni/SKILL.md").read_text(encoding="utf-8")
urd=(root/"agents/urdMutationOni/SKILL.md").read_text(encoding="utf-8")
shared=(root/"agents/shared/ESCALATION_KERNEL_V1.md").read_text(encoding="utf-8")

need(sync.get("schema")=="luhmOs.fourTierEscalationSync.v1","sync schema drift")
need([x.get("tier") for x in sync.get("tiers",[])]==[0,1,2,3],"sync tier shape drift")
pair=sync.get("syncPair",{})
need(pair.get("evidenceDoctor")=="urdDoctorGoddess","Urd sync identity drift")
need(pair.get("continuitySecretary")=="belldandySecretary","Belldandy sync identity drift")
need(pair.get("chair")=="lum","Lum chair drift")
need(pair.get("finalAuthority")=="Professor","Professor authority drift")
need(pair.get("hiddenAsyncExecution") is False,"hidden async leak")
need(pair.get("pairMayGrantGreen") is False,"pair GREEN authority leak")
need(pair.get("pairMayGrantCrown") is False,"pair Crown authority leak")
rec=sync.get("reconciliation",{})
need(rec.get("sameTaskSourceScopeRequired") is True,"identity continuity missing")
need(rec.get("urdBelldandyConflict")=="CONFLICT","conflict law drift")
need(rec.get("deterministicRedAction")=="STOP_ADVANCEMENT","RED stop law drift")
need(rec.get("tierChangeMayExpandAuthority") is False,"tier authority leak")

for name,doc in {
    "kernel":kernel,"founder":founder,"corporate":corporate,"magic":magic,
    "art":art,"technology":titan,"rooms":rooms,"operating":operating
}.items():
    need(doc.get("fourTierSync")=="doctrine/fourTierEscalationSyncV1.json",f"{name} sync pointer drift")

need(rooms.get("transitionSync",{}).get("requiredOnTierChange") is True,"room transition sync not required")
need(rooms.get("transitionSync",{}).get("hiddenAsyncExecution") is False,"room hidden async leak")
open_sync=opening.get("fourTierEscalationSync",{})
need(open_sync.get("contract")=="doctrine/fourTierEscalationSyncV1.json","opening-day sync pointer missing")
need(open_sync.get("trainers")==["urdDoctorGoddess","belldandySecretary"],"opening-day trainer pair drift")
es=truth.get("escalationSystem",{})
need(es.get("fourTierSync")=="doctrine/fourTierEscalationSyncV1.json","source-truth sync pointer missing")
need(es.get("syncPair")==["urdDoctorGoddess","belldandySecretary"],"source-truth pair drift")
need(es.get("syncPairMayGrantGreen") is False and es.get("syncPairMayGrantCrown") is False,"source-truth authority leak")
need(control.get("inherits",{}).get("fourTierEscalationSync")=="doctrine/fourTierEscalationSyncV1.json","control-plane sync pointer missing")
need(control.get("invariants",{}).get("urdBelldandyTierTransitionSync") is True,"control-plane sync invariant missing")
need(control.get("invariants",{}).get("escalationSyncDoesNotExpandAuthority") is True,"control-plane authority invariant missing")
need(control.get("invariants",{}).get("escalationConflictHoldsCurrentTier") is True,"control-plane conflict invariant missing")
need("## Four-tier escalation sync" in bel,"Belldandy sync practice missing")
need("## Four-tier escalation sync" in urd,"Urd sync practice missing")
need("## Urd + Belldandy tier-transition sync" in shared,"shared sync practice missing")

print(json.dumps({
    "schema":"luhmOs.fourTierEscalationSyncAudit.v1",
    "status":"GREEN_FOUR_TIER_URD_BELLDANDY_SYNC" if not errors else "RED_FOUR_TIER_URD_BELLDANDY_SYNC",
    "tiers":[0,1,2,3],
    "profiles":["default","corporate","magic","art","technology"],
    "syncPair":["urdDoctorGoddess","belldandySecretary"],
    "scope":"source contract only",
    "runtimeExecutionProof":False,
    "physicalProof":False,
    "promotion":False,
    "crownStatus":"STOP",
    "errors":errors
},indent=2))
raise SystemExit(1 if errors else 0)

#!/usr/bin/env python3
from __future__ import annotations
import json, pathlib, sys

root=pathlib.Path(__file__).resolve().parents[1]
errors=[]

def load(rel):
    return json.loads((root/rel).read_text(encoding="utf-8"))

def need(ok,msg):
    if not ok: errors.append(msg)

reconcile=load("doctrine/openPrReconciliationV2.json")
truth=load("doctrine/currentSourceTruthV3.json")
activity=load("doctrine/chatActivityPresentationV1.json")
intent=load("doctrine/humanCenteredIntentRouterV2.json")
titan=load("doctrine/operationTitan7ChatTriggerV2.json")
roleplay=load("doctrine/codingRoleplayDirectorV2.json")
pet=load("doctrine/characterPetPresentationV1.json")
study=load("doctrine/professorOldMagicStudyMeshV2.json")
deploy=load("doctrine/professorOldMagicStudyDeployV2.json")
examReceipt=load("doctrine/professorOldMagicLumExamReceiptV1.json")

need(reconcile.get("status")=="PROPOSED_SOURCE_ONLY","reconciliation must remain proposed")
need(reconcile.get("law",{}).get("mergeStaleWholeBranch") is False,"stale whole-branch merge must stay false")
need(reconcile.get("law",{}).get("portNovelCompatibleDelta") is True,"novel compatible delta law missing")
need(len(reconcile.get("portedOrAdapted",[]))==5,"ported/adapted PR count drift")
need(len(reconcile.get("supersededOrHistorical",[]))==16,"superseded/historical PR count drift")
need(activity.get("aggregation",{}).get("oneVisibleEventPerSemanticClass") is True,"activity aggregation missing")
need(activity.get("aggregation",{}).get("repeatedPerTargetEvents") is False,"per-target activity spam must stay false")
need(intent.get("likeTermFold")=="doctrine/chatLikeTermFoldV1.json","intent router not bound to like-term fold")
need(intent.get("operationTitan7")=="doctrine/operationTitan7ChatTriggerV2.json","intent router Titan binding drift")
need(titan.get("escalationOrder")==["forFuckSake","scorchedEarth","finalForm"],"Titan escalation order drift")
need(titan.get("escalations",{}).get("forFuckSake",{}).get("passTarget")==25,"FFS tier must be 25-pass")
need(titan.get("escalations",{}).get("scorchedEarth",{}).get("passTarget")==50,"Scorched Earth tier must be 50-pass")
need("noTitanFleet" in titan.get("laws",[]),"Titan fleet must remain retired")
need(roleplay.get("bubbleLaw",{}).get("bubbleCannotEstablishGreen") is True,"roleplay bubble truth boundary drift")
need(roleplay.get("progressLaw",{}).get("repeatedLikeTermBubbles") is False,"roleplay like-term spam drift")
need(pet.get("petSystem",{}).get("authority")=="presentationOnly","pet layer authority drift")
need(study.get("classLibrary",{}).get("driveReceiptProven") is True,"study mesh Drive proof must be present after sealed exam upload")
need(study.get("classLibrary",{}).get("currentLearningReceipt")=="doctrine/professorOldMagicLumExamReceiptV1.json","study mesh receipt pointer drift")
need(examReceipt.get("status")=="SEALED_STUDY_LIBRARY_PROOF","study exam receipt is not sealed proof")
need(examReceipt.get("driveZipRoundTripVerified") is True,"study exam Drive ZIP round-trip not proven")
need(examReceipt.get("driveBase64TransportVerified") is True,"study exam Drive Base64 transport not proven")
need(examReceipt.get("zipSha256")=="04cdfdadf9e07a860398e8035342307586f1dd0c8e2a9cf83f321d9f4f7c2457","study exam sealed ZIP identity drift")
need(set(deploy.get("load",[]))=={"lum","urdDoctorGoddess","belldandySecretary","skuldResearch"},"study deploy canonical agent set drift")
need(truth.get("openPrReconciliation",{}).get("contract")=="doctrine/openPrReconciliationV2.json","source truth reconciliation pointer missing")
need(truth.get("experienceLayer",{}).get("intentRouter")=="doctrine/humanCenteredIntentRouterV2.json","experience intent router pointer missing")
need(truth.get("studyLayer",{}).get("driveReceiptProven") is True,"source truth missing proven study Drive receipt")
need(truth.get("studyLayer",{}).get("latestReceipt")=="doctrine/professorOldMagicLumExamReceiptV1.json","source truth study receipt pointer drift")
need(truth.get("studyLayer",{}).get("promotionScope")=="professorOldMagicStudyLibraryOnly","study promotion scope widened unexpectedly")

for rel in [
  "frontEnd/jquery/luhm.codingRoleplay.js",
  "scripts/game/activityLoading.gd",
  "scripts/game/adventureDirector.gd",
  "scripts/game/scriptedChatDirector.gd",
  "agents/humanCenteredIntentRouter/SKILL.md",
  "agents/professorOldMagicStudy/SKILL.md",
]:
    need((root/rel).is_file(),f"missing reconciled source: {rel}")

index=(root/"frontEnd/index.html").read_text(encoding="utf-8")
app=(root/"frontEnd/app.js").read_text(encoding="utf-8")
need("jquery/luhm.codingRoleplay.js" in index,"roleplay runtime not loaded")
need("luhm:magic:roleplay:activate" in app,"magic roleplay app binding missing")
need("UNKNOWN_UNTIL_EXACT_EXECUTION_RECEIPT" in app,"vendor debug truth boundary missing from app")

if errors:
    print(json.dumps({"status":"RED_OPEN_PR_RECONCILIATION","errors":errors},indent=2))
    raise SystemExit(1)

print(json.dumps({
  "status":"GREEN_OPEN_PR_RECONCILIATION_SOURCE_CANDIDATE",
  "portedOrAdapted":5,
  "supersededOrHistorical":15,
  "staleWholeBranchMerge":False,
  "providerFanoutPerTarget":False,
  "crownStatus":"STOP"
},indent=2))

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

experience=json.loads((root/"doctrine/inChatExperienceV1.json").read_text(encoding="utf-8"))
precision=json.loads((root/"doctrine/chatPrecisionCommandV1.json").read_text(encoding="utf-8"))
after_hours=json.loads((root/"doctrine/afterHoursExperienceV1.json").read_text(encoding="utf-8"))
need(experience.get("schema")=="luhmOs.inChatExperience.v1","schema drift")
need(experience.get("boss")=="lum","Lum boss drift")
need(experience.get("authority")=="Professor","Professor authority drift")

sources=experience.get("sources",{})
expected={
  "intentRouter":"doctrine/humanCenteredIntentRouterV2.json",
  "activity":"doctrine/chatActivityPresentationV1.json",
  "roleplay":"doctrine/codingRoleplayDirectorV2.json",
  "pets":"doctrine/characterPetPresentationV1.json",
  "loadingSprites":"doctrine/agentLoadingSpriteManifestV1.json",
  "agentControl":"doctrine/luhmAiControlPlaneV1.json",
  "sourceTruth":"doctrine/currentSourceTruthV3.json",
  "crownFlow":"doctrine/chatGptPluginCrownFlowV1.json",
  "runtimeReceipt":"doctrine/chatGptPluginRuntimeReceiptV1.json",
  "openingDayStaffTraining":"doctrine/openingDayStaffTrainingV1.json",
  "apiSpine":"doctrine/apiSpineV1.json",
  "trafficController":"doctrine/cloudflareAirTrafficControllerV1.json",
  "chatPrecisionCommand":"doctrine/chatPrecisionCommandV1.json",
  "afterHours":"doctrine/afterHoursExperienceV1.json"
}
need(sources==expected,"source map drift")
for rel in expected.values():
    need((root/rel).is_file(),f"missing source {rel}")

runtime=experience.get("runtime",{})
need(runtime.get("tool")=="luhm_open_cockpit","tool binding drift")
need(runtime.get("resourceUri")=="ui://luhm-os/cockpit-v2.html","resource URI drift")
need(runtime.get("surface")=="mcp-app","surface drift")
need(runtime.get("panels")==["sourceTruth","crownFlow","openingDay","apiSpine","airTraffic","activeCast","activity","roleplay","petDock","commandCapsule","precisionCommands","afterHours","godotHandoff"],"panel contract drift")
need(runtime.get("godotEmbeddingInChat") is False,"Godot embedding boundary drift")

authority=experience.get("authorityBoundary",{})
for key in ("mutationAuthority","greenAuthority","publicationAuthority","signingAuthority","crownAuthority"):
    need(authority.get(key) is False,f"authority leak: {key}")
need(authority.get("readOnlyPlugin") is True,"read-only plugin law missing")

proof=experience.get("proof",{})
for key in ("sourceConfiguredDoesNotEqualLiveHostProof","toolResultMustExposeThisSchema","chatResourceMustMatchResourceUri","standaloneHarnessMustExposeThisSchema"):
    need(proof.get(key) is True,f"proof contract missing: {key}")

module=(root/"host/mcp/luhmHarness.py").read_text(encoding="utf-8")
widget=(root/"host/harness/widget.html").read_text(encoding="utf-8")
need('UI_RESOURCE_URI = "ui://luhm-os/cockpit-v2.html"' in module,"harness still on cockpit v1")
need('"schema": "luhmOs.inChatExperiencePayload.v1"' in module,"tool payload schema missing")
need('"experience": experience' in module,"tool/config do not expose experience")
need('id="experienceSchema"' in widget and 'id="experiencePanels"' in widget,"widget does not render experience")
need('id="crownGate"' in widget and 'id="crownAction"' in widget,"widget does not render Crown flow")
need('id="openingDay"' in widget and 'id="installModel"' in widget,"widget does not render opening-day state")
need('"openingDay": opening_day' in module,"harness does not expose opening-day training")
need('"apiSpine": api_spine' in module and '"trafficController": traffic_controller' in module,"harness does not expose API spine/traffic controller")
need('id="apiSpine"' in widget and 'id="airTraffic"' in widget,"widget does not render API spine/traffic controller")
need('"crownFlow": crown_flow' in module and '"runtimeReceipt": runtime_receipt' in module,"harness does not expose Crown flow receipts")
need('"precisionCommands": precision_command' in module,"harness does not expose precision command contract")
need('latest?.precisionCommands?.examples' in widget,"widget does not consume precision command payload")
need('const precisionCommands=[' not in widget,"widget still hard-codes precision commands")
need(any(row.get("debugVerb")=="HELP" and row.get("camelHump")=="showHelp" for row in precision.get("examples",[])),"HELP precision command missing")
need(len(precision.get("examples",[]))>=9,"precision command registry unexpectedly shrank")
need(after_hours.get("schema")=="luhmOs.afterHoursExperience.v1","After Hours schema drift")
boundary=after_hours.get("modeBoundary",{})
need(boundary.get("defaultMode")=="normalChat","After Hours must default outside fiction")
need(boundary.get("explicitEntryRequired") is True,"After Hours explicit entry law missing")
need(boundary.get("normalChatNeverAutoEnters") is True,"normal chat may auto-enter After Hours")
need(boundary.get("exitReturnsToNormalChat") is True,"EXIT boundary missing")
fiction=after_hours.get("fictionBoundary",{})
need(fiction.get("fictionalSceneStateCannotMutateRealWorld") is True,"fiction may mutate real world")
need(fiction.get("roleplayCannotGrantAuthority") is True,"roleplay authority leak")
need(fiction.get("allCharactersAdults") is True,"adult-cast contract missing")
fast=after_hours.get("fastMudTurn",{})
need(fast.get("status")=="CANDIDATE_SOURCE_ONLY","fast MUD candidate scope drift")
need("IN SCENE" in fast.get("chatEntryPrefixes",[]),"fast MUD in-scene entry missing")
need("OOC" in fast.get("chatExitPrefixes",[]),"fast MUD OOC exit missing")
pace=fast.get("pacing",{})
need(pace.get("actionFirst") is True,"fast MUD lost immediate action")
need(pace.get("maxWordsPerRoutineTurn",1000)<=150,"fast MUD response budget drift")
need(pace.get("maxSuggestedChoices",1000)<=3,"fast MUD choices too many")
need(pace.get("noRoutineQuestWidgets") is True,"fast MUD UI slowdown regression")
need(pace.get("showQuestInventoryOnlyWhenChangedOrRequested") is True,"fast MUD state flood regression")
art=fast.get("art",{})
need(art.get("textTurnsNeverBlockedOnImageGeneration") is True,"fast MUD art blocking regression")
need(art.get("doNotSearchForImagesOnRoutineActions") is True,"fast MUD routine image lookup regression")
need(art.get("keepTextDialogueOutsideRenderedArt") is True,"fast MUD baked dialogue regression")
need(fast.get("boundaries",{}).get("oocStopsSceneImmediately") is True,"OOC boundary regression")
need(fast.get("boundaries",{}).get("roleplayNeverGrantsCrown") is True,"Crown boundary regression")
need('"afterHours": after_hours' in module,"harness does not expose After Hours contract")
need('id="afterHoursShell"' in widget and 'id="afterHoursEnter"' in widget,"After Hours shell missing")
need('afterHoursState="OUTSIDE"' in widget,"After Hours does not default OUTSIDE")
need('setAfterHoursMode("OUTSIDE")' in widget,"After Hours boot boundary missing")
cli=subprocess.run([sys.executable,str(root/"tools/luhm.py"),"-h"],capture_output=True,text=True)
need(cli.returncode==0 and "HELP" in cli.stdout and "CONTINUE" in cli.stdout,"luhm -h does not expose precision command vocabulary")

print(json.dumps({
  "schema":"luhmOs.inChatExperienceAudit.v1",
  "status":"greenInChatExperienceCandidate" if not errors else "redInChatExperienceCandidate",
  "resourceUri":runtime.get("resourceUri"),
  "panelCount":len(runtime.get("panels",[])),
  "liveHostProof":False,
  "crownStatus":"STOP",
  "errors":errors
},indent=2))
raise SystemExit(1 if errors else 0)

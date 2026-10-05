#!/usr/bin/env python3
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
errors=[]

def need(ok,msg):
    if not ok:
        errors.append(msg)

experience=json.loads((root/"doctrine/inChatExperienceV1.json").read_text(encoding="utf-8"))
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
  "chatPrecisionCommand":"doctrine/chatPrecisionCommandV1.json"
}
need(sources==expected,"source map drift")
for rel in expected.values():
    need((root/rel).is_file(),f"missing source {rel}")

runtime=experience.get("runtime",{})
need(runtime.get("tool")=="luhm_open_cockpit","tool binding drift")
need(runtime.get("resourceUri")=="ui://luhm-os/cockpit-v2.html","resource URI drift")
need(runtime.get("surface")=="mcp-app","surface drift")
need(runtime.get("panels")==["sourceTruth","crownFlow","openingDay","apiSpine","airTraffic","activeCast","activity","roleplay","petDock","commandCapsule","precisionCommands","godotHandoff"],"panel contract drift")
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

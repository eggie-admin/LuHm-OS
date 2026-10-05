#!/usr/bin/env python3
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
errors=[]
def need(ok,msg):
    if not ok: errors.append(msg)

flow=json.loads((root/"doctrine/chatGptPluginCrownFlowV1.json").read_text())
receipt=json.loads((root/"doctrine/chatGptPluginRuntimeReceiptV1.json").read_text())
milestone=json.loads((root/"doctrine/chatGptPluginMilestoneV2.json").read_text())
truth=json.loads((root/"doctrine/currentSourceTruthV3.json").read_text())

need(flow.get("schema")=="luhmOs.chatGptPluginCrownFlow.v1","flow schema drift")
need(flow.get("authority")=="Professor","Professor authority drift")
need(flow.get("boss")=="lum","Lum boss drift")
need(flow.get("transitionLogic",{}).get("currentGate")=="chatGptMetadataRefresh","current gate drift")
need(flow.get("rules",{}).get("noAutomaticCrown") is True,"automatic Crown leak")
need(flow.get("rules",{}).get("deterministicRedStops") is True,"RED stop missing")
need(flow.get("rules",{}).get("unknownNeverBecomesGreen") is True,"UNKNOWN green leak")

gates=flow.get("gates",[])
ids=[g.get("id") for g in gates]
expected=["candidateCi","mainPromotion","runtimeDeploy","chatGptMetadataRefresh","toolDiscovery","cockpitInvocation","hostEvaluation","crownReady","professorCrown"]
need(ids==expected,"gate order drift")
need(all(g.get("state")=="PROVED" for g in gates[:3]),"machine proof gates must be proved")
need(all(g.get("state")=="PENDING" for g in gates[3:]),"host/Crown gates must remain pending")
need(receipt.get("runtimeProof",{}).get("deployedCommit")=="d88f5ff23d580327a10f585d8b23b6beebc21aa4","runtime SHA drift")
need(receipt.get("runtimeProof",{}).get("deployStatus")=="succeeded","runtime deploy not proved")
need(receipt.get("runtimeProof",{}).get("harnessHttpStatus")==200,"harness HTTP proof missing")
need(receipt.get("chatGptHostProof",{}).get("cockpitV2Discovered")=="PENDING","host proof overclaim")
need(receipt.get("crownStatus")=="STOP","receipt Crown overclaim")
need(milestone.get("crownFlow")=="doctrine/chatGptPluginCrownFlowV1.json","milestone flow pointer missing")
need(milestone.get("runtimeReceipt")=="doctrine/chatGptPluginRuntimeReceiptV1.json","milestone receipt pointer missing")
need(truth.get("pluginLayer",{}).get("renderRuntime")=="GREEN","source truth runtime proof missing")
need(truth.get("pluginLayer",{}).get("chatGptHost")=="AMBER","source truth host must remain AMBER")
need(truth.get("pluginLayer",{}).get("crownStatus")=="STOP","source truth Crown overclaim")

print(json.dumps({
  "schema":"luhmOs.chatGptPluginCrownFlowAudit.v1",
  "status":"GREEN_CROWN_FLOW_SOURCE" if not errors else "RED_CROWN_FLOW_SOURCE",
  "currentGate":flow.get("transitionLogic",{}).get("currentGate"),
  "renderRuntime":"GREEN",
  "chatGptHost":"AMBER",
  "crownStatus":"STOP",
  "errors":errors
},indent=2))
raise SystemExit(1 if errors else 0)

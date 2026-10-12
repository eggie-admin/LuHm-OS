#!/usr/bin/env python3
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
errors=[]
def need(ok,msg):
    if not ok: errors.append(msg)

flow=json.loads((root/"doctrine/chatGptPluginCrownFlowV1.json").read_text())
receipt=json.loads((root/"doctrine/chatGptPluginRuntimeReceiptV1.json").read_text())
package=json.loads((root/"doctrine/publicPluginPackageReceiptV1.json").read_text())
milestone=json.loads((root/"doctrine/chatGptPluginMilestoneV2.json").read_text())
truth=json.loads((root/"doctrine/currentSourceTruthV3.json").read_text())

need(flow.get("schema")=="luhmOs.chatGptPluginCrownFlow.v1","flow schema drift")
need(flow.get("authority")=="Professor","Professor authority drift")
need(flow.get("boss")=="lum","Lum boss drift")
need(flow.get("transitionLogic",{}).get("currentGate")=="publicPackageUpload","current gate drift")
need(flow.get("rules",{}).get("noAutomaticCrown") is True,"automatic Crown leak")
need(flow.get("rules",{}).get("deterministicRedStops") is True,"RED stop missing")
need(flow.get("rules",{}).get("unknownNeverBecomesGreen") is True,"UNKNOWN green leak")

gates=flow.get("gates",[])
ids=[g.get("id") for g in gates]
expected=["candidateCi","mainPromotion","runtimeDeploy","publicPackageBuild","publicPackageUpload","automatedPackageChecks","mcpConnectAndDomainVerify","currentToolScan","reviewMaterials","reviewSubmission","reviewApproval","professorPublish","directorySearch","publicInvocation","crownReady","professorCrown"]
need(ids==expected,"gate order drift")
need(all(g.get("state")=="PROVED" for g in gates[:4]),"machine proof gates must be proved")
need(all(g.get("state")=="PENDING" for g in gates[4:]),"portal/public/Crown gates must remain pending")
need(receipt.get("runtimeProof",{}).get("deployedCommit")=="14ee43d22fafe0fcaaa1b1fb427c9b1dd42a0fda","runtime SHA drift")
need(receipt.get("runtimeProof",{}).get("deployStatus")=="succeeded","runtime deploy not proved")
need(receipt.get("runtimeProof",{}).get("harnessHttpStatus")==200,"harness HTTP proof missing")
need(receipt.get("chatGptHostProof",{}).get("cockpitV2Discovered")=="PENDING","host proof overclaim")
need(package.get("status")=="GREEN_UPLOAD_PACKAGE","public package must be GREEN")
need(package.get("artifact",{}).get("sha256")=="1e74d830b5d8381112ae857a00630c69aedff8957466304630bded952a7dbd09","package SHA drift")
need(package.get("plugin",{}).get("version")=="0.5.2","plugin package version stale")
need(package.get("sourceRef")=="dae5c07210a8a3599a202ed2a62acf430fb3a952","package sourceRef drift")
need(package.get("artifact",{}).get("bytes")==16120,"package size drift")
need(package.get("buildEvidence",{}).get("githubActionRunId")==38217231216,"package build run drift")
need(package.get("publicationAuthority") is False and package.get("crownStatus")=="STOP","package authority overclaim")
need(receipt.get("crownStatus")=="STOP","receipt Crown overclaim")
need(milestone.get("crownFlow")=="doctrine/chatGptPluginCrownFlowV1.json","milestone flow pointer missing")
need(milestone.get("runtimeReceipt")=="doctrine/chatGptPluginRuntimeReceiptV1.json","milestone receipt pointer missing")
need(truth.get("pluginLayer",{}).get("renderRuntime")=="GREEN","source truth runtime proof missing")
need(truth.get("pluginLayer",{}).get("chatGptHost")=="AMBER","source truth host must remain AMBER")
need(truth.get("pluginLayer",{}).get("publicPackage")=="GREEN","source truth package proof missing")
need(truth.get("pluginLayer",{}).get("directoryPublication")=="PENDING","directory publication overclaim")
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

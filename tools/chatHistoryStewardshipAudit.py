#!/usr/bin/env python3
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
errors=[]

def need(ok,msg):
    if not ok:
        errors.append(msg)

hist=json.loads((root/"doctrine/chatHistoryStewardshipV1.json").read_text(encoding="utf-8"))
ctl=json.loads((root/"doctrine/luhmAiControlPlaneV1.json").read_text(encoding="utf-8"))
chat=json.loads((root/"doctrine/projectChatCanonV1.json").read_text(encoding="utf-8"))
bel=(root/"agents/belldandyQualityOni/SKILL.md").read_text(encoding="utf-8")
boot=(root/"agents/projectChatBootstrap/SKILL.md").read_text(encoding="utf-8")

need(hist.get("schema")=="luhmOs.chatHistoryStewardship.v1","schema drift")
need(hist.get("owner")=="belldandySecretary","owner drift")
need(hist.get("boss")=="lum","boss drift")
truth=hist.get("truthLaw",{})
need(truth.get("currentCanonicalSourceBeatsChatHistory") is True,"current source must beat chat history")
need(truth.get("currentUserInstructionBeatsOldChatInstruction") is True,"current user instruction must beat old chat instruction")
need(truth.get("contradictionsStayExplicit") is True,"contradictions must remain explicit")
auto=hist.get("automaticActions",{})
for key in ("readWhenAvailable","index","summarize","classify","extractDecisions","buildHandoff","flagContradictions"):
    need(auto.get(key) is True,f"safe history action missing: {key}")
for key in ("deleteChat","archiveChat","renameChat","rewriteHistory"):
    need(auto.get(key) is False,f"history destructive action leak: {key}")
need(hist.get("privacy",{}).get("doNotDumpFullHistoryIntoEveryTurn") is True,"full-history dump guard missing")
need(hist.get("privacy",{}).get("privateChatContentDoesNotEnterPublicRepo") is True,"private chat repo guard missing")
need(hist.get("hiddenAsyncExecution") is False,"hidden async leak")
need(hist.get("promotion") is False and hist.get("crownStatus")=="STOP","authority leak")

b=ctl.get("agents",{}).get("belldandySecretary",{})
for cap in ("chatHistoryIndex","decisionExtraction","historicalReceiptIndex","contradictionLedger","supersededInstructionDetection","chatHandoffCompression"):
    need(cap in b.get("capabilities",[]),f"Belldandy capability missing: {cap}")
need(ctl.get("routeProfiles",{}).get("chatHistory")==["lum","belldandySecretary"],"chat history route drift")
need(ctl.get("providerBoundary",{}).get("chatHistoryStewardship",{}).get("contract")=="doctrine/chatHistoryStewardshipV1.json","control-plane history binding missing")
need(chat.get("alwaysLoadedCore",{}).get("chatHistoryStewardship")=="doctrine/chatHistoryStewardshipV1.json","chat canon history binding missing")
need(chat.get("contextLaw",{}).get("historySteward")=="belldandySecretary","chat history steward drift")
need("## Chat history stewardship" in bel,"Belldandy skill missing chat-history section")
need("## Historical chat continuity" in boot,"bootstrap missing history routing")

print(json.dumps({
  "schema":"luhmOs.chatHistoryStewardshipAudit.v1",
  "status":"greenChatHistoryStewardshipCandidate" if not errors else "redChatHistoryStewardshipCandidate",
  "owner":"belldandySecretary",
  "destructiveChatMutation":False,
  "hiddenAsyncExecution":False,
  "crownStatus":"STOP",
  "errors":errors
},indent=2))
raise SystemExit(1 if errors else 0)

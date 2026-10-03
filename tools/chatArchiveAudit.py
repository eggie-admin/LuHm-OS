#!/usr/bin/env python3
import json, pathlib, sys, tomllib

root=pathlib.Path(__file__).resolve().parents[1]
errors=[]

def load(path):
    try:return json.loads((root/path).read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"{path}: {exc}")
        return {}

def need(ok,msg):
    if not ok: errors.append(msg)

exp=load("doctrine/chatExperienceV1.json")
handoff=load("doctrine/chatArchiveHandoffV1.json")
canon=load("doctrine/projectChatCanonV1.json")
plane=load("doctrine/luhmAiControlPlaneV1.json")
truth=load("doctrine/SOURCE_OF_TRUTH.json")

need(exp.get("outputPolicy",{}).get("rawToolLogsByDefault") is False,"raw tool logs must default off")
need(exp.get("outputPolicy",{}).get("deltaOnly") is True,"delta-only chat law missing")
need(exp.get("conversationLaw",{}).get("noFakeGreen") is True,"noFakeGreen missing")
need(exp.get("agentPresentation",{}).get("doNotNarrateRoutineAgentChatter") is True,"routine agent chatter suppression missing")
need(handoff.get("nextWorkChat",{}).get("defaultResponseMode")=="compactConversational","handoff response mode drift")
need(canon.get("alwaysLoadedCore",{}).get("chatExperience")=="doctrine/chatExperienceV1.json","chat canon missing experience doctrine")
need(plane.get("chatExperienceContract")=="doctrine/chatExperienceV1.json","control plane missing experience contract")
need(truth.get("chatExperience",{}).get("contract")=="doctrine/chatExperienceV1.json","source truth missing chat experience pointer")
need(truth.get("chatArchiveHandoff",{}).get("contract")=="doctrine/chatArchiveHandoffV1.json","source truth missing handoff pointer")

lum=(root/"agents/lum/SKILL.md").read_text(encoding="utf-8")
need("doctrine/operationTitan7AgentMeshV1.json" not in lum,"Lum retains deleted Titan7 agent-mesh pointer")
need("doctrine/operationTitan7V1.json" in lum,"Lum missing canonical Titan7 pointer")
need("doctrine/chatExperienceV1.json" in lum,"Lum missing chat experience binding")
need("raw tool logs" in lum.lower(),"Lum missing log suppression law")

profiles=sorted((root/".codex/agents").glob("*.toml"))
need([p.stem for p in profiles]==["belldandySecretary","skuldResearch","urdDoctorGoddess","yume"],"resident agent profiles drift")
for p in profiles:
    data=tomllib.loads(p.read_text(encoding="utf-8"))
    need(data.get("sandbox_mode")=="read-only",f"{p} not read-only")

print(json.dumps({
  "schema":"luhmOs.chatArchiveAudit.v1",
  "status":"GREEN_CHAT_ARCHIVE_HANDOFF" if not errors else "RED_CHAT_ARCHIVE_HANDOFF",
  "errors":errors,
  "defaultResponseMode":"compactConversational",
  "crownStatus":"STOP"
},indent=2))
sys.exit(1 if errors else 0)

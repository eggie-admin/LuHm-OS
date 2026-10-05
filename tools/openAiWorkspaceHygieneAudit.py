#!/usr/bin/env python3
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
errors=[]

def need(ok,msg):
    if not ok:
        errors.append(msg)

hygiene=json.loads((root/"doctrine/openAiWorkspaceHygieneV1.json").read_text(encoding="utf-8"))
control=json.loads((root/"doctrine/luhmAiControlPlaneV1.json").read_text(encoding="utf-8"))
chat=json.loads((root/"doctrine/projectChatCanonV1.json").read_text(encoding="utf-8"))
skill=(root/"agents/belldandyQualityOni/SKILL.md").read_text(encoding="utf-8")

need(hygiene.get("schema")=="luhmOs.openAiWorkspaceHygiene.v1","schema drift")
need(hygiene.get("owner")=="belldandySecretary","owner drift")
need(hygiene.get("boss")=="lum","boss drift")
auto=hygiene.get("automaticActions",{})
for key in ("read","index","classify","compare","flag","propose"):
    need(auto.get(key) is True,f"safe automatic action missing: {key}")
for key in ("delete","move","rename","overwrite","detach","publish"):
    need(auto.get(key) is False,f"destructive automatic action leak: {key}")
need(hygiene.get("identityLaw",{}).get("filenameAloneNeverProvesDuplicate") is True,"filename-only duplicate rule missing")
need(hygiene.get("hiddenAsyncExecution") is False,"hidden async execution leak")
need(hygiene.get("promotion") is False and hygiene.get("crownStatus")=="STOP","authority leak")

bel=control.get("agents",{}).get("belldandySecretary",{})
for cap in ("openAiWorkspaceInventory","chatGptLibraryIndex","projectFileHygiene","duplicateReferenceDetection","staleHandoffDetection","orphanArtifactDetection","archiveProposal"):
    need(cap in bel.get("capabilities",[]),f"Belldandy capability missing: {cap}")
for forbid in ("deleteUserContent","moveUserContent","renameUserContent","overwriteUserContent","detachUserContent"):
    need(forbid in bel.get("forbidden",[]),f"Belldandy forbidden action missing: {forbid}")
need(control.get("providerBoundary",{}).get("openAiWorkspaceHygiene",{}).get("contract")=="doctrine/openAiWorkspaceHygieneV1.json","control-plane hygiene binding missing")
need(chat.get("alwaysLoadedCore",{}).get("openAiWorkspaceHygiene")=="doctrine/openAiWorkspaceHygieneV1.json","chat core hygiene binding missing")
need("doctrine/openAiWorkspaceHygieneV1.json" in chat.get("loadOrder",[]),"hygiene contract missing from load order")
need("OpenAI / ChatGPT workspace hygiene" in skill,"Belldandy skill missing workspace section")
need("may not silently delete, move, rename, overwrite" in skill,"Belldandy destructive boundary missing")

print(json.dumps({
  "schema":"luhmOs.openAiWorkspaceHygieneAudit.v1",
  "status":"greenOpenAiWorkspaceHygieneCandidate" if not errors else "redOpenAiWorkspaceHygieneCandidate",
  "owner":"belldandySecretary",
  "automaticDestructiveMutation":False,
  "hiddenAsyncExecution":False,
  "crownStatus":"STOP",
  "errors":errors
},indent=2))
raise SystemExit(1 if errors else 0)

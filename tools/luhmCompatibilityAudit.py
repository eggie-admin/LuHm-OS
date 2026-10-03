#!/usr/bin/env python3
import json, pathlib, re, sys, tomllib

root=pathlib.Path(__file__).resolve().parents[1]
errors=[]

def load(path):
    try:return json.loads((root/path).read_text(encoding="utf-8"))
    except Exception as exc: errors.append(f"{path}: {exc}"); return {}

def require(condition,message):
    if not condition: errors.append(message)

layers=load("doctrine/luhmCompatibilityLayersV1.json")
titan=load("doctrine/operationTitan7V1.json")
plane=load("doctrine/luhmAiControlPlaneV1.json")
canon=load("doctrine/projectChatCanonV1.json")

require(layers.get("layerOne",{}).get("id")=="openAiCompatibilityLayer","layer one mismatch")
require(layers.get("layerTwo",{}).get("id")=="githubCompatibilityLayer","layer two mismatch")
require(layers.get("layerTwo",{}).get("allProviderResultsReturnTo")=="lum","remote provider results must return to Lum")
require(layers.get("wireProtocol",{}).get("javascriptAdapter",{}).get("authority") is False,"wire minifier may not have authority")
require(titan.get("canonicalName")=="operationTitan7","operationTitan7 name drift")
require(titan.get("notAProject") is True,"operationTitan7 must not be a project")
require(titan.get("notAlwaysRunning") is True,"operationTitan7 must not always run")
require(titan.get("invocationLaw",{}).get("scheduledBackgroundRunsForbidden") is True,"Titan7 scheduled runs forbidden")
require(titan.get("escalation",{}).get("forFuckSake",{}).get("commitWindowMax")==25,"FFS tier mismatch")
require(titan.get("escalation",{}).get("scorchedEarth",{}).get("commitWindowMax")==50,"Scorched Earth tier mismatch")
require(titan.get("escalation",{}).get("finalForm",{}).get("commitWindowMax")==50,"Final Form history ceiling mismatch")
require(plane.get("compatibilityLayersContract")=="doctrine/luhmCompatibilityLayersV1.json","control plane missing compatibility layers")
require(plane.get("operationTitan7",{}).get("contract")=="doctrine/operationTitan7V1.json","control plane missing Titan7 plugin contract")
require("OperationTitan7" not in canon.get("bootstrapTrigger",{}).get("projectNames",[]),"project bootstrap still treats Titan7 as a project")

profiles=sorted((root/".codex/agents").glob("*.toml"))
expected=["belldandySecretary","skuldResearch","urdDoctorGoddess","yume"]
require([p.stem for p in profiles]==expected,"resident goddess profiles mismatch")
config=tomllib.loads((root/".codex/config.toml").read_text(encoding="utf-8"))
require(config.get("agents",{}).get("max_concurrent_threads_per_session")==4,"agent concurrency must be 4")

source=(root/"frontEnd/jquery/luhmManifestMin.js").read_text(encoding="utf-8")
runtime=(root/"frontEnd/jquery/luhmManifestMin.min.js").read_text(encoding="utf-8")
titan_js=(root/"frontEnd/jquery/operationTitan7.min.js").read_text(encoding="utf-8")
require(len(runtime.encode()) < len(source.encode()),"manifest runtime is not minified")
require("$.luhmManifestMin" in runtime,"manifest minifier runtime missing")
require("$.fn[p]" in titan_js or "operationTitan7" in titan_js,"Titan7 jQuery plugin missing")

for path in [
 "doctrine/operationTitan7AgentMeshV1.json",
 "doctrine/operationTitan7FinalFormV1.json",
 "doctrine/OPERATION_TITAN7_WATCH_FLEET_V1.json",
 ".github/workflows/operation-titan7-agent-mesh.yml",
 ".github/workflows/operation-titan7-final-form.yml",
 ".github/workflows/operation-titan7-watch-fleet.yml"
]:
    require(not (root/path).exists(),f"legacy Titan7 file still active: {path}")

workflow=(root/".github/workflows/operationTitan7.yml").read_text(encoding="utf-8")
require("schedule:" not in workflow,"Titan7 workflow may not be scheduled")
require("workflow_dispatch:" in workflow,"Titan7 callable workflow missing workflow_dispatch")
require("dryRun --escalation finalForm" in workflow,"Final Form doctrine proof missing")

print(json.dumps({
 "schema":"luhmOs.compatibilityAndTitan7Audit.v1",
 "status":"GREEN_COMPATIBILITY_AND_TITAN7" if not errors else "RED_COMPATIBILITY_AND_TITAN7",
 "errors":errors,
 "layerOne":"openAiCompatibilityLayer",
 "layerTwo":"githubCompatibilityLayer",
 "operationTitan7":"callable",
 "crownStatus":"STOP"
},indent=2))
sys.exit(1 if errors else 0)

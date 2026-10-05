#!/usr/bin/env python3
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
errors=[]

def need(ok,msg):
    if not ok:
        errors.append(msg)

training=json.loads((root/"doctrine/openingDayStaffTrainingV1.json").read_text(encoding="utf-8"))
truth=json.loads((root/"doctrine/currentSourceTruthV3.json").read_text(encoding="utf-8"))
experience=json.loads((root/"doctrine/inChatExperienceV1.json").read_text(encoding="utf-8"))
harness=(root/"host/mcp/luhmHarness.py").read_text(encoding="utf-8")
widget=(root/"host/harness/widget.html").read_text(encoding="utf-8")

need(training.get("schema")=="luhmOs.openingDayStaffTraining.v1","training schema drift")
need(training.get("authority")=="Professor","Professor authority drift")
need(training.get("trainer")=="lum","Lum trainer drift")
need(training.get("status")=="SOURCE_CONFIGURED_CANDIDATE","training status overclaim")

install=training.get("installModel",{})
need(install.get("target")=="publicDirectoryOneInstall","one-install target drift")
need(install.get("canonicalBackend")=="https://luhm-os-harness-green.onrender.com/mcp","canonical backend drift")
need(install.get("endUserManualMcpUrlRequired") is False,"manual MCP setup leaked into end-user flow")
need(install.get("endUserZipRequired") is False,"ZIP leaked into end-user flow")
need(install.get("luhmAccountLoginRequired") is False,"unproved LuHm login requirement added")

surfaces=training.get("surfaces",{})
need(surfaces.get("inChat",{}).get("tool")=="luhm_open_cockpit","in-chat tool drift")
need(surfaces.get("inChat",{}).get("resourceUri")=="ui://luhm-os/cockpit-v2.html","in-chat resource drift")
need(surfaces.get("inApp",{}).get("sameContract") is True,"app/chat contract split")
need(surfaces.get("inApp",{}).get("manualSetupAfterInstall") is False,"manual post-install setup drift")

staff=training.get("staffModel",{})
need(staff.get("rosterSource")=="doctrine/agentSystemDeploymentV1.json","roster source drift")
need(staff.get("boss")=="lum","staff boss drift")
need(staff.get("residentCore")==["urdDoctorGoddess","belldandySecretary","skuldResearch"],"resident core drift")
need(staff.get("maxParallelSupportWorkers")==3,"parallelism drift")
need(staff.get("helpersRecruitHelpers") is False,"recursive recruiting enabled")
need(staff.get("hiddenAsyncExecution") is False,"hidden async claim enabled")

ids=[step.get("id") for step in training.get("orientation",[])]
need(ids==["companyLaw","rollCall","departmentDrill","redDrill","recordsDrill","compatibilityDrill","customerRehearsal"],"orientation sequence drift")

first=training.get("firstRunExperience",{})
need(first.get("lumGreeting")=="LuHm OS online. Staff checked in. What are we building?","first-run greeting drift")
need(first.get("showOnlyRoutedWorkers") is True,"fake staff activity allowed")
need(first.get("architectureDumpForbidden") is True,"architecture dump allowed")
need(first.get("manualSetupDumpForbidden") is True,"manual setup dump allowed")

fast=training.get("fastPath",{})
need(fast.get("machineGatesContinueAutomatically") is True,"FAST_PATH machine gates disabled")
need(fast.get("userActionOnlyWhenRequired") is True,"unnecessary user action allowed")
need(fast.get("oneUserActionAtATime") is True,"user action batching enabled")

proof=training.get("proof",{})
for key in ("sourceConfiguredDoesNotEqualPublicInstallProof","runtimeMustExposeThisContract","chatAndStandaloneMustExposeSameContract","oneClickDirectoryInstallRemainsExternalUntilPublished"):
    need(proof.get(key) is True,f"proof boundary missing: {key}")

need(training.get("publicationAuthority") is False,"publication authority leak")
need(training.get("crownStatus")=="STOP","Crown overclaim")
need(truth.get("experienceLayer",{}).get("openingDayStaffTraining")=="doctrine/openingDayStaffTrainingV1.json","source truth training pointer missing")
need(truth.get("experienceLayer",{}).get("installTarget")=="publicDirectoryOneInstall","source truth install target drift")
need(truth.get("experienceLayer",{}).get("endUserManualMcpSetup") is False,"source truth manual MCP drift")
need(experience.get("sources",{}).get("openingDayStaffTraining")=="doctrine/openingDayStaffTrainingV1.json","experience training pointer missing")
need("openingDay" in experience.get("runtime",{}).get("panels",[]),"opening-day panel missing")
need('"openingDay": opening_day' in harness,"harness opening-day payload missing")
need('id="openingDay"' in widget and 'id="installModel"' in widget,"widget opening-day bindings missing")

print(json.dumps({
  "schema":"luhmOs.openingDayStaffTrainingAudit.v1",
  "status":"GREEN_OPENING_DAY_SOURCE" if not errors else "RED_OPENING_DAY_SOURCE",
  "installTarget":install.get("target"),
  "inChatTool":surfaces.get("inChat",{}).get("tool"),
  "sameAppAndChatContract":surfaces.get("inApp",{}).get("sameContract"),
  "orientationSteps":len(ids),
  "publicInstallProof":"PENDING_EXTERNAL_DIRECTORY",
  "crownStatus":"STOP",
  "errors":errors
},indent=2))
raise SystemExit(1 if errors else 0)

#!/usr/bin/env python3
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
errors=[]

def need(ok,msg):
    if not ok:
        errors.append(msg)

def load(rel):
    return json.loads((root/rel).read_text(encoding="utf-8"))

training=load("doctrine/openingDayStaffTrainingV1.json")
truth=load("doctrine/currentSourceTruthV3.json")
experience=load("doctrine/inChatExperienceV1.json")
deployment=load("doctrine/agentSystemDeploymentV1.json")
control=load("doctrine/luhmAiControlPlaneV1.json")
provider=load("doctrine/providerEconomyV1.json")
api=load("doctrine/apiSpineV1.json")
harness=(root/"host/mcp/luhmHarness.py").read_text(encoding="utf-8")
widget=(root/"host/harness/widget.html").read_text(encoding="utf-8")

need(training.get("schema")=="luhmOs.openingDayStaffTraining.v1","training schema drift")
need(training.get("authority")=="Professor","Professor authority drift")
need(training.get("trainer")=="lum","Lum trainer drift")
need(training.get("status")=="SOURCE_CONFIGURED_CANDIDATE","training status overclaim")

scope=training.get("companyScopeOfPractice",{})
need(scope.get("companyLaw")=="AI proposes. Policy authorizes. CI proves. Human promotes.","company source law drift")
need(scope.get("currentPublicBoundary")=="readOnlyUntilSeparateAuthorityAndExternalPublicationGatesProveOtherwise","public scope boundary drift")
for item in (
    "sourceTruthAndDoctrine",
    "researchAndCompatibility",
    "softwareMutationAndBuild",
    "evidenceAndQualityAdjudication",
    "recordsStorageAndLogistics",
    "creativeMediaAndGameDevelopment",
    "androidThinClientAndPhysicalProof",
    "publicPluginAndInChatExperience",
):
    need(item in scope.get("internalPractice",[]),f"company scope missing: {item}")

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

classroom=training.get("staffClassroom",{})
need(classroom.get("professor",{}).get("mayDelegateCrown") is False,"Professor Crown delegation leak")
need(classroom.get("lum",{}).get("maySelfApprove") is False,"Lum self-approval leak")
need(classroom.get("goddesses",{}).get("members")==["urdDoctorGoddess","belldandySecretary","skuldResearch"],"goddess classroom roster drift")
need(classroom.get("goddesses",{}).get("majorityVoteAuthority") is False,"goddess vote authority leak")
need(classroom.get("oni",{}).get("recursiveRecruitment") is False,"Oni recursive recruitment leak")
need(classroom.get("oni",{}).get("hiddenAsyncExecution") is False,"Oni hidden async leak")
need(classroom.get("robots",{}).get("mayInterpretAuthority") is False,"robot authority interpretation leak")
need(classroom.get("robots",{}).get("mayGrantGreenWithoutMatchingDeterministicProof") is False,"robot fake GREEN leak")
need(classroom.get("robots",{}).get("mayGrantCrown") is False,"robot Crown leak")

daddies=classroom.get("daddies",{})
need(daddies.get("mayGrantGreen") is False,"Daddy provider GREEN leak")
need(daddies.get("mayGrantCrown") is False,"Daddy provider Crown leak")
need(daddies.get("mayRewriteCompanyScope") is False,"Daddy company-scope leak")
provider_ids={x.get("id") for x in daddies.get("providers",[])}
need({"openAi","googleAi","githubCopilot","huggingFace","edgeGallery"}.issubset(provider_ids),"Daddy provider classroom incomplete")
need(provider.get("sharedProviderBoundary",{}).get("providerOutputRequiresLumReconciliation") is True,"provider reconciliation law drift")
need(api.get("routing",{}).get("principle")=="capabilityFirstProviderSecond","capability-first routing drift")

scope_law=training.get("scopeOfPracticeLaw",{})
for key in (
    "everyWorkerKnowsOwnRole",
    "everyWorkerKnowsForbiddenCapabilities",
    "everyWorkerKnowsWhoReceivesHandoff",
    "everyWorkerKnowsProofBoundary",
    "everyWorkerKnowsCustomerFacingBoundary",
):
    need(scope_law.get(key) is True,f"scope-of-practice teaching missing: {key}")
need(scope_law.get("personalityNeverExpandsCapability") is True,"personality capability leak")
need(scope_law.get("trainingNeverExpandsAuthority") is True,"training authority leak")
need(scope_law.get("unknownRemains")=="UNKNOWN","UNKNOWN state drift")
need(scope_law.get("conflictRemains")=="CONFLICT","CONFLICT state drift")

workflow=training.get("sharedWorkflow",{})
need(workflow.get("covenantGuardRail")==["sanityCheck","audit","ingest","mutation","test","apply","continue","deploy"],"covenant guard rail drift")
need(workflow.get("noFakeGreen") is True,"fake GREEN allowed")
need(workflow.get("fastPath")=="continueMachineGatesUntilRealUserActionOrCrownBoundary","FAST_PATH training drift")

skills=training.get("skillsAndLogic",{})
need(skills.get("skillsAreRepositoryBackedContracts") is True,"skills training definition drift")
need(skills.get("deterministicChecksOutrankOpinion") is True,"deterministic evidence precedence drift")
need(skills.get("capabilityFirstProviderSecond") is True,"provider-selection logic drift")
need(skills.get("leastConsequentialLaneFirst") is True,"least-consequential routing drift")
need(skills.get("exactSourceIdentityForTruthSensitiveWork") is True,"truth-sensitive source identity drift")

learning=training.get("learningModel",{})
need(learning.get("staffMaySelfModify") is False,"staff self-modification leak")
need(learning.get("providerOutputMayBecomeLessonWithoutReconciliation") is False,"provider lesson reconciliation leak")
need(learning.get("staleLessonIsProof") is False,"stale lesson promoted to proof")
need(learning.get("continuousHiddenTraining") is False,"hidden continuous training claim")
for field in ("taskId","sourceRef","scopeId","evidenceRefs","provingReceipt","validityScope"):
    need(field in learning.get("verifiedLessonRequires",[]),f"verified lesson missing: {field}")

prep=training.get("openingDayPrep",{})
need(prep.get("phase")=="STAFF_ORIENTATION_CANDIDATE","opening-day prep phase drift")
need(prep.get("requiredAgentCount")==15,"opening-day required agent count drift")
need(prep.get("rosterMustMatchDeployment") is True,"opening-day roster matching disabled")
need(prep.get("customerRehearsalRequired") is True,"customer rehearsal not required")
need(prep.get("publicationStillExternal") is True,"publication boundary drift")
need(deployment.get("requiredAgentCount")==15 and len(deployment.get("requiredAgents",[]))==15,"deployment roster count drift")
need(set(deployment.get("requiredAgents",[]))==set(control.get("agents",{})),"opening-day roster/control-plane mismatch")

ids=[step.get("id") for step in training.get("orientation",[])]
expected_ids=[
    "companyScope","companyLaw","rollCall","scopeOfPractice","workflowDrill","skillsDrill",
    "learningDrill","redDrill","recordsDrill","compatibilityDrill","daddyPitchDrill",
    "robotDrill","customerRehearsal","openingDayReview"
]
need(ids==expected_ids,"orientation sequence drift")

first=training.get("firstRunExperience",{})
need(first.get("lumGreeting")=="LuHm OS online. Staff checked in. What are we building?","first-run greeting drift")
need(first.get("showOnlyRoutedWorkers") is True,"fake staff activity allowed")
need(first.get("architectureDumpForbidden") is True,"architecture dump allowed")
need(first.get("manualSetupDumpForbidden") is True,"manual setup dump allowed")
need(first.get("providerBrandingHiddenByDefault") is True,"provider plumbing exposed by default")

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
  "status":"GREEN_OPENING_DAY_STAFF_TRAINING_CANDIDATE" if not errors else "RED_OPENING_DAY_STAFF_TRAINING_CANDIDATE",
  "installTarget":install.get("target"),
  "staffAgentCount":len(deployment.get("requiredAgents",[])),
  "orientationSteps":len(ids),
  "providerPitchBoundary":"candidateEvidenceOnly",
  "learningModel":"repositoryBackedNotModelWeightTraining",
  "publicInstallProof":"PENDING_EXTERNAL_DIRECTORY",
  "crownStatus":"STOP",
  "errors":errors
},indent=2))
raise SystemExit(1 if errors else 0)

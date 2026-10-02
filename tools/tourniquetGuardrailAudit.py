#!/usr/bin/env python3
import json
from pathlib import Path

rootPath=Path(__file__).resolve().parents[1]
errors=[]

def need(ok,msg):
    if not ok:
        errors.append(msg)

contractPath=rootPath/"doctrine/tourniquetGuardrailV1.json"
truthPath=rootPath/"doctrine/SOURCE_OF_TRUTH.json"
chatPath=rootPath/"doctrine/projectChatCanonV1.json"
controlPath=rootPath/"doctrine/luhmAiControlPlaneV1.json"

for path in (contractPath,truthPath,chatPath,controlPath):
    need(path.is_file(),f"missing {path.relative_to(rootPath)}")

if contractPath.is_file():
    contractDoc=json.loads(contractPath.read_text())
    need(contractDoc.get("triggerOwner")=="Professor","Professor must own trigger")
    law=contractDoc.get("triggerLaw",{})
    need(law.get("semanticIntentBeatsExactPhrase") is True,"tourniquet must be semantic")
    need(law.get("explicitCorrectionAlwaysInterrupts") is True,"explicit correction must interrupt")
    actions=contractDoc.get("immediateActions",[])
    for action in ("haltCurrentInterpretation","discardQueuedAssumptions","bindProfessorCorrection","reframeTaskEnvelope","resumeOnlyFromCorrectedEnvelope"):
        need(action in actions,f"missing immediate action {action}")
    forbidden=contractDoc.get("forbiddenAfterTrigger",[])
    for item in ("continueOldPlan","silentlyBlendOldAndNewIntent","keepQueuedVendorAiWorkBasedOnOldIntent","keepQueuedMutationBasedOnOldIntent"):
        need(item in forbidden,f"missing forbidden action {item}")
    roles=contractDoc.get("cabinetRoles",{})
    need(roles.get("lum",{}).get("role")=="interruptReceiverAndReframer","Lum interrupt role drift")
    need(roles.get("urdDoctorGoddess",{}).get("role")=="driftDiagnosis","Urd tourniquet role drift")
    need(roles.get("belldandySecretary",{}).get("role")=="correctionLedger","Belldandy tourniquet role drift")
    need(contractDoc.get("automaticResume") is False,"automatic resume leak")
    need(contractDoc.get("hiddenAsyncExecution") is False,"hidden async leak")
    need(contractDoc.get("professorFinalAuthority") is True,"Professor authority drift")

if truthPath.is_file():
    truthDoc=json.loads(truthPath.read_text())
    tg=truthDoc.get("tourniquetGuardrail",{})
    need(tg.get("contract")=="doctrine/tourniquetGuardrailV1.json","source truth tourniquet binding missing")
    need(tg.get("automaticResume") is False,"source truth auto resume leak")

if chatPath.is_file():
    chatDoc=json.loads(chatPath.read_text())
    need(chatDoc.get("alwaysLoadedCore",{}).get("tourniquetGuardrail")=="doctrine/tourniquetGuardrailV1.json","tourniquet not always loaded")
    need(chatDoc.get("chatRuntime",{}).get("professorCorrectionInterruptsCurrentPlan") is True,"chat interrupt law missing")
    need(chatDoc.get("chatRuntime",{}).get("automaticResumeAfterCorrection") is False,"chat auto resume leak")

if controlPath.is_file():
    controlDoc=json.loads(controlPath.read_text())
    inv=controlDoc.get("invariants",{})
    need(inv.get("professorCorrectionInterruptsCurrentPlan") is True,"control-plane interrupt missing")
    need(inv.get("supersededIntentMayContinue") is False,"superseded intent may continue")
    tourniquetState=controlDoc.get("bossToolchain",{}).get("tourniquet",{})
    need(tourniquetState.get("automaticResume") is False,"boss toolchain auto resume leak")

for rel,token in {
    "agents/lum/SKILL.md":"## Tourniquet guardrail",
    "agents/urdMutationOni/SKILL.md":"## Tourniquet monitoring",
    "agents/belldandyQualityOni/SKILL.md":"## Tourniquet monitoring",
}.items():
    skillFile=rootPath/rel
    need(skillFile.is_file(),f"missing {rel}")
    if skillFile.is_file():
        need(token in skillFile.read_text(),f"{rel} missing tourniquet binding")

print(json.dumps({
    "schema":"luhmOs.tourniquetGuardrailAudit.v1",
    "status":"greenTourniquetCandidate" if not errors else "redTourniquetCandidate",
    "triggerOwner":"Professor",
    "urdDoctorGoddess":"driftDiagnosis",
    "belldandySecretary":"correctionLedger",
    "automaticResume":False,
    "errors":errors,
    "crownStatus":"stop"
},indent=2))
raise SystemExit(1 if errors else 0)

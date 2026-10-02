#!/usr/bin/env python3
import json
from pathlib import Path

rootPath = Path(__file__).resolve().parents[1]
violations = []

def requireTruth(isTrue, message):
    if not isTrue:
        violations.append(message)

contractPath = rootPath / "doctrine/tourniquetGuardrailV1.json"
truthPath = rootPath / "doctrine/SOURCE_OF_TRUTH.json"
chatPath = rootPath / "doctrine/projectChatCanonV1.json"
controlPath = rootPath / "doctrine/luhmAiControlPlaneV1.json"

for targetPath in (contractPath, truthPath, chatPath, controlPath):
    requireTruth(targetPath.is_file(), f"missing {targetPath.relative_to(rootPath)}")

if contractPath.is_file():
    contractDoc = json.loads(contractPath.read_text())
    requireTruth(contractDoc.get("triggerOwner") == "Professor", "Professor must own trigger")

    triggerLaw = contractDoc.get("triggerLaw", {})
    requireTruth(triggerLaw.get("semanticIntentBeatsExactPhrase") is True, "tourniquet must be semantic")
    requireTruth(triggerLaw.get("explicitCorrectionAlwaysInterrupts") is True, "explicit correction must interrupt")

    immediateActions = contractDoc.get("immediateActions", [])
    requiredActions = (
        "haltCurrentInterpretation",
        "discardQueuedAssumptions",
        "bindProfessorCorrection",
        "reframeTaskEnvelope",
        "resumeOnlyFromCorrectedEnvelope",
    )
    for actionName in requiredActions:
        requireTruth(actionName in immediateActions, f"missing immediate action {actionName}")

    forbiddenActions = contractDoc.get("forbiddenAfterTrigger", [])
    requiredBlocks = (
        "continueOldPlan",
        "silentlyBlendOldAndNewIntent",
        "keepQueuedVendorAiWorkBasedOnOldIntent",
        "keepQueuedMutationBasedOnOldIntent",
    )
    for blockedAction in requiredBlocks:
        requireTruth(blockedAction in forbiddenActions, f"missing forbidden action {blockedAction}")

    cabinetRoles = contractDoc.get("cabinetRoles", {})
    requireTruth(cabinetRoles.get("lum", {}).get("role") == "interruptReceiverAndReframer", "Lum interrupt role drift")
    requireTruth(cabinetRoles.get("urdDoctorGoddess", {}).get("role") == "driftDiagnosis", "Urd tourniquet role drift")
    requireTruth(cabinetRoles.get("belldandySecretary", {}).get("role") == "correctionLedger", "Belldandy tourniquet role drift")
    requireTruth(contractDoc.get("automaticResume") is False, "automatic resume leak")
    requireTruth(contractDoc.get("hiddenAsyncExecution") is False, "hidden async leak")
    requireTruth(contractDoc.get("professorFinalAuthority") is True, "Professor authority drift")

if truthPath.is_file():
    truthDoc = json.loads(truthPath.read_text())
    tourniquetTruth = truthDoc.get("tourniquetGuardrail", {})
    requireTruth(tourniquetTruth.get("contract") == "doctrine/tourniquetGuardrailV1.json", "source truth tourniquet binding missing")
    requireTruth(tourniquetTruth.get("automaticResume") is False, "source truth auto resume leak")

if chatPath.is_file():
    chatDoc = json.loads(chatPath.read_text())
    requireTruth(chatDoc.get("alwaysLoadedCore", {}).get("tourniquetGuardrail") == "doctrine/tourniquetGuardrailV1.json", "tourniquet not always loaded")
    requireTruth(chatDoc.get("chatRuntime", {}).get("professorCorrectionInterruptsCurrentPlan") is True, "chat interrupt law missing")
    requireTruth(chatDoc.get("chatRuntime", {}).get("automaticResumeAfterCorrection") is False, "chat auto resume leak")

if controlPath.is_file():
    controlDoc = json.loads(controlPath.read_text())
    invariants = controlDoc.get("invariants", {})
    requireTruth(invariants.get("professorCorrectionInterruptsCurrentPlan") is True, "control-plane interrupt missing")
    requireTruth(invariants.get("supersededIntentMayContinue") is False, "superseded intent may continue")
    tourniquetState = controlDoc.get("bossToolchain", {}).get("tourniquet", {})
    requireTruth(tourniquetState.get("automaticResume") is False, "boss toolchain auto resume leak")

skillChecks = {
    "agents/lum/SKILL.md": "## Tourniquet guardrail",
    "agents/urdMutationOni/SKILL.md": "## Tourniquet monitoring",
    "agents/belldandyQualityOni/SKILL.md": "## Tourniquet monitoring",
}
for relPath, requiredHeading in skillChecks.items():
    skillFile = rootPath / relPath
    requireTruth(skillFile.is_file(), f"missing {relPath}")
    if skillFile.is_file():
        requireTruth(requiredHeading in skillFile.read_text(), f"{relPath} missing tourniquet binding")

print(json.dumps({
    "schema": "luhmOs.tourniquetGuardrailAudit.v1",
    "status": "greenTourniquetCandidate" if not violations else "redTourniquetCandidate",
    "triggerOwner": "Professor",
    "urdDoctorGoddess": "driftDiagnosis",
    "belldandySecretary": "correctionLedger",
    "automaticResume": False,
    "violations": violations,
    "crownStatus": "stop",
}, indent=2))
raise SystemExit(1 if violations else 0)

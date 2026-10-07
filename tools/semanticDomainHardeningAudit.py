#!/usr/bin/env python3
import json
from pathlib import Path

rootPath = Path(__file__).resolve().parents[1]
errorList = []

def need(conditionValue, messageValue):
    if not conditionValue:
        errorList.append(messageValue)

semanticDoc = json.loads((rootPath / "doctrine/semanticDomainHardeningV1.json").read_text(encoding="utf-8"))
chatDoc = json.loads((rootPath / "doctrine/projectChatCanonV1.json").read_text(encoding="utf-8"))
cabinetDoc = json.loads((rootPath / "doctrine/lumGoddessCabinetV1.json").read_text(encoding="utf-8"))
urdDoc = json.loads((rootPath / "doctrine/urdClinicalSecurityPracticeV1.json").read_text(encoding="utf-8"))

sharedSkill = (rootPath / "agents/goddessSharedSystemsPractice/SKILL.md").read_text(encoding="utf-8")
lumSkill = (rootPath / "agents/lum/SKILL.md").read_text(encoding="utf-8")
urdSkill = (rootPath / "agents/urdMutationOni/SKILL.md").read_text(encoding="utf-8")
belldandySkill = (rootPath / "agents/belldandyQualityOni/SKILL.md").read_text(encoding="utf-8")
skuldSkill = (rootPath / "agents/skuldResearchOni/SKILL.md").read_text(encoding="utf-8")
agentsDoc = (rootPath / "AGENTS.md").read_text(encoding="utf-8")

need(semanticDoc.get("primeLaw") == "displayMetaphor -> machineMeaning -> allowedActions -> forbiddenInterpretations -> evidenceGate -> authorityCeiling", "semantic prime law drift")
need(semanticDoc.get("liveMutation") is False, "semantic doctrine unexpectedly grants mutation")
need(semanticDoc.get("humanSafety", {}).get("appliesToPeople") is True, "human safety boundary missing")

requiredTerms = [
    "quarantine", "diagnosis", "symptom", "pathology", "triage",
    "treatment", "prognosis", "prescription", "patient", "clinical",
    "doctorGoddess", "tsa", "sterileArea"
]
termMap = semanticDoc.get("terms", {})
for termName in requiredTerms:
    termValue = termMap.get(termName, {})
    need(bool(termValue), f"semantic term missing: {termName}")
    for fieldName in ("machineMeaning", "allowedActions", "forbiddenInterpretations", "evidenceGate", "authorityCeiling"):
        need(fieldName in termValue, f"{termName} missing {fieldName}")

need("automaticDeletion" in termMap.get("quarantine", {}).get("forbiddenInterpretations", []), "quarantine may imply deletion")
need(termMap.get("treatment", {}).get("preferredCanonicalAlias") == "repairPlan", "treatment alias must resolve to repairPlan")
need(termMap.get("prescription", {}).get("preferredCanonicalAlias") == "recommendedAction", "prescription alias must resolve to recommendedAction")
need("ProfessorAsPatient" in termMap.get("patient", {}).get("forbiddenInterpretations", []), "patient term may target Professor")
need("physicianCredential" in termMap.get("doctorGoddess", {}).get("forbiddenInterpretations", []), "doctorGoddess credential boundary missing")

need(chatDoc.get("alwaysLoadedCore", {}).get("semanticDomainHardening") == "doctrine/semanticDomainHardeningV1.json", "semantic doctrine not always loaded")
need("doctrine/semanticDomainHardeningV1.json" in chatDoc.get("loadOrder", []), "semantic doctrine missing from chat load order")
need(cabinetDoc.get("semanticBoundary") == "doctrine/semanticDomainHardeningV1.json", "cabinet semantic boundary missing")
need(urdDoc.get("semanticBoundary") == "doctrine/semanticDomainHardeningV1.json", "Urd clinical semantic boundary missing")

for nameValue, textValue in (
    ("shared skill", sharedSkill),
    ("Lum skill", lumSkill),
    ("Urd skill", urdSkill),
    ("Belldandy skill", belldandySkill),
    ("Skuld skill", skuldSkill),
    ("AGENTS", agentsDoc),
):
    need("semanticDomainHardeningV1.json" in textValue, f"{nameValue} does not load semantic boundary")

print(json.dumps({
    "schema": "luhmOs.semanticDomainHardeningAudit.v1",
    "status": "GREEN_SEMANTIC_DOMAIN_CANDIDATE" if not errorList else "RED_SEMANTIC_DOMAIN_CANDIDATE",
    "errors": errorList,
    "historicalEvidenceRewritten": False,
    "liveMutation": False,
    "crownStatus": "STOP"
}, indent=2))
raise SystemExit(1 if errorList else 0)

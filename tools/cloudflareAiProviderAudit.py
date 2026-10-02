#!/usr/bin/env python3
import json
from pathlib import Path

rootPath = Path(__file__).resolve().parents[1]
violations = []

def requireTruth(isTrue, message):
    if not isTrue:
        violations.append(message)

providerPath = rootPath / "doctrine/cloudflareAiProviderV1.json"
controlPath = rootPath / "doctrine/luhmAiControlPlaneV1.json"
cabinetPath = rootPath / "doctrine/lumGoddessCabinetV1.json"
truthPath = rootPath / "doctrine/SOURCE_OF_TRUTH.json"
skillPath = rootPath / "agents/cloudflareAiProvider/SKILL.md"

for targetPath in (providerPath, controlPath, cabinetPath, truthPath, skillPath):
    requireTruth(targetPath.is_file(), f"missing {targetPath.relative_to(rootPath)}")

if providerPath.is_file():
    providerDoc = json.loads(providerPath.read_text())
    requireTruth(providerDoc.get("providerId") == "cloudflareAiProvider", "provider id drift")
    requireTruth(providerDoc.get("boss") == "lum", "Lum boss drift")

    acquaintance = providerDoc.get("acquaintance", {})
    requireTruth(acquaintance.get("mayAddressLum") is True, "provider cannot address Lum")
    requireTruth(acquaintance.get("mayAddressGoddessesDirectly") is False, "direct goddess control leak")
    requireTruth(acquaintance.get("mayRecruitAgents") is False, "provider recruitment leak")
    requireTruth(acquaintance.get("mayRouteWorkers") is False, "provider routing leak")
    requireTruth(acquaintance.get("mayGrantGreen") is False, "provider GREEN authority leak")
    requireTruth(acquaintance.get("mayGrantCrown") is False, "provider Crown authority leak")

    goddessMap = acquaintance.get("knowsGoddesses", {})
    for goddessId in ("urdDoctorGoddess", "belldandySecretary", "skuldResearch"):
        requireTruth(goddessId in goddessMap, f"provider does not know {goddessId}")

    evidence = providerDoc.get("evidence", {})
    requireTruth(evidence.get("successIsGreen") is False, "provider success maps to GREEN")

    security = providerDoc.get("security", {})
    requireTruth(security.get("credentialsHostSideOnly") is True, "credential boundary drift")

    networkBoundary = providerDoc.get("networkBoundary", {})
    for boundaryKey in ("dnsMutation", "tunnelMutation", "publicExposure", "cloudflareEdgeAuthority"):
        requireTruth(networkBoundary.get(boundaryKey) is False, f"network authority leak: {boundaryKey}")

    requireTruth(providerDoc.get("crownStatus") == "stop", "Crown must stop")

if controlPath.is_file():
    controlDoc = json.loads(controlPath.read_text())
    cloudflareProvider = controlDoc.get("providers", {}).get("cloudflareAiProvider", {})
    requireTruth(cloudflareProvider.get("contract") == "doctrine/cloudflareAiProviderV1.json", "control-plane provider contract missing")
    requireTruth(cloudflareProvider.get("speaksTo") == "lum", "control-plane provider must speak to Lum")
    requireTruth(cloudflareProvider.get("cabinetAware") is True, "provider must be cabinet aware")
    requireTruth(cloudflareProvider.get("cabinetMember") is False, "provider must not be cabinet member")

if cabinetPath.is_file():
    cabinetDoc = json.loads(cabinetPath.read_text())
    cloudflareProvider = cabinetDoc.get("externalProviders", {}).get("cloudflareAiProvider", {})
    requireTruth(cloudflareProvider.get("returnsTo") == "lum", "cabinet provider must return to Lum")
    requireTruth(cloudflareProvider.get("directGoddessRouting") is False, "cabinet direct routing leak")

if truthPath.is_file():
    truthDoc = json.loads(truthPath.read_text())
    cloudflareProvider = truthDoc.get("aiProviders", {}).get("cloudflareAiProvider", {})
    requireTruth(cloudflareProvider.get("contract") == "doctrine/cloudflareAiProviderV1.json", "source truth provider contract missing")
    requireTruth(cloudflareProvider.get("status") == "candidateContractOnly", "source truth must not claim live provider")

if skillPath.is_file():
    skillText = skillPath.read_text()
    requiredPhrases = (
        "Lum is the only conversational boss",
        "Urd is the doctor goddess",
        "Belldandy is the secretary goddess",
        "Skuld is the research goddess",
        "successful API response is `OBSERVED`, not GREEN",
    )
    for phrase in requiredPhrases:
        requireTruth(phrase in skillText, f"skill missing phrase: {phrase}")

print(json.dumps({
    "schema": "luhmOs.cloudflareAiProviderAudit.v1",
    "status": "greenCloudflareAiProviderCandidate" if not violations else "redCloudflareAiProviderCandidate",
    "cabinetAware": True,
    "cabinetMember": False,
    "providerAuthority": False,
    "crownStatus": "stop",
    "violations": violations,
}, indent=2))
raise SystemExit(1 if violations else 0)

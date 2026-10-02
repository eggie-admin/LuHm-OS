#!/usr/bin/env python3
import json
from pathlib import Path

rootPath=Path(__file__).resolve().parents[1]
errors=[]

def need(ok,msg):
    if not ok: errors.append(msg)

providerPath=rootPath/"doctrine/cloudflareAiProviderV1.json"
controlPath=rootPath/"doctrine/luhmAiControlPlaneV1.json"
cabinetPath=rootPath/"doctrine/lumGoddessCabinetV1.json"
truthPath=rootPath/"doctrine/SOURCE_OF_TRUTH.json"
skillPath=rootPath/"agents/cloudflareAiProvider/SKILL.md"

for path in (providerPath,controlPath,cabinetPath,truthPath,skillPath):
    need(path.is_file(),f"missing {path.relative_to(rootPath)}")

if providerPath.is_file():
    providerDoc=json.loads(providerPath.read_text())
    need(providerDoc.get("providerId")=="cloudflareAiProvider","provider id drift")
    need(providerDoc.get("boss")=="lum","Lum boss drift")
    acquaintance=providerDoc.get("acquaintance",{})
    need(acquaintance.get("mayAddressLum") is True,"provider cannot address Lum")
    need(acquaintance.get("mayAddressGoddessesDirectly") is False,"direct goddess control leak")
    need(acquaintance.get("mayRecruitAgents") is False,"provider recruitment leak")
    need(acquaintance.get("mayRouteWorkers") is False,"provider routing leak")
    need(acquaintance.get("mayGrantGreen") is False,"provider GREEN authority leak")
    need(acquaintance.get("mayGrantCrown") is False,"provider Crown authority leak")
    goddessMap=acquaintance.get("knowsGoddesses",{})
    for ident in ("urdDoctorGoddess","belldandySecretary","skuldResearch"):
        need(ident in goddessMap,f"provider does not know {ident}")
    evidence=providerDoc.get("evidence",{})
    need(evidence.get("successIsGreen") is False,"provider success maps to GREEN")
    security=providerDoc.get("security",{})
    need(security.get("credentialsHostSideOnly") is True,"credential boundary drift")
    networkBoundary=providerDoc.get("networkBoundary",{})
    for k in ("dnsMutation","tunnelMutation","publicExposure","cloudflareEdgeAuthority"):
        need(networkBoundary.get(k) is False,f"network authority leak: {k}")
    need(providerDoc.get("crownStatus")=="stop","Crown must stop")

if controlPath.is_file():
    controlDoc=json.loads(controlPath.read_text())
    providers=controlDoc.get("providers",{})
    cloudflareProvider=providers.get("cloudflareAiProvider",{})
    need(cloudflareProvider.get("contract")=="doctrine/cloudflareAiProviderV1.json","control-plane provider contract missing")
    need(cloudflareProvider.get("speaksTo")=="lum","control-plane provider must speak to Lum")
    need(cloudflareProvider.get("cabinetAware") is True,"provider must be cabinet aware")
    need(cloudflareProvider.get("cabinetMember") is False,"provider must not be cabinet member")

if cabinetPath.is_file():
    cabinetDoc=json.loads(cabinetPath.read_text())
    externalProviders=cabinetDoc.get("externalProviders",{})
    cf=ext.get("cloudflareAiProvider",{})
    need(cloudflareProvider.get("returnsTo")=="lum","cabinet provider must return to Lum")
    need(cloudflareProvider.get("directGoddessRouting") is False,"cabinet direct routing leak")

if truthPath.is_file():
    truthDoc=json.loads(truthPath.read_text())
    cf=truth.get("aiProviders",{}).get("cloudflareAiProvider",{})
    need(cloudflareProvider.get("contract")=="doctrine/cloudflareAiProviderV1.json","source truth provider contract missing")
    need(cloudflareProvider.get("status")=="candidateContractOnly","source truth must not claim live provider")

if skillPath.is_file():
    skillText=skillPath.read_text()
    for token in ("Lum is the only conversational boss","Urd is the doctor goddess","Belldandy is the secretary goddess","Skuld is the research goddess","successful API response is `OBSERVED`, not GREEN"):
        need(token in skillText,f"skill missing token: {token}")

print(json.dumps({
  "schema":"luhmOs.cloudflareAiProviderAudit.v1",
  "status":"greenCloudflareAiProviderCandidate" if not errors else "redCloudflareAiProviderCandidate",
  "cabinetAware":True,
  "cabinetMember":False,
  "providerAuthority":False,
  "crownStatus":"stop",
  "errors":errors
},indent=2))
raise SystemExit(1 if errors else 0)

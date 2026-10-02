#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import pathlib
import py_compile
import re
import sys

rootPath = pathlib.Path(__file__).resolve().parents[1]
violations = []

def requireTruth(isTrue, message):
    if not isTrue:
        violations.append(message)

def loadJson(relPath):
    path = rootPath / relPath
    requireTruth(path.is_file(), f"missing {relPath}")
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        violations.append(f"invalid json {relPath}: {exc}")
        return {}

enterpriseScope = loadJson("doctrine/MCP_ENTERPRISE_SCOPE_V1.json")
cryptoDoc = loadJson("doctrine/enterpriseCryptoV1.json")
gatewayDoc = loadJson("doctrine/providerEnterpriseGatewayV1.json")
providerDoc = loadJson("doctrine/providerOrchestraV1.json")
accountEvidence = loadJson("doctrine/providerAccountEvidenceV1.json")

gatewayPath = rootPath / "host/providers/providerGateway.py"
adapterPaths = {
    "openAi": rootPath / "host/providers/openAiProvider.py",
    "googleAi": rootPath / "host/providers/googleAiProvider.py",
    "cloudflare": rootPath / "host/providers/cloudflareAiProvider.py",
}

requireTruth(enterpriseScope.get("cryptographyDoctrine") == "doctrine/enterpriseCryptoV1.json", "enterprise crypto pointer drift")
requireTruth(enterpriseScope.get("providerGatewayDoctrine") == "doctrine/providerEnterpriseGatewayV1.json", "enterprise provider gateway pointer missing")
gitHubLayer = enterpriseScope.get("gitHubCompatibilityLayer", {})
requireTruth(gitHubLayer.get("order") == 2, "GitHub is not compatibility layer #2 in enterprise scope")
requireTruth(gitHubLayer.get("exactSourceReceiptsRequired") is True, "GitHub exact-source receipt law missing")

secretLaw = cryptoDoc.get("secretLaw", {})
for fieldName in (
    "secretValuesInGit",
    "secretValuesInPrompts",
    "secretValuesInBrowser",
    "secretValuesInJquery",
    "secretValuesInGodot",
    "secretValuesInAndroidApk",
    "secretValuesInDriveMetadata",
):
    requireTruth(secretLaw.get(fieldName) is False, f"crypto secret boundary drift: {fieldName}")
requireTruth(secretLaw.get("logRedactionRequired") is True, "log redaction law missing")

adapterContract = gatewayDoc.get("adapterContract", {})
requireTruth(adapterContract.get("interface") == "host/providers/providerGateway.py", "gateway implementation pointer drift")
for fieldName in (
    "directProviderCallsFromJquery",
    "directProviderCallsFromGodot",
    "directProviderCallsFromAndroid",
    "directProviderCallsFromAgents",
):
    requireTruth(adapterContract.get(fieldName) is False, f"provider bypass leak: {fieldName}")

compatChain = gatewayDoc.get("compatibilityChain", [])
requireTruth(len(compatChain) >= 2 and compatChain[1] == "githubCompatibilityLayer2", "gateway compatibility chain lost GitHub layer #2")

providerGateway = providerDoc.get("enterpriseGateway", {})
requireTruth(providerGateway.get("contract") == "doctrine/providerEnterpriseGatewayV1.json", "provider orchestra gateway contract missing")
requireTruth(providerGateway.get("implementation") == "host/providers/providerGateway.py", "provider orchestra gateway implementation missing")
requireTruth(providerGateway.get("gitHubCompatibilityLayerOrder") == 2, "provider orchestra GitHub layer #2 drift")
requireTruth(providerGateway.get("failClosed") is True, "provider gateway must fail closed")

for providerId in ("openAi", "googleAi", "cloudflare"):
    providerState = providerDoc.get("providers", {}).get(providerId, {})
    requireTruth(providerState.get("adapterState") == "green", f"{providerId} adapter is not green")
    requireTruth(providerState.get("mayGrantGreen") is False, f"{providerId} provider gained GREEN authority")

requireTruth(providerDoc.get("providers", {}).get("googleAi", {}).get("entitlementState") != "green", "Google AI entitlement falsely green")
requireTruth(providerDoc.get("providers", {}).get("cloudflare", {}).get("entitlementState") != "green", "Cloudflare entitlement falsely green")

googleEvidence = accountEvidence.get("providers", {}).get("googleAi", {})
requireTruth(googleEvidence.get("accountState") == "green", "Google AI account evidence missing")
requireTruth(googleEvidence.get("planState") == "green", "Google AI plan evidence missing")
requireTruth(googleEvidence.get("apiCredentialState") == "unknown", "Google AI API credential falsely proven")

cloudflareEvidence = accountEvidence.get("providers", {}).get("cloudflare", {})
requireTruth(cloudflareEvidence.get("accountState") == "green", "Cloudflare account evidence missing")
requireTruth(cloudflareEvidence.get("zoneState") == "green", "Cloudflare zone evidence missing")
requireTruth(cloudflareEvidence.get("workersAiEntitlementState") == "unknown", "Cloudflare Workers AI entitlement falsely proven")

for path in (gatewayPath, *adapterPaths.values()):
    requireTruth(path.is_file(), f"missing {path.relative_to(rootPath)}")
    if path.is_file():
        try:
            py_compile.compile(str(path), doraise=True)
        except Exception as exc:
            violations.append(f"python syntax {path.relative_to(rootPath)}: {exc}")

if gatewayPath.is_file():
    gatewayText = gatewayPath.read_text(encoding="utf-8")
    for phrase in (
        "providerSpecs",
        "getCredentialState",
        "healthPacket",
        "invoke",
        '"providerSuccessMeans" = "observed"' if False else 'result["providerSuccessMeans"] = "observed"',
        'result["greenAuthority"] = False',
        'result["crownStatus"] = "stop"',
    ):
        requireTruth(phrase in gatewayText, f"provider gateway missing {phrase}")

for providerId, path in adapterPaths.items():
    if path.is_file():
        textValue = path.read_text(encoding="utf-8")
        requireTruth("def isConfigured()" in textValue, f"{providerId} adapter missing isConfigured")
        requireTruth("def invoke(" in textValue, f"{providerId} adapter missing invoke")

cloudflareText = adapterPaths["cloudflare"].read_text(encoding="utf-8") if adapterPaths["cloudflare"].is_file() else ""
requireTruth("DNS, TLS, tunnel, and public-exposure authority" in cloudflareText, "Cloudflare network separation comment missing")

secretLikeRx = re.compile(r"\b(?:sk-(?:proj-)?[A-Za-z0-9_-]{20,}|AIza[0-9A-Za-z_-]{30,}|ghp_[A-Za-z0-9]{20,}|hf_[A-Za-z0-9]{20,})\b")
for relPath in (
    "doctrine/enterpriseCryptoV1.json",
    "doctrine/providerEnterpriseGatewayV1.json",
    "doctrine/providerOrchestraV1.json",
    "doctrine/providerAccountEvidenceV1.json",
    "host/providers/providerGateway.py",
    "host/providers/openAiProvider.py",
    "host/providers/googleAiProvider.py",
    "host/providers/cloudflareAiProvider.py",
):
    path = rootPath / relPath
    if path.is_file():
        requireTruth(secretLikeRx.search(path.read_text(encoding="utf-8")) is None, f"secret-like literal in {relPath}")

print(json.dumps({
    "schema":"luhmOs.providerEnterpriseGatewayAudit.v1",
    "status":"greenProviderEnterpriseGateway" if not violations else "redProviderEnterpriseGateway",
    "githubCompatibilityLayer":2,
    "adapterGreen":["openAi","googleAi","cloudflare"],
    "accountEvidence":{
        "openAi":"observed",
        "googleAi":"pendingProviderHandshake",
        "cloudflare":"pendingProviderHandshake",
        "huggingFace":"observed",
        "render":"observed"
    },
    "violations":violations,
    "crownStatus":"stop"
}, indent=2))
raise SystemExit(1 if violations else 0)

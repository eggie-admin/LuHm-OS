#!/usr/bin/env python3
from __future__ import annotations

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

providerDoc = loadJson("doctrine/providerOrchestraV1.json")
sentryDoc = loadJson("doctrine/googleSentryAuthV1.json")
artSchemaDoc = loadJson("doctrine/yumeArtSchemaV1.json")
betaDoc = loadJson("doctrine/yumeArtChatBetaV1.json")
hfDoc = loadJson("doctrine/huggingFaceArtUtilityV1.json")

openAiPath = rootPath / "host/providers/openAiProvider.py"
yumeSkillPath = rootPath / "agents/yumeArtOni/SKILL.md"
requirementsPath = rootPath / "host/mcp/requirements.txt"
copilotPath = rootPath / ".github/copilot-instructions.md"
yumePluginPath = rootPath / "frontEnd/jquery/luhmYumeBooth.js"
oldYumePluginPath = rootPath / "frontEnd/jquery/luhm.yumeBooth.js"
frontEndIndexPath = rootPath / "frontEnd/index.html"
frontEndAppPath = rootPath / "frontEnd/app.js"
harnessPath = rootPath / "host/mcp/luhmHarness.py"
widgetPath = rootPath / "host/harness/widget.html"
mcpConfigPath = rootPath / "plugins/luhm-os/mcp.json"
hfSharedPath = rootPath / "agents/shared/huggingFaceCapabilityLawV1.md"
hfSkillPaths = [
    rootPath / "agents/lum/SKILL.md",
    rootPath / "agents/urdMutationOni/SKILL.md",
    rootPath / "agents/belldandyQualityOni/SKILL.md",
    rootPath / "agents/skuldResearchOni/SKILL.md",
    rootPath / "agents/yumeArtOni/SKILL.md",
    rootPath / "agents/sumiAssetOni/SKILL.md",
    rootPath / "agents/momoResearchOni/SKILL.md",
    rootPath / "agents/shioriCriticOni/SKILL.md",
    rootPath / "agents/kiriContextOni/SKILL.md",
]

for path in (openAiPath, yumeSkillPath, requirementsPath, copilotPath, yumePluginPath, frontEndIndexPath, frontEndAppPath, harnessPath, widgetPath, mcpConfigPath, hfSharedPath, *hfSkillPaths):
    requireTruth(path.is_file(), f"missing {path.relative_to(rootPath)}")

if openAiPath.is_file():
    try:
        py_compile.compile(str(openAiPath), doraise=True)
    except Exception as exc:
        violations.append(f"OpenAI provider syntax: {exc}")
    providerText = openAiPath.read_text(encoding="utf-8")
    for required in (
        "client.responses.create(",
        "store=False",
        "X-Client-Request-Id",
        "providerSuccessMeans",
        '"greenAuthority": False',
        '"crownStatus": "stop"',
    ):
        requireTruth(required in providerText, f"OpenAI adapter missing {required}")
    requireTruth("OPENAI_API_KEY" in providerText, "OpenAI server credential binding missing")

if requirementsPath.is_file():
    requirementsText = requirementsPath.read_text(encoding="utf-8")
    requireTruth("openai==3.22.0" in requirementsText, "official OpenAI SDK pin missing")

openAi = providerDoc.get("providers", {}).get("openAi", {})
requireTruth(openAi.get("apiSurface") == "responsesApi", "OpenAI Responses API drift")
requireTruth(openAi.get("secretBoundary") == "serverEnvironmentOnly", "OpenAI secret boundary drift")
requireTruth(openAi.get("mayGrantGreen") is False, "OpenAI gained GREEN authority")
modes = openAi.get("integrationModes", {})
requireTruth(modes.get("chatGptMcpApp", {}).get("requiresLuhmOpenAiApiKey") is False, "ChatGPT MCP incorrectly requires LuHm API key")
requireTruth(modes.get("directOpenAiApi", {}).get("requiresLuhmOpenAiApiKey") is True, "direct OpenAI API credential law missing")
requireTruth(modes.get("directOpenAiApi", {}).get("defaultStore") is False, "direct OpenAI API store=false law missing")

compatLayers = providerDoc.get("compatibilityLayers", [])
githubLayers = [row for row in compatLayers if row.get("id") == "github"]
requireTruth(bool(githubLayers) and githubLayers[0].get("order") == 2, "GitHub is not compatibility layer #2")
githubProvider = providerDoc.get("providers", {}).get("github", {})
requireTruth("secondCompatibilityLayer" in githubProvider.get("roles", []), "GitHub compatibility role missing")

identityProvider = sentryDoc.get("identityProvider", {})
requireTruth(identityProvider.get("role") == "identitySentryOnly", "Google Sentry role drift")
requireTruth(identityProvider.get("mayGrantHydraAuthority") is False, "Google Sentry authority leak")
sessionLaw = sentryDoc.get("sessionLaw", {})
for fieldName in ("httpOnlyCookie","secureCookie","csrfDefense","pkce","state","nonce","revocable"):
    requireTruth(sessionLaw.get(fieldName) is True, f"Google Sentry missing {fieldName}")
for fieldName in ("refreshTokenNeverInBrowser","providerTokensNeverInJquery","providerTokensNeverInGodot","providerTokensNeverInApk"):
    requireTruth(sessionLaw.get(fieldName) is True, f"credential boundary missing {fieldName}")

queryRules = artSchemaDoc.get("queryRules", {})
for fieldName in ("noRawDoctrineScanFromJquery","noDriveFolderCrawlFromJquery","noProviderCredentialReadFromYume","boundedRowsOnly","idsAndHashesTravelWithRows"):
    requireTruth(queryRules.get(fieldName) is True, f"Yume schema missing {fieldName}")

requireTruth(betaDoc.get("contracts", {}).get("artSchema") == "doctrine/yumeArtSchemaV1.json", "Yume beta art schema binding missing")
requireTruth(betaDoc.get("contracts", {}).get("googleSentry") == "doctrine/googleSentryAuthV1.json", "Yume beta Google Sentry binding missing")
requireTruth(betaDoc.get("githubSecondCompatibilityLayer", {}).get("enabled") is True, "Yume beta GitHub compatibility binding missing")

hfPrivacy = hfDoc.get("privacyAndArtLaw", {})
requireTruth(hfPrivacy.get("providerOutputIsCandidateOnly") is True, "HF output authority drift")
requireTruth(hfDoc.get("providerMayGrantCanon") is False, "HF canon authority leak")
requireTruth(hfDoc.get("providerMayGrantGreen") is False, "HF GREEN authority leak")

hfProvider = providerDoc.get("providers", {}).get("huggingFace", {})
requireTruth(hfProvider.get("sharedLaw") == "agents/shared/huggingFaceCapabilityLawV1.md", "HF shared law binding missing")
requireTruth(hfProvider.get("directWorkerDispatch") is False, "HF direct worker dispatch leak")
requireTruth(hfProvider.get("lumDispatchRequired") is True, "HF Lum dispatch gate missing")

if hfSharedPath.is_file():
    hfSharedText = hfSharedPath.read_text(encoding="utf-8")
    for phrase in ("signs and dispatches every provider job", "Temporary CPU/GPU Jobs require an explicit bounded task", "Provider output is `observed`"):
        requireTruth(phrase in hfSharedText, f"HF shared law missing {phrase}")

for skillPath in hfSkillPaths:
    if skillPath.is_file():
        requireTruth("huggingFaceCapabilityLawV1.md" in skillPath.read_text(encoding="utf-8"), f"{skillPath.relative_to(rootPath)} missing HF acquaintance")

if yumeSkillPath.is_file():
    yumeText = yumeSkillPath.read_text(encoding="utf-8")
    for phrase in (
        "Schema-focused creation and file management",
        "Orchestra acquaintance",
        "Google Sentry interaction",
        "getCutscenePackage",
        "GitHub/Copilot",
        "Hugging Face",
        "Big Brother",
    ):
        requireTruth(phrase in yumeText, f"Yume skill missing {phrase}")

if copilotPath.is_file():
    copilotText = copilotPath.read_text(encoding="utf-8")
    requireTruth("second compatibility layer" in copilotText, "Copilot missing GitHub compatibility law")
    requireTruth("doctrine/yumeArtSchemaV1.json" in copilotText, "Copilot missing Yume schema")

requireTruth(not oldYumePluginPath.exists(), "legacy dotted Yume plugin path still exists")
if yumePluginPath.is_file():
    pluginText = yumePluginPath.read_text(encoding="utf-8")
    requireTruth('const pluginName = "luhmYumeBooth"' in pluginText, "Yume jQuery plugin identity drift")
    requireTruth('"cutsceneRequested"' in pluginText, "Yume cutscene event missing")
    requireTruth('"hfCapabilityRequested"' in pluginText, "Yume HF lab event missing")
    requireTruth('dispatchedBy: "lum"' in pluginText, "Yume HF lab bypasses Lum")
    requireTruth("requestAnimationFrame" in pluginText, "Yume parallax loop missing")

if frontEndIndexPath.is_file():
    frontEndIndexText = frontEndIndexPath.read_text(encoding="utf-8")
    requireTruth("./jquery/luhmYumeBooth.js" in frontEndIndexText, "Yume plugin not loaded by cockpit")
    requireTruth("data-yume-booth" in frontEndIndexText, "Yume booth DOM missing")
    requireTruth("HF LAB // SPECIAL EFFECTS DEPARTMENT" in frontEndIndexText, "HF lab UI missing")
    requireTruth('data-yume-hf="depthMap"' in frontEndIndexText, "HF depth action missing")
    requireTruth('data-yume-hf="imageTo3dResearch"' in frontEndIndexText, "HF 3D scout action missing")

if frontEndAppPath.is_file():
    frontEndAppText = frontEndAppPath.read_text(encoding="utf-8")
    requireTruth("luhmYumeBooth" in frontEndAppText, "Yume booth not initialized")
    requireTruth("yume_cutscene_requested" in frontEndAppText, "Yume native cutscene bridge event missing")

if harnessPath.is_file():
    harnessText = harnessPath.read_text(encoding="utf-8")
    requireTruth('@server.custom_route("/cockpit/"' in harnessText, "Render cockpit route missing")
    requireTruth('"jquery/luhmYumeBooth.js"' in harnessText, "Render Yume plugin route missing")

if widgetPath.is_file():
    widgetText = widgetPath.read_text(encoding="utf-8")
    requireTruth('id="yume"' in widgetText, "MCP widget Yume card missing")
    requireTruth('origin+"/cockpit/"' in widgetText, "MCP widget cockpit handoff missing")

if mcpConfigPath.is_file():
    mcpConfig = json.loads(mcpConfigPath.read_text(encoding="utf-8"))
    requireTruth(
        mcpConfig.get("mcpServers", {}).get("luhm", {}).get("url") == "https://luhm-os-yume-autobeta.onrender.com/mcp",
        "beta plugin MCP does not point at Yume auto-beta edge"
    )

betaDeployment = betaDoc.get("betaDeployment", {})
requireTruth(betaDeployment.get("mode") == "autoDeploy", "beta auto-deploy doctrine missing")
requireTruth(betaDeployment.get("autoDeploy") is True, "beta auto-deploy disabled in doctrine")
requireTruth(betaDeployment.get("dnsMutation") is False, "beta deploy unexpectedly mutates DNS")

secretRx = re.compile(r"\b(?:sk-(?:proj-)?[A-Za-z0-9_-]{20,}|AIza[0-9A-Za-z_-]{30,}|ghp_[A-Za-z0-9]{20,})\b")
for relPath in (
    "doctrine/providerOrchestraV1.json",
    "doctrine/googleSentryAuthV1.json",
    "doctrine/yumeArtSchemaV1.json",
    "doctrine/yumeArtChatBetaV1.json",
    "doctrine/huggingFaceArtUtilityV1.json",
    "host/providers/openAiProvider.py",
    "agents/yumeArtOni/SKILL.md",
):
    path = rootPath / relPath
    if path.is_file():
        requireTruth(secretRx.search(path.read_text(encoding="utf-8")) is None, f"secret-like literal in {relPath}")

print(json.dumps({
    "schema":"luhmOs.yumeProviderBetaAudit.v1",
    "status":"greenYumeProviderBeta" if not violations else "redYumeProviderBeta",
    "checks":{
        "googleSentry":True,
        "openAiResponses":True,
        "githubCompatibilityLayer2":True,
        "huggingFaceUtilityLane":True,
        "yumeSqlStyleSchema":True
    },
    "violations":violations,
    "crownStatus":"stop"
}, indent=2))
raise SystemExit(1 if violations else 0)

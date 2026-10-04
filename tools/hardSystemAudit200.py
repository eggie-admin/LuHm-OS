#!/usr/bin/env python3
import ast
import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def exists(path):
    return (ROOT / path).exists()

def py_ok(path):
    try:
        ast.parse((ROOT / path).read_text(encoding="utf-8"), filename=path)
        return True
    except Exception:
        return False

def camel(value):
    return bool(re.fullmatch(r"[a-z][A-Za-z0-9]*", value))

def doctrine_camel_path(path):
    name = Path(path).name
    if name.endswith(".template.json"):
        stem = name[:-len(".template.json")]
    elif name.endswith(".json"):
        stem = name[:-5]
    else:
        return True
    return camel(stem)

def all_keys_camel(value):
    if isinstance(value, dict):
        return all(camel(str(k)) and all_keys_camel(v) for k, v in value.items())
    if isinstance(value, list):
        return all(all_keys_camel(v) for v in value)
    return True

def collect_doctrine_refs(value, path=()):
    out = []
    if isinstance(value, str) and value.startswith("doctrine/") and value.endswith(".json"):
        out.append((path, value))
    elif isinstance(value, dict):
        for k, v in value.items():
            out.extend(collect_doctrine_refs(v, path + (k,)))
    elif isinstance(value, list):
        for i, v in enumerate(value):
            out.extend(collect_doctrine_refs(v, path + (str(i),)))
    return out

truth = load("doctrine/currentSourceTruthV3.json")
control = load("doctrine/luhmAiControlPlaneV1.json")
chat = load("doctrine/projectChatCanonV1.json")
covenant = load("doctrine/everlastingCovenantV1.json")
lane = load("doctrine/proposedWorkingLaneV1.json")
naming = load("doctrine/camelHumpDoctrineLawV1.json")
format_law = load("doctrine/currentFormatLawV1.json")
manifest_law = load("doctrine/aiManifestFormatV1.json")
python_law = load("doctrine/python3ControlPlaneLawV1.json")
ai_manifest = load("doctrine/aiTaskManifestV2.template.json")
training = load("doctrine/agentTrainingSealV1.json")
urd = load("doctrine/urdEvidenceAdjudicationV1.json")
sprites = load("doctrine/agentLoadingSpriteManifestV1.json")
runtime_sprites = load("host/harness/agent-loading-sprites.json")
big = load("doctrine/bigBrotherCovenantV1.json")
economy = load("doctrine/providerEconomyV1.json")
openai = load("doctrine/openAiDeploymentV3.json")
content = load("doctrine/contentLaneDoctrineV1.json")
matrix = load("doctrine/assetEligibilityMatrixV1.json")
yume = load("doctrine/yumeCreativePipelineV1.json")
yume_desk = load("doctrine/yumeBigBrotherArtDeskV1.json")
yume_work = load("doctrine/yumeArtistWorkstationV1.json")
yume_edu = load("doctrine/yumeArtEducationV1.json")
campaign = load("doctrine/unifiedCampaignWorkbenchV1.json")
patronage = load("doctrine/patronageCampaignV1.json")
plugin = load("doctrine/pluginPublicationV2.json")
plugin_milestone = load("doctrine/chatGptPluginMilestoneV2.json")
mcp_scope = load("doctrine/mcpEnterpriseScopeV2.json")
android = load("doctrine/androidWeb3CockpitV2.json")
bridge = load("doctrine/androidWeb3BridgeV2.json")
antenna = load("doctrine/samsungAntennaV1.json")
release = load("doctrine/releaseBoundaryV2.json")
roadmap = load("doctrine/chatDeploymentRoadmapV1.json")
audit_contract = load("doctrine/hardSystemAuditV1.json")

checks = []
def add(domain, name, ok):
    checks.append((domain, name, bool(ok)))

expected_guard = ["sanityCheck","audit","ingest","mutation","test","apply","continue","deploy"]
agents = control.get("agents", {})
agent_ids = list(agents.keys())
legacy_refs = truth.get("legacyArtifacts", {})
active_truth_refs = [
    ref for p, ref in collect_doctrine_refs(truth)
    if not p or p[0] != "legacyArtifacts"
]

# 01-20 sourceGovernance
g = [
("truthSchema", truth.get("schema") == "luhmOs.currentSourceTruth.v3"),
("truthStatus", truth.get("status") == "AMBER_PROPOSED_SEAL_OF_TRUTH"),
("truthAuthority", truth.get("authority") == "Professor"),
("sourceLaw", truth.get("sourceLaw") == "AI proposes. Policy authorizes. CI proves. Human promotes."),
("promotionFalse", truth.get("promotion") is False),
("publicationFalse", truth.get("publicationAuthority") is False),
("releaseFalse", truth.get("releaseAuthority") is False),
("signingFalse", truth.get("productionSigningAuthority") is False),
("crownStop", truth.get("crownStatus") == "STOP"),
("workingLaneContract", truth.get("workingDoctrineLane",{}).get("contract") == "doctrine/proposedWorkingLaneV1.json"),
("workingLaneStatus", truth.get("workingDoctrineLane",{}).get("status") == "PROPOSED_ONLY"),
("workingLaneNoPromotion", truth.get("workingDoctrineLane",{}).get("currentMutationPromotion") is False),
("professorPromotionRequired", truth.get("workingDoctrineLane",{}).get("professorPromotionRequired") is True),
("historicalReceiptsHistorical", truth.get("workingDoctrineLane",{}).get("historicalReceiptsRemainHistorical") is True),
("covenantContract", truth.get("everlastingCovenant",{}).get("contract") == "doctrine/everlastingCovenantV1.json"),
("guardRail", truth.get("everlastingCovenant",{}).get("guardRail") == expected_guard),
("controlContract", truth.get("aiControlPlane",{}).get("contract") == "doctrine/luhmAiControlPlaneV1.json"),
("controlBoss", control.get("boss") == "lum"),
("chatBoss", chat.get("boss") == "lum"),
("roadmapBound", truth.get("roadmap") == "doctrine/chatDeploymentRoadmapV1.json"),
]
for n,o in g: add("sourceGovernance",n,o)

# 21-40 namingAndManifestFormat
good_sample = "big-brother-review-001.json"
bad_sample = "BigBrotherReview_001.json"
manifest_regex = manifest_law.get("fileNaming",{}).get("currentAiManifestFilenameRegex","")
g = [
("namingSchema", naming.get("schema") == "luhmOs.camelHumpDoctrineLaw.v1"),
("machineIdentifiersCamel", naming.get("currentNaming",{}).get("machineIdentifiers") == "lowerCamelHump"),
("doctrineBasenamesCamel", naming.get("currentNaming",{}).get("doctrineFileBasenames") == "lowerCamelHump"),
("jsonKeysCamel", naming.get("currentNaming",{}).get("jsonObjectKeys") == "lowerCamelHump"),
("agentIdsCamel", all(camel(x) for x in agent_ids)),
("formatLawSchema", format_law.get("schema") == "luhmOs.currentFormatLaw.v1"),
("formatNamesNamingLaw", format_law.get("specializedContracts",{}).get("doctrineNaming") == "doctrine/camelHumpDoctrineLawV1.json"),
("formatNamesManifestLaw", format_law.get("specializedContracts",{}).get("aiManifestFormat") == "doctrine/aiManifestFormatV1.json"),
("formatNamesPythonLaw", format_law.get("specializedContracts",{}).get("python3ControlPlane") == "doctrine/python3ControlPlaneLawV1.json"),
("manifestLawSchema", manifest_law.get("schema") == "luhmOs.aiManifestFormat.v1"),
("manifestKebabStyle", manifest_law.get("fileNaming",{}).get("currentAiManifestFilenameStyle") == "kebab-case"),
("manifestRegexGood", bool(re.fullmatch(manifest_regex, good_sample))),
("manifestRegexBad", not bool(re.fullmatch(manifest_regex, bad_sample))),
("aiTaskSchemaCurrent", "luhmOs.aiTaskManifest.v2" in manifest_law.get("currentSchemas",[])),
("aiTaskTemplateCurrent", "doctrine/aiTaskManifestV2.template.json" in manifest_law.get("currentTemplates",[])),
("aiTaskSchema", ai_manifest.get("schema") == "luhmOs.aiTaskManifest.v2"),
("aiTaskKeysCamel", all_keys_camel(ai_manifest)),
("yumeKebabTemplateCurrent", "agents/yumeArtOni/templates/big-brother-art-task-v1.template.json" in manifest_law.get("currentTemplates",[])),
("legacyRemoteManifestRegistered", manifest_law.get("legacyFormats",{}).get("remoteAiManifestV1") == "doctrine/remote-ai-manifest-v1.template.json"),
("activeDoctrineRefsCamel", all(doctrine_camel_path(p) for p in active_truth_refs)),
]
for n,o in g: add("namingAndManifestFormat",n,o)

# 41-60 agentAndUrdMigration
urd_agent = agents.get("urdDoctorGoddess",{})
g = [
("activeAgentCount15", len(agents) == 15),
("trainingCount15", training.get("expectedAgentCount") == 15),
("trainingRosterMatches", training.get("requiredAgents") == agent_ids),
("drNaoNotActive", "drNao" not in agents),
("drNaoLegacyRegistered", control.get("legacyAgentMigrations",{}).get("drNao",{}).get("activeAgent") is False),
("trainingDrNaoLegacy", training.get("legacyAgentMigrations",{}).get("drNao",{}).get("currentTrainingRoster") is False),
("urdAuthorityReadOnly", urd_agent.get("defaultAuthority") == "READ_ONLY"),
("urdAdjudicates", "adjudicateEvidence" in urd_agent.get("capabilities",[])),
("urdSourceIdentity", "sourceIdentityCheck" in urd_agent.get("capabilities",[])),
("urdReceiptValidity", "receiptValidityCheck" in urd_agent.get("capabilities",[])),
("urdPhysicalBoundary", "physicalDeviceEvidenceBoundary" in urd_agent.get("capabilities",[])),
("urdVerdict", "deterministicVerdict" in urd_agent.get("capabilities",[])),
("urdContractSchema", urd.get("schema") == "luhmOs.urdEvidenceAdjudication.v1"),
("urdContractOwner", urd.get("owner") == "urdDoctorGoddess"),
("urdStatePrecedence", urd.get("statePrecedence") == ["ERROR","RED","UNKNOWN","AMBER","GREEN"]),
("urdLegacyInactive", urd.get("legacyTreatment",{}).get("drNaoActiveAgent") is False),
("proofRouteUrd", control.get("routeProfiles",{}).get("proof") == ["lum","urdDoctorGoddess"]),
("releaseRouteUrd", "urdDoctorGoddess" in control.get("routeProfiles",{}).get("release",[]) and "drNao" not in control.get("routeProfiles",{}).get("release",[])),
("spriteRosterNoDrNao", "drNao" not in sprites.get("agentIds",[]) and len(sprites.get("agentIds",[])) == 15),
("runtimeSpritesNoDrNao", all(x.get("agentId") != "drNao" for x in runtime_sprites.get("sprites",[]))),
]
for n,o in g: add("agentAndUrdMigration",n,o)

# 61-80 providerArchitecture
g = [
("bigSchema", big.get("schema") == "luhmOs.bigBrotherCovenant.v1"),
("bigProviderId", big.get("providerId") == "googleAi"),
("bigNickname", big.get("providerNickname") == "bigBrother"),
("bigNotEdge", big.get("identityLaw",{}).get("bigBrotherIsNotEdgeGallery") is True),
("bigManifestV2", big.get("taskLaw",{}).get("manifestSchema") == "luhmOs.aiTaskManifest.v2"),
("bigManifestTemplate", big.get("taskLaw",{}).get("template") == "doctrine/aiTaskManifestV2.template.json"),
("bigManifestKebab", big.get("taskLaw",{}).get("filenameStyle") == "kebab-case.json"),
("bigCandidateEvidence", big.get("taskLaw",{}).get("outputIsCandidateEvidence") is True),
("bigLumReconcile", big.get("taskLaw",{}).get("lumReconciliationRequired") is True),
("bigNoGreen", big.get("providerAuthority",{}).get("mayGrantGreen") is False),
("bigNoCrown", big.get("providerAuthority",{}).get("mayGrantCrown") is False),
("bigNoMerge", big.get("providerAuthority",{}).get("mayMerge") is False),
("economySchema", economy.get("schema") == "luhmOs.providerEconomy.v1"),
("economyHq", economy.get("headquarters") == "luhmOs"),
("economyBigRole", economy.get("bigBrother",{}).get("role") == "highCapacityExternalWorker"),
("economyOpenRole", economy.get("openDaddy",{}).get("role") == "scarcePremiumCapability"),
("economyNoVendorAuthority", economy.get("experienceLaw",{}).get("vendorEntitlementDoesNotDefineArchitecture") is True),
("openAiSchema", openai.get("schema") == "luhmOs.openAiDeployment.v3"),
("openAiNoDrNao", openai.get("architecture",{}).get("drNaoActive") is False and len(openai.get("architecture",{}).get("activeAgents",[])) == 15),
("openAiNoEmbeddedSecrets", openai.get("openAi",{}).get("credentialInGit") is False and openai.get("openAi",{}).get("credentialInApk") is False),
]
for n,o in g: add("providerArchitecture",n,o)

# 81-100 creativeAndCampaign
g = [
("contentSchema", content.get("schema") == "luhmOs.contentLaneDoctrine.v1"),
("oneCanon", content.get("canonLaw",{}).get("oneCharacterCanon") is True),
("noSplitCanon", content.get("canonLaw",{}).get("separateCharacterCanonsPerLane") is False),
("privateNotPublic", content.get("lanes",{}).get("privateMutation",{}).get("publicDistributionAllowed") is False),
("betaNotPublic", content.get("lanes",{}).get("betaAfterDark",{}).get("publicDistributionAllowed") is False),
("publicFamily", content.get("lanes",{}).get("cathedralPublic",{}).get("maturityCeiling") == "familySafe"),
("adultLock", content.get("adultLock",{}).get("allSexualizedPresentationRequiresAdultCharacter") is True),
("matrixFailClosed", matrix.get("fallbackLaw",{}).get("missingLaneMetadata") == "failClosed"),
("yumeWorkstation", yume.get("artistWorkstation") == "doctrine/yumeArtistWorkstationV1.json"),
("yumeEducation", yume.get("artEducation") == "doctrine/yumeArtEducationV1.json"),
("fineArtTrack", yume_edu.get("fineArtTrack",{}).get("role") == "meaningFormAndVisualLanguage"),
("commercialTrack", yume_edu.get("commercialArtTrack",{}).get("role") == "reproductionProductionAndDelivery"),
("publicGenAiForbidden", yume_work.get("publicAuthorshipLaw",{}).get("publicGenerativeAiDefault") == "FORBIDDEN_UNLESS_PROFESSOR_CHANGES_POLICY"),
("bigBrotherDoesNotReplaceYume", yume_desk.get("siblingLaw",{}).get("bigBrotherMayReplaceYume") is False),
("yumeTaskKebab", yume_desk.get("taskPacket",{}).get("template") == "agents/yumeArtOni/templates/big-brother-art-task-v1.template.json"),
("campaignDraftOnly", campaign.get("status") == "PROPOSED_DRAFT_ONLY"),
("campaignEvidenceUrd", campaign.get("evidenceLead") == "urdDoctorGoddess"),
("campaignNoAutoCrossPost", "noAutomatedCrossPosting" in campaign.get("socialLaw",[])),
("patronageNoAutoSend", patronage.get("campaignState",{}).get("automaticSend") is False),
("patronageProfessorReview", patronage.get("campaignState",{}).get("professorReviewRequiredBeforeEachSend") is True),
]
for n,o in g: add("creativeAndCampaign",n,o)

# 101-120 pluginAndMcp
server_text = (ROOT / "host/mcp/luhmMcpServer.py").read_text(encoding="utf-8")
g = [
("pluginSchema", plugin.get("schema") == "luhmOs.pluginPublication.v2"),
("pluginReadOnly", plugin.get("runtime",{}).get("toolsReadOnly") is True),
("pluginNoWrite", plugin.get("runtime",{}).get("writeToolsAllowed") is False),
("pluginNoDestructive", plugin.get("runtime",{}).get("destructiveToolsAllowed") is False),
("pluginMilestoneSchema", plugin_milestone.get("schema") == "luhmOs.chatGptPluginMilestone.v2"),
("pluginMilestoneServer", plugin_milestone.get("runtime",{}).get("server") == "host/mcp/luhmMcpServer.py"),
("pluginExternalPending", "approvedChatGptConnectionTest" in plugin_milestone.get("remainingGates",[])),
("mcpScopeSchema", mcp_scope.get("schema") == "luhmOs.mcpEnterpriseScope.v2"),
("mcpStateless", mcp_scope.get("transport",{}).get("statelessHttp") is True),
("mcpNoSessionAuthority", mcp_scope.get("transport",{}).get("sessionOwnsAuthority") is False),
("mcpNoSessionTruth", mcp_scope.get("transport",{}).get("sessionOwnsSourceTruth") is False),
("mcpWriteNeedsOauth", mcp_scope.get("authentication",{}).get("privateOrWriteToolsRequireOauth21") is True),
("mcpOauthNotClaimed", mcp_scope.get("authentication",{}).get("oauthImplemented") is False),
("serverPython", py_ok("host/mcp/luhmMcpServer.py")),
("serverCurrentTruth", 'currentSourceTruthV3.json' in server_text),
("serverCurrentControl", 'luhmAiControlPlaneV1.json' in server_text),
("serverCurrentMcpScope", 'mcpEnterpriseScopeV2.json' in server_text),
("serverCurrentOpenAi", 'openAiDeploymentV3.json' in server_text),
("serverNoLegacyControlConstant", 'ONI_MESH_CONTROL_PLANE_V2.json' not in server_text),
("serverNoActiveDrNaoMap", '"DrNao": "doctorOni"' not in server_text),
]
for n,o in g: add("pluginAndMcp",n,o)

# 121-140 androidAndSamsungAntenna
g = [
("androidSchema", android.get("schema") == "luhmOs.androidWeb3Cockpit.v2"),
("androidBridgeCurrent", android.get("bridgeContract") == "doctrine/androidWeb3BridgeV2.json"),
("androidReleaseCurrent", android.get("releaseBoundary") == "doctrine/releaseBoundaryV2.json"),
("androidShellFalse", android.get("targetArchitecture",{}).get("shellAuthority") is False),
("androidNoArbitraryShell", android.get("targetArchitecture",{}).get("arbitraryShell") == "FORBIDDEN"),
("androidPhysicalPending", android.get("currentEvidence",{}).get("physicalSamsungWebViewProof") == "PENDING"),
("bridgeSchema", bridge.get("schema") == "luhmOs.androidWeb3Bridge.v2"),
("bridgeExactOrigin", bridge.get("security",{}).get("exactOriginOnly") is True),
("bridgeNoCommands", bridge.get("security",{}).get("arbitraryCommands") is False),
("bridgeNoShell", bridge.get("security",{}).get("shellAuthority") is False),
("antennaSchema", antenna.get("schema") == "luhmOs.samsungAntenna.v1"),
("antennaTarget", antenna.get("target") == "Samsung Galaxy S24 FE"),
("antennaTermux", antenna.get("architecture",{}).get("termuxRole") == "localControlPlaneAndMutationShell"),
("antennaX11", antenna.get("architecture",{}).get("termuxX11Role") == "localhostGraphicalDisplayPath"),
("antennaShizuku", antenna.get("architecture",{}).get("shizukuRole") == "explicitAndroidBinderPermissionBridge"),
("antennaLocalhost", antenna.get("networkLaw",{}).get("localhostFirst") is True),
("antennaNoPublicServer", antenna.get("architecture",{}).get("publicPhoneServer") is False),
("antennaExplicitPermission", antenna.get("mutationLaw",{}).get("shizukuPermissionMustBeExplicitlyGranted") is True),
("antennaNoWebShell", antenna.get("mutationLaw",{}).get("arbitraryWebToShellBridgeForbidden") is True),
("roadmapOrder", [x.get("id") for x in roadmap.get("stages",[])] == ["chatFoundation","chatGptPlugin","samsungAntenna"]),
]
for n,o in g: add("androidAndSamsungAntenna",n,o)

# 141-160 python3Authority
authority_files = python_law.get("currentAuthorityFiles",[])
g = [
("pythonLawSchema", python_law.get("schema") == "luhmOs.python3ControlPlaneLaw.v1"),
("pythonCanonical", python_law.get("canonicalLanguage") == "python3"),
("pythonAiOrchestration", "AI orchestration" in python_law.get("currentPython3Scopes",[])),
("pythonRouting", "task routing" in python_law.get("currentPython3Scopes",[])),
("pythonAudits", "source-truth audits" in python_law.get("currentPython3Scopes",[])),
("pythonEvidence", "evidence adjudication" in python_law.get("currentPython3Scopes",[])),
("pythonManifestValidation", "manifest validation" in python_law.get("currentPython3Scopes",[])),
("pythonMcp", "MCP server logic" in python_law.get("currentPython3Scopes",[])),
("authorityFilesPython", all(x.endswith(".py") for x in authority_files)),
("authorityFilesExist", all(exists(x) for x in authority_files)),
("routerPython", py_ok("tools/lumTaskRouter.py")),
("covenantAuditPython", py_ok("tools/everlastingCovenantAudit.py")),
("trainingAuditPython", py_ok("tools/agentTrainingAudit.py")),
("hardAuditPython", py_ok("tools/hardSystemAudit200.py")),
("mcpPython", py_ok("host/mcp/luhmMcpServer.py")),
("jsIsAdapter", "presentation adapter" in python_law.get("runtimeAdapterExceptions",{}).get("javascript","")),
("gdscriptIsAdapter", "runtime adapter" in python_law.get("runtimeAdapterExceptions",{}).get("gdscript","")),
("kotlinIsAdapter", "platform bridge" in python_law.get("runtimeAdapterExceptions",{}).get("kotlin","")),
("shellIsGlue", "glue" in python_law.get("runtimeAdapterExceptions",{}).get("shell","")),
("truthMcpLanguage", truth.get("mcpLayer",{}).get("language") == "python3"),
]
for n,o in g: add("python3Authority",n,o)

# 161-180 securityAndAuthority
g = [
("allAgentsNoRecruit", all(a.get("mayRecruit") is False for a in agents.values())),
("allAgentsNoSelfApprove", all(a.get("maySelfApprove") is False for a in agents.values())),
("controlProfessor", control.get("authority") == "Professor"),
("chatProfessor", chat.get("authority") == "professor"),
("covenantNoSelfPromotion", covenant.get("guardRail",{}).get("selfPromotion") is False),
("covenantNoAutoCrown", covenant.get("guardRail",{}).get("automaticCrown") is False),
("providerNoSelfApprove", big.get("providerAuthority",{}).get("maySelfApprove") is False),
("providerNoPublish", big.get("providerAuthority",{}).get("mayPublish") is False),
("providerNoSign", big.get("providerAuthority",{}).get("mayProductionSign") is False),
("campaignNoPublish", all(v.get("publicationAuthority") is False for v in campaign.get("channels",{}).values())),
("patronageNoBulkSend", patronage.get("campaignState",{}).get("bulkSend") is False),
("pluginNoPublication", plugin.get("publicationAuthority") is False),
("pluginNoDirectoryClaim", plugin.get("directoryPublicationProven") is False),
("mcpGreenFalse", mcp_scope.get("operations",{}).get("greenAuthority") is False),
("mcpPublicationFalse", mcp_scope.get("operations",{}).get("publicationAuthority") is False),
("releaseNoStable", "stablePromotion" in release.get("deniedActions",[])),
("releaseNoProductionSign", "productionSigning" in release.get("deniedActions",[])),
("releaseNoRemoteShell", "remoteShellExecution" in release.get("deniedActions",[])),
("publicLaneProviderCannotPromote", matrix.get("crossLaneRules",{}).get("providerCannotPromoteAsset") is True),
("professorFinalRoadmap", roadmap.get("providerTopology",{}).get("finalAuthority") == "Professor"),
]
for n,o in g: add("securityAndAuthority",n,o)

# 181-200 integrityAndLegacyIsolation
try:
    head = subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
except Exception:
    head = "UNKNOWN"
expected_source = os.environ.get("LUHM_SOURCE_REF","").strip()
try:
    diff_ok = subprocess.run(["git","diff","--check"],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True).returncode == 0
except Exception:
    diff_ok = False
legacy_required = [
    "doctrine/SOURCE_OF_TRUTH.json",
    "doctrine/ONI_MESH_CONTROL_PLANE_V2.json",
    "doctrine/PLUGIN_PUBLICATION_MILESTONE_20260930.json",
    "doctrine/ANDROID_WEB3_COCKPIT_SWITCH_V1.json",
    "doctrine/RELEASE_BOUNDARY.json"
]
current_required = [
    "doctrine/currentSourceTruthV3.json",
    "doctrine/luhmAiControlPlaneV1.json",
    "doctrine/releaseBoundaryV2.json",
    "doctrine/mcpEnterpriseScopeV2.json",
    "doctrine/openAiDeploymentV3.json",
    "doctrine/pluginPublicationV2.json",
    "doctrine/androidWeb3CockpitV2.json",
    "doctrine/androidWeb3BridgeV2.json",
    "doctrine/samsungAntennaV1.json",
    "doctrine/chatDeploymentRoadmapV1.json"
]
g = [
("auditContractSchema", audit_contract.get("schema") == "luhmOs.hardSystemAudit.v1"),
("auditRequired200", audit_contract.get("requiredPasses") == 200),
("auditTenDomains", len(audit_contract.get("domains",[])) == 10),
("auditTwentyPerDomain", audit_contract.get("passesPerDomain") == 20),
("auditFailClosed", audit_contract.get("failClosed") is True),
("sourceEnvPresent", bool(expected_source)),
("sourceMatchesHead", bool(expected_source) and expected_source == head),
("gitDiffCheck", diff_ok),
("legacyEvidenceFilesExist", all(exists(x) for x in legacy_required)),
("currentFilesExist", all(exists(x) for x in current_required)),
("oldSourceRegisteredLegacy", legacy_refs.get("priorSourceTruth") == "doctrine/SOURCE_OF_TRUTH.json"),
("oldMeshRegisteredLegacy", legacy_refs.get("priorOniMeshControlPlane") == "doctrine/ONI_MESH_CONTROL_PLANE_V2.json"),
("oldPluginRegisteredLegacy", legacy_refs.get("priorPluginPublicationMilestone") == "doctrine/PLUGIN_PUBLICATION_MILESTONE_20260930.json"),
("oldAndroidRegisteredLegacy", legacy_refs.get("priorAndroidWeb3CockpitContract") == "doctrine/ANDROID_WEB3_COCKPIT_SWITCH_V1.json"),
("oldReleaseRegisteredLegacy", legacy_refs.get("priorReleaseBoundary") == "doctrine/RELEASE_BOUNDARY.json"),
("oldRemoteManifestLegacy", legacy_refs.get("priorRemoteAiManifest") == "doctrine/remote-ai-manifest-v1.template.json"),
("controlNoLegacyRelease", control.get("inherits",{}).get("releaseBoundary") == "doctrine/releaseBoundaryV2.json"),
("chatLoadsCurrentTruth", "doctrine/currentSourceTruthV3.json" in chat.get("loadOrder",[])),
("currentRefsExist", all(exists(ref) for ref in active_truth_refs)),
("legacyCannotOwnAuthority", format_law.get("legacyPolicy",{}).get("mayOwnCurrentAuthority") is False),
]
for n,o in g: add("integrityAndLegacyIsolation",n,o)

if len(checks) != 200:
    raise SystemExit(f"HARD_AUDIT_CONFIGURATION_ERROR expected=200 actual={len(checks)}")

failed = []
for i, (domain, name, ok) in enumerate(checks, 1):
    print(f"{'PASS' if ok else 'FAIL'} {i:03d}/200 {domain}.{name}")
    if not ok:
        failed.append(f"{domain}.{name}")

state = "GREEN" if not failed else "RED"
print(f"HARD_SYSTEM_AUDIT={state}")
print(f"passes={200-len(failed)}/200")
print(f"sourceRef={head}")
print("legacyAuthority=false")
print("crown=STOP")
if failed:
    raise SystemExit("HARD_SYSTEM_AUDIT=RED failed=" + ",".join(failed))

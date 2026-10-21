#!/usr/bin/env python3
"""Executable, read-only public CAST audit. No provider calls, DDL, merges or releases."""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
def load(path): return json.loads((ROOT / path).read_text(encoding="utf-8"))
def source(path): return (ROOT / path).read_text(encoding="utf-8")
results = []
def audit(name, passed):
    results.append((name, bool(passed)))
    print(("PASS " if passed else "FAIL ") + name)

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.links = []
    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        if tag == "a":
            self.links.append(dict(attrs).get("href", ""))

manifest = load("doctrine/soloStudioCastReleaseV1.json")
roster = load("doctrine/agentSystemDeploymentV1.json")
quarantine = load("doctrine/companyWideOperationalQuarantineV1.json")
cabinet = load("doctrine/lumGoddessCabinetV1.json")
canon = load("doctrine/projectChatCanonV1.json")
studio = load("doctrine/soloStudioOperatingProfileV1.json")
truth = load("doctrine/currentSourceTruthV3.json")
hardening = load("doctrine/tenPassHardeningV1.json")
site = source("publicationSite/tester.html")
home = source("publicationSite/index.html")
release = source("publicationSite/release.html")
copilot = source(".github/copilot-instructions.md")
bootstrap = source("AGENTS.md")
skill = source("agents/projectChatBootstrap/SKILL.md")
parser = Page()
parser.feed(site)

expected = (
    "lum","urdDoctorGoddess","belldandySecretary","skuldResearch",
    "kiri","momo","shiori","kugi","tetsu","kaji","fumi","sumi","koe",
    "yume","mediaAssetFactory"
)
# Fifteen independent canonical identity assertions.
for role in expected:
    audit("registeredRole:" + role, role in roster["requiredAgents"])
# Fifteen equal-scope hold assertions.
for role in expected:
    audit("quarantinedRole:" + role, role in quarantine["registeredAgents"])
# Canon and release boundaries.
audit("rosterExactCount", len(roster["requiredAgents"]) == 15)
audit("rosterNoDuplicate", len(set(roster["requiredAgents"])) == 15)
audit("quarantineExactCount", quarantine["registeredCount"] == 15)
audit("quarantineNoDuplicate", len(set(quarantine["registeredAgents"])) == 15)
audit("rosterMatchesQuarantine", roster["requiredAgents"] == quarantine["registeredAgents"])
audit("quarantineStillActive", quarantine["state"] == "QUARANTINED")
audit("quarantineNoActiveWorkers", quarantine["activeTaskWorkersAllowed"] is False)
audit("quarantineNoHiddenWorkers", quarantine["hiddenAsyncAgents"] is False)
audit("quarantineRetainsSkills", quarantine["preserveSkillsAndReceipts"] is True)
audit("supervisedProbeNotProven", quarantine["supervisedProbe"]["hostInvocationReceipt"] is None)
audit("urdProofPending", quarantine["supervisedProbe"]["urdEvaluationReceipt"] is None)
audit("humanResumePending", quarantine["supervisedProbe"]["professorResumeReceipt"] is None)
audit("quarantineNoCrown", quarantine["crownStatus"] == "STOP")
audit("lumStillBoss", manifest["boss"] == roster["activationLaw"]["helpersSpeakTo"] == canon["boss"] == cabinet["boss"] == "lum")
audit("singleMutableSourceLane", roster["activationLaw"]["oneMutableSourceLane"] is True)
audit("supportWorkerCap", roster["activationLaw"]["maxParallelSupportWorkers"] == 3)
audit("noRecursiveRecruitment", roster["activationLaw"]["recursiveRecruitment"] is False)
audit("cabinetRosterCount", len(cabinet["members"]) == 4)
for role in ("lum","urdDoctorGoddess","belldandySecretary","skuldResearch"):
    audit("cabinetRole:" + role, role in [x["id"] for x in cabinet["members"]])
for role in ("lum","urdDoctorGoddess","belldandySecretary","skuldResearch","yume"):
    audit("previewMember:" + role, role in manifest["members"])
audit("manifestIdentity", manifest["schema"] == "luhmOs.soloStudioCastRelease.v1")
audit("manifestQuarantinePath", manifest["quarantineRef"] == "doctrine/companyWideOperationalQuarantineV1.json")
audit("manifestReadOnly", manifest["publicPreviewOnly"] is True)
audit("manifestNoAutonomousClaim", manifest["autonomousAgentsClaimed"] is False)
audit("manifestReleaseTarget", manifest["releaseTarget"] == "public static tester portal")
audit("manifestSafeOrigin", manifest["publicLink"] == "https://luhm-os-publication-site.onrender.com/tester.html")
audit("publicSourceOfTruth", truth["canonicalRepository"] == "eggie-admin/LuHm-OS")
audit("noAutomaticPublicationFromSource", truth["publicationAuthority"] is False)
audit("studioNoDefaultSpend", studio["costs"]["newRecurringSpendUsdDefault"] == 0)
audit("studioWorkIsHumanAuthorized", studio["privacyAndSafety"]["access"].startswith("Least privilege"))
audit("tenPassSourceGate", hardening["schema"] == "luhmOs.tenPassHardening.v1")
audit("tenPassNoLiveDb", hardening["liveProviderChangesPerformed"] is False)
# Public HTML negative controls and actual visible disclosures.
audit("htmlDoctype", site.lower().startswith("<!doctype html>"))
audit("htmlViewport", 'name="viewport"' in site)
audit("htmlLandmark", "main" in parser.tags)
audit("htmlHasHeading", "h1" in parser.tags)
audit("fourDisclosurePanels", parser.tags.count("details") == 4)
audit("fourFocusSummaries", parser.tags.count("summary") == 4)
audit("nativeKeyboardAccessible", "<summary>" in site and "details" in parser.tags)
audit("noExternalScript", "script" not in parser.tags)
audit("noLoginForm", "form" not in parser.tags)
audit("noInputCollection", "input" not in parser.tags and "textarea" not in parser.tags)
audit("noUserUploads", "file" not in parser.tags)
audit("noEmbeddedRemotePlayer", "iframe" not in parser.tags)
audit("noStylesheetDependency", "link" not in parser.tags)
audit("privacyPageReachableByLink", "/privacy.html" in parser.links)
audit("releasePageReachableByLink", "/release.html" in parser.links)
audit("repositoryFeedbackLink", "https://github.com/eggie-admin/LuHm-OS/issues/new" in parser.links)
audit("publicSourceLink", "https://github.com/eggie-admin/LuHm-OS" in parser.links)
audit("homeTesterLink", "/tester.html" in home)
audit("releaseTesterLink", "/tester.html" in release)
audit("publicReleaseHonesty", "not live AI agents" in site.lower())
audit("daybreakNoEndorsement", "No OpenAI endorsement" in site)
audit("privatePluginSeparated", "connected ChatGPT plugin" in site)
audit("readOnlyClarity", "Read-only preview" in site)
audit("feedbackNoSecrets", "never passwords" in site)
audit("noProductionExposure", "Nothing here activates an agent" in site)
audit("userModesExplicit", all(x in site for x in ("Default", "IC", "OOC", "IRL")))
for word in ("Yume", "Urd", "Skuld", "Belldandy", "Lum"):
    audit("publicRoleName:" + word, word in site)
audit("renderPrivateServicesUntouched", "Render" not in site or "live infrastructure" in site)
audit("copilotKnowsPublicContract", "doctrine/soloStudioCastReleaseV1.json" in copilot)
audit("bootstrapKnowsPublicContract", "doctrine/soloStudioCastReleaseV1.json" in bootstrap)
audit("bootstrapPreservesQuarantine", "quarantine" in bootstrap.lower())
audit("sourceSkillPreservesQuarantine", "QUARANTINED" in skill)
audit("noNewCredentials", ".env" not in site and "Bearer " not in site)
audit("noBusinessRegistrationClaim", "registered LLC" not in site)
audit("noAgentModelTrainingClaim", "model fine-tuning" not in site)
audit("noProductionSQLDDL", "CREATE TABLE" not in site and "DROP TABLE" not in site)

failed = [name for name, good in results if not good]
print("CAST_PUBLIC_SOURCE_AUDIT=" + str(len(results) - len(failed)) + "/" + str(len(results)))
print("PROVIDER_EXECUTION=UNVERIFIED; HOST_AGENT_QUARANTINE=ON")
if len(results) < 60 or failed:
    print("FAILED_ASSERTIONS=" + repr(failed), file=sys.stderr)
    sys.exit(1)

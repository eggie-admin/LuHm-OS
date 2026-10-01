#!/usr/bin/env python3
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "doctrine" / "DOCTOR_ONI_MILESTONE_GUARD_V3.json"
SKILL = ROOT / "agents" / "doctorOni" / "SKILL.md"

errors = []
warnings = []


def fail(message):
    errors.append(message)


def warn(message):
    warnings.append(message)


def require(condition, message):
    if not condition:
        fail(message)


try:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
except Exception as exc:
    print(f"DOCTOR_ONI_TRUTH_GUARD=RED\ncontract parse failure: {exc}")
    sys.exit(2)

skill = SKILL.read_text(encoding="utf-8") if SKILL.exists() else ""

require(contract.get("status") == "PROPOSED_CANDIDATE", "candidate contract must remain PROPOSED_CANDIDATE")
require(contract.get("crownStatus") == "STOP", "CROWN must remain STOP")
require(contract.get("authority") == "Professor", "Professor must remain authority")
require(contract.get("primaryRole") == "OpenAI/Lum anti-hallucination truth guard", "Doctor primary role drifted")
require(contract.get("secondaryRole") == "milestone and automation drift guard", "Doctor secondary role drifted")
require(contract.get("truthLaw") == "No evidence -> no factual claim. Unknown stays UNKNOWN.", "truth law drifted")

classes = set(contract.get("claimClasses", []))
required_classes = {"PROVEN", "SOURCE_DERIVED", "OBSERVED", "INFERENCE", "PROPOSAL", "MEMORY_ONLY", "UNKNOWN", "CONTRADICTED"}
require(classes == required_classes, "claim classification vocabulary drift")

truth = contract.get("truthFirewall", {})
for key in ("materialClaimsRequireEvidence", "contradictionsMustBeReported"):
    require(truth.get(key) is True, f"truth firewall requires {key}=true")
for key in (
    "memoryIsMutableStateProof",
    "plausibilityIsProof",
    "confidenceIsProof",
    "toneIsProof",
    "silentGapFilling",
    "candidateMayBeCalledCurrent",
    "ciMayImplyDeviceRuntimeRelease",
    "inferIntentToLie",
):
    require(truth.get(key) is False, f"truth firewall requires {key}=false")
require(truth.get("unsupportedClaimVerdict") == "UNKNOWN_DOCTOR_ONI_UNSUPPORTED_CLAIM", "unsupported claim verdict drift")
require(truth.get("falseStateClaimVerdict") == "RED_DOCTOR_ONI_FALSE_STATE_CLAIM", "false-state claim verdict drift")

claim_receipt = set(contract.get("requiredClaimReceipt", []))
for field in ("claimId", "claimText", "claimClass", "sourceRef", "evidenceRefs", "scope", "limits", "verdict"):
    require(field in claim_receipt, f"claim receipt missing {field}")

milestone = contract.get("activeMilestone", {})
for field in ("id", "status", "sourceRef", "objective", "nextGate", "completionRequires"):
    require(bool(milestone.get(field)), f"activeMilestone missing {field}")
require(milestone.get("status", "").startswith("AMBER_"), "candidate active milestone must remain AMBER until promoted")

relations = set(contract.get("milestoneRelations", []))
require(relations == {"DIRECT", "SUPPORT", "BLOCKER", "EXEMPT"}, "milestone relation vocabulary drift")

packet = set(contract.get("requiredMilestonePacket", []))
for field in (
    "milestoneId", "milestoneSourceRef", "taskId", "sourceRef", "relation",
    "expectedDelta", "nextGate", "allowedScope", "mutationBudget",
    "evidenceRequired", "stopConditions"
):
    require(field in packet, f"milestone packet missing {field}")

receipt = set(contract.get("requiredAutomationReceipt", []))
for field in (
    "milestoneId", "taskId", "automationId", "trigger", "sourceBefore",
    "sourceAfter", "relation", "expectedDelta", "observedDelta", "evidenceRefs",
    "gatesClosed", "gatesOpened", "nextGate", "status", "authorityUsed",
    "mutationCount", "retryCount"
):
    require(field in receipt, f"automation receipt missing {field}")

gov = contract.get("automationGovernance", {})
require(gov.get("newOrChangedAutomationRequiresMilestonePacket") is True, "new/changed automation must require milestone packet")
require(gov.get("recursiveTaskSpawning") is False, "recursive task spawning must be false")
require(gov.get("selfPromotion") is False, "self promotion must be false")
require(gov.get("selfCrown") is False, "self Crown must be false")
require(gov.get("unboundedRetries") is False, "unbounded retries must be false")
require(gov.get("mutationAfterExpectedDeltaAchieved") is False, "automation must stop after expected delta")
require(gov.get("defaultForUnclassifiedAutomation") == "UNKNOWN_AUTOMATION_UNACCOUNTED", "unclassified automation must fail closed")

for phrase in (
    "OpenAI / Lum truth firewall",
    "Anti-vibes rule",
    "Claim receipt",
    "Memory firewall",
    "Source precedence",
    "No evidence -> no factual claim. Unknown stays UNKNOWN.",
    "UNKNOWN_DOCTOR_ONI_UNSUPPORTED_CLAIM",
    "RED_DOCTOR_ONI_FALSE_STATE_CLAIM",
    "Active-milestone lock",
    "Side-quest firewall",
    "Automation receipt contract",
    "Witching Hour handoff",
):
    require(phrase in skill, f"Doctor skill missing required truth/milestone phrase: {phrase}")

for forbidden_power in (
    "modifying source herself",
    "merging or rebasing",
    "publishing or deploying",
    "self-Crown",
    "treating memory, confidence, or plausibility as proof",
):
    require(forbidden_power in skill, f"Doctor authority/truth boundary missing: {forbidden_power}")

require("Dependency drift" in skill, "Doctor v3 must contain dependency-drift handling")
require("dangling dependency" in skill, "Doctor v3 must not pretend missing dependencies exist")
require("TRUTH_CHECK" in contract.get("witchingHourSequence", []), "Witching Hour must contain TRUTH_CHECK")

workflow = ROOT / ".github" / "workflows" / "doctor-oni-milestone-guard.yml"
if workflow.exists():
    text = workflow.read_text(encoding="utf-8")
    require("Doctor Oni Truth + Milestone Guard" in text, "truth guard workflow name missing")
    require("doctorOniMilestoneGuardAudit.py" in text, "guard workflow does not invoke auditor")
else:
    warn("guard workflow not present yet")

status = "GREEN" if not errors else "RED"
print(f"DOCTOR_ONI_TRUTH_GUARD={status}")
print(f"errors={len(errors)} warnings={len(warnings)}")
for item in errors:
    print("ERROR:", item)
for item in warnings:
    print("WARN:", item)
print("NOTE: GREEN proves only the candidate truth/milestone guard contract and static audit. It does not make any unverified LuHm claim true and is not deployment, publication, device, enterprise, or Crown GREEN.")
sys.exit(0 if not errors else 2)

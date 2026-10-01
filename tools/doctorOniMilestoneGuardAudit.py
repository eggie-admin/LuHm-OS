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
    print(f"DOCTOR_ONI_MILESTONE_GUARD=RED\ncontract parse failure: {exc}")
    sys.exit(2)

skill = SKILL.read_text(encoding="utf-8") if SKILL.exists() else ""

require(contract.get("status") == "PROPOSED_CANDIDATE", "candidate contract must remain PROPOSED_CANDIDATE")
require(contract.get("crownStatus") == "STOP", "CROWN must remain STOP")
require(contract.get("authority") == "Professor", "Professor must remain authority")

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
    "Active-milestone lock",
    "Side-quest firewall",
    "Automation receipt contract",
    "Milestone progress rule",
    "Witching Hour handoff",
    "UNKNOWN_AUTOMATION_UNACCOUNTED",
    "AMBER_DOCTOR_ONI_SIDE_QUEST_DRIFT",
    "RED_DOCTOR_ONI_MILESTONE_BREACH",
):
    require(phrase in skill, f"Doctor skill missing required milestone guard phrase: {phrase}")

for forbidden_power in (
    "modifying source herself",
    "merging or rebasing",
    "publishing or deploying",
    "self-Crown",
):
    require(forbidden_power in skill, f"Doctor authority boundary missing: {forbidden_power}")

# Current main has a known dangling ONI_PROTOCOL_V2 reference in v2. v3 must be self-contained
# and must explicitly fail closed if a protocol dependency is absent.
require("Dependency drift" in skill, "Doctor v3 must contain dependency-drift handling")
require("dangling dependency" in skill, "Doctor v3 must not pretend missing dependencies exist")

# Any workflow added with this candidate must itself be milestone-governed by name.
workflow = ROOT / ".github" / "workflows" / "doctor-oni-milestone-guard.yml"
if workflow.exists():
    text = workflow.read_text(encoding="utf-8")
    require("Doctor Oni Milestone Guard" in text, "guard workflow name missing")
    require("doctorOniMilestoneGuardAudit.py" in text, "guard workflow does not invoke auditor")
else:
    warn("guard workflow not present yet")

status = "GREEN" if not errors else "RED"
print(f"DOCTOR_ONI_MILESTONE_GUARD={status}")
print(f"errors={len(errors)} warnings={len(warnings)}")
for item in errors:
    print("ERROR:", item)
for item in warnings:
    print("WARN:", item)
print("NOTE: GREEN proves only the candidate milestone-guard contract/static audit. It is not milestone completion, deployment, publication, device, enterprise, or Crown GREEN.")
sys.exit(0 if not errors else 2)

"""Milestone task continuity negative controls, no tool access or secrets required."""
from __future__ import annotations
import copy
import json
import unittest
from pathlib import Path
from tools.milestoneTaskQueue import validate, evaluate

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "b" * 40


class MilestoneTaskQueueTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.queue = json.loads((ROOT / "doctrine/milestoneTaskQueueV1.json").read_text())

    def test_current_canon_schema(self):
        validate(self.queue)
        self.assertEqual(len(self.queue["tasks"]), 8)
        self.assertFalse(self.queue["security"]["runtimeWorkerActivationAllowed"])
        self.assertEqual(self.queue["scheduler"]["runnerCount"], 1)

    def test_unknown_never_silently_green(self):
        result = evaluate(self.queue, {}, SOURCE)
        self.assertEqual(result["status"], "CONTINUE")
        self.assertEqual(result["nextExecutable"], "mobileMainHost")
        self.assertEqual(result["completedTasks"], [])
        self.assertFalse(result["executionAuthorizedByThisPlan"])
        self.assertFalse(result["humanProductCrownGranted"])

    def test_proof_must_have_same_source_and_evidence(self):
        for obs in (
            {"state": "PROVEN", "sourceRef": SOURCE, "checkedAt": "2026-10-24"},
            {"state": "PROVEN", "sourceRef": "c" * 40, "checkedAt": "2026-10-24", "evidenceRefs": ["render:real"]},
            {"state": "PROVEN", "sourceRef": SOURCE, "evidenceRefs": ["render:real"]}
        ):
            with self.assertRaisesRegex(ValueError, "UNPROVEN_MILESTONE"):
                evaluate(self.queue, {"mobileMainHost": obs}, SOURCE)

    def test_verified_dependency_unblocks_device_check_only(self):
        obs = {"mobileMainHost": {
            "state": "PROVEN", "sourceRef": SOURCE,
            "checkedAt": "2026-10-24T20:00:00-04:00",
            "evidenceRefs": ["github:source", "render:deploy", "host:mcp"]
        }}
        r = evaluate(self.queue, obs, SOURCE)
        self.assertEqual(r["tasks"][0]["state"], "DONE")
        self.assertIn("androidCockpitProof", r["remainingExecutable"])
        self.assertNotIn("samsungBetaDelivery", r["remainingExecutable"])

    def test_hard_red_blocks_only_one_lane(self):
        obs = {"samsungCanonSigning": {
            "state": "HARD_RED",
            "reason": "SECRET_OR_OWNER_PROTECTED_SETTING",
            "evidenceRefs": ["github:issue388-owner-settings-unavailable"],
            "sourceRef": SOURCE, "checkedAt": "2026-10-24"
        }}
        r = evaluate(self.queue, obs, SOURCE)
        self.assertIn("samsungCanonSigning", r["hardRedTasks"])
        self.assertEqual(r["status"], "CONTINUE")
        self.assertEqual(r["nextExecutable"], "mobileMainHost")
        self.assertNotIn("samsungBetaDelivery", r["remainingExecutable"])

    def test_hard_red_requires_allowed_code_and_evidence(self):
        with self.assertRaisesRegex(ValueError, "HARD_RED_NEEDS_CAUSE"):
            evaluate(self.queue, {"chatGptInlineMount": {
                "state": "HARD_RED", "reason": "IT_LOOKS_BAD", "evidenceRefs": []
            }}, SOURCE)

    def test_phone_cannot_be_proven_from_web_check(self):
        obs = {
            "mobileMainHost": {
                "state": "PROVEN", "sourceRef": SOURCE, "checkedAt": "2026-10-24",
                "evidenceRefs": ["render:verified-live"]
            },
            "androidCockpitProof": {
                "state": "PROVEN", "sourceRef": SOURCE, "checkedAt": "2026-10-24",
                "evidenceRefs": ["ci:headlessChromium"]
            }
        }
        with self.assertRaisesRegex(ValueError, "OWNER_RECEIPT_REQUIRED"):
            evaluate(self.queue, obs, SOURCE)

    def test_dependency_proof_required(self):
        obs = {"samsungBetaDelivery": {
            "state": "PROVEN", "sourceRef": SOURCE,
            "checkedAt": "2026-10-24",
            "ownerReceipt": True, "evidenceRefs": ["device:receipt"]
        }}
        with self.assertRaisesRegex(ValueError, "DEPENDENCY_NOT_PROVEN"):
            evaluate(self.queue, obs, SOURCE)

    def test_no_dependency_cycles_or_unknown_deps(self):
        a = copy.deepcopy(self.queue)
        a["tasks"][0]["dependsOn"] = ["finalProductCrown"]
        with self.assertRaisesRegex(ValueError, "CYCLIC_MILESTONES"):
            validate(a)
        b = copy.deepcopy(self.queue)
        b["tasks"][0]["dependsOn"] = ["ghostTask"]
        with self.assertRaisesRegex(ValueError, "BAD_DEPENDENCY"):
            validate(b)

    def test_no_duplicate_tasks_or_multiple_runners(self):
        a = copy.deepcopy(self.queue)
        a["tasks"].append(copy.deepcopy(a["tasks"][0]))
        with self.assertRaisesRegex(ValueError, "INVALID_TASK_IDS"):
            validate(a)
        b = copy.deepcopy(self.queue)
        b["scheduler"]["runnerCount"] = 2
        with self.assertRaisesRegex(ValueError, "MULTIPLE_SCHEDULED_RUNNERS"):
            validate(b)

    def test_no_safety_fence_drift(self):
        a = copy.deepcopy(self.queue)
        a["taskLaw"]["forbidden"].remove("PUBLISH_PRIVATE_MEDIA")
        with self.assertRaisesRegex(ValueError, "MISSING_SAFETY_FENCES"):
            validate(a)
        b = copy.deepcopy(self.queue)
        b["security"]["runtimeWorkerActivationAllowed"] = True
        with self.assertRaisesRegex(ValueError, "AGENT_QUARANTINE_BYPASS"):
            validate(b)

    def test_bounded_attempts_and_single_mutation(self):
        a = copy.deepcopy(self.queue)
        a["taskLaw"]["boundedAttemptsPerTick"] = 200
        with self.assertRaisesRegex(ValueError, "UNBOUNDED_TICK"):
            validate(a)
        b = copy.deepcopy(self.queue)
        b["taskLaw"]["onlyOneMutationLane"] = False
        with self.assertRaisesRegex(ValueError, "GLOBAL_STOP_OR_RACE"):
            validate(b)


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Source-only CAST Bridge two-thread/4-tier/four-typed-SQL-lane tests."""
from __future__ import annotations

import copy
import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "host" / "api"))
spec = importlib.util.spec_from_file_location(
    "luhmCastTwoThreadBridge", ROOT / "host/api/luhmCastTwoThreadBridge.py")
assert spec and spec.loader
cast = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cast)
SHA = "f0cb6ee54066b490c0e80efc2c96200fec76ee2d"
PRIVATE_GOAL = "Private demo with original studio material. Do not log this."
TASK = {"task_id": "castTask", "source_ref": SHA,
        "scope_id": "personalStudio", "goal": PRIVATE_GOAL}


class TestCastTwoThread(unittest.TestCase):
    def test_source_contract_four_tiers_lanes_two_threads(self):
        s = cast.source_audit()
        self.assertEqual(s["status"], "SOURCE_CONSISTENT_ONLY", s["issues"])
        self.assertEqual(s["threadCount"], 2)
        self.assertEqual(s["dataLaneCount"], 4)
        self.assertEqual(s["escalationTierCount"], 4)
        self.assertEqual(s["matrixCells"], 16)
        self.assertEqual(s["activeAgentThreads"], 0)
        self.assertFalse(s["chatGptSecondConversationCreated"])

    def test_one_task_two_separate_timelines_and_goal_never_transmitted(self):
        r = cast.plan(**TASK)
        self.assertEqual(r["state"], "HOLD_EXTERNAL_CI_HOST_AND_OWNER_RECEIPTS")
        self.assertEqual([t["threadId"] for t in r["threads"]],
                         ["professorLum", "lumMesh"])
        self.assertEqual([l["id"] for l in r["typedLanes"]],
                         list(cast.LANES))
        self.assertEqual(len(r["matrix4x4"]), 4)
        self.assertEqual(sum(len(row["lanes"]) for row in r["matrix4x4"]), 16)
        self.assertEqual([x["stage"] for x in r["canon"]], list(cast.STAGES))
        self.assertEqual(r["typedLanes"][2]["sourceVerified"], None)
        self.assertFalse(r["sourceCommitVerifiedAgainstGitHub"])
        self.assertFalse(r["appSecondThreadCreated"])
        self.assertEqual(r["actualMeshAgentsStarted"], 0)
        self.assertEqual(r["networkCalls"], 0)
        self.assertEqual(r["databaseWrites"], 0)
        self.assertFalse(r["greenAuthority"])
        import json
        self.assertNotIn(PRIVATE_GOAL, json.dumps(r))

    def test_all_tiers_and_later_stage_never_claim_execution(self):
        for tier in range(4):
            with self.subTest(tier=tier):
                r = cast.plan(**TASK, tier=tier, requested_stage="deploy")
                self.assertEqual(r["tier"], tier)
                self.assertEqual(r["requestedStage"], "deploy")
                self.assertEqual(r["typedLanes"][0]["stageOrdinal"], 7)
                self.assertEqual(r["bridgeSmokeState"], "NOT_RUN")
                self.assertFalse(r["productionDeployment"])
                self.assertFalse(r["greenAuthority"])

    def test_same_exact_goal_input_replays_deterministic_plan(self):
        a, b = cast.plan(**TASK), cast.plan(**TASK)
        self.assertEqual(a["requestSha256"], b["requestSha256"])
        self.assertEqual(a, b)

    def test_valid_early_receipt_claims_are_explicitly_untrusted(self):
        receipts = [
            {"taskId": "castTask", "sourceRef": SHA,
             "scopeId": "personalStudio", "stage": x,
             "evidenceSha256": ("a" if i == 0 else "b") * 64}
            for i, x in enumerate(("sanityCheck", "audit"))
        ]
        r = cast.plan(**TASK, requested_stage="mutation",
                      evidence_claims=receipts)
        self.assertEqual(r["evidenceReview"]["claimsSubmitted"], 2)
        self.assertFalse(r["evidenceReview"]["proofOriginTrusted"])
        self.assertEqual(r["evidenceReview"]["latestClaimedStage"], "audit")
        self.assertFalse(r["threads"][1]["messages"][1]["proofOriginTrusted"])
        self.assertFalse(r["greenAuthority"])

    def test_wrong_source_skip_duplicate_stage_and_forged_evidence_rejected(self):
        base = {"taskId": "castTask", "sourceRef": SHA,
                "scopeId": "personalStudio", "stage": "sanityCheck",
                "evidenceSha256": "e" * 64}
        for claims in (
            [{**base, "sourceRef": "f" * 40}],
            [{**base, "scopeId": "otherScope"}],
            [{**base, "stage": "mutation"}],
            [base, base],
            [{**base, "evidenceSha256": "NOT_A_SHA"}],
            [{**base, "shell": "true"}],
            [{**base, "stage": "CASTED"}],
        ):
            with self.subTest(claims=claims), self.assertRaises(ValueError):
                cast.plan(**TASK, evidence_claims=claims)
        with self.assertRaises(ValueError):
            cast.plan(**TASK, evidence_claims=[base] * 9)

    def test_invalid_task_tier_stage_and_goal_denied(self):
        for altered in (
            {"source_ref": "main"}, {"task_id": "../unsafe"},
            {"scope_id": "unsafe scope"}, {"goal": ""},
            {"goal": "x" * 2049}, {"tier": -1},
            {"tier": True}, {"tier": 4}, {"requested_stage": "cast"},
        ):
            with self.subTest(altered=altered), self.assertRaises(ValueError):
                cast.plan(**{**TASK, **altered})

    def test_policy_tampering_blocks_source_projection(self):
        original = cast._load
        def forged(path):
            x = original(path)
            if path == cast.CONTRACT:
                x = copy.deepcopy(x)
                x["runtime"]["activeMiniAgents"] = 2
                x["receiptRules"]["noSkip"] = False
                x["canonicalStates"][2] = "deploy"
            return x
        with patch.object(cast, "_load", side_effect=forged):
            s = cast.source_audit()
            self.assertIn("RED_CAST_FAKE_LIVE_THREAD", s["issues"])
            self.assertIn("RED_CAST_RECEIPT_AUTHORITY", s["issues"])
            self.assertIn("RED_CAST_STATE_MACHINE", s["issues"])
            r = cast.plan(**TASK)
            self.assertEqual(r["status"], "STOP_SOURCE_DRIFT")


if __name__ == "__main__":
    unittest.main()

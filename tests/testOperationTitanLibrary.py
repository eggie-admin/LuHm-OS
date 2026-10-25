#!/usr/bin/env python3
"""Operation Titan is a library method, not an ambient voice/roleplay trigger."""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("luhmOsLibrary", ROOT / "lib/luhmOs.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
LuHmOS = module.LuHmOS
SOURCE_REF = "a" * 40


def invoke(**changes):
    params = {
        "mode": "system", "taskId": "safeBetaReview",
        "sourceRef": SOURCE_REF, "actualSourceRef": SOURCE_REF,
        "scopeId": "candidateOnly", "milestoneId": "titan7Review",
        "tier": 0, "outcome": "working",
    }
    params.update(changes)
    return LuHmOS.fn.operationTitan(**params)


class TitanLibraryTests(unittest.TestCase):
    def test_canonical_class_library_entry(self):
        self.assertTrue(callable(LuHmOS.fn.operationTitan))
        x = invoke()
        self.assertEqual(x["functionRef"], "LuHmOS.fn.operationTitan")
        self.assertEqual(x["buildVersion"], 7)
        self.assertEqual(x["sourceRef"], SOURCE_REF)
        self.assertFalse(x["mutationExecuted"])
        self.assertFalse(x["testsExecuted"])

    def test_exact_source_ref_is_required(self):
        for bad in ({"sourceRef": "main"}, {"actualSourceRef": "b" * 40}):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                invoke(**bad)

    def test_all_cannot_mutate_or_claim_green(self):
        a = invoke(mode="all", tier=3)
        self.assertTrue(a["requestedMutation"])
        self.assertEqual(a["dispatch"], "STOP_SEPARATE_AUTHORIZED_EXECUTOR")
        self.assertFalse(a["mutationExecuted"])
        self.assertFalse(a["greenClaim"])
        self.assertEqual(a["crownStatus"], "STOP")
        self.assertIn("operationTitan7FinalFormAudit.py", a["testPlan"][0])

    def test_apply_alone_cannot_dispatch(self):
        a = invoke(mode="apply", outcome="green")
        self.assertFalse(a["mutationExecuted"])
        self.assertFalse(a["releaseAuthority"])
        self.assertFalse(a["publicationAuthority"])
        self.assertFalse(a["mergeAuthority"])

    def test_tier_change_cannot_grant_authority(self):
        for tier in range(4):
            for outcome in ("working", "green", "blocked", "unknown", "conflict"):
                with self.subTest(tier=tier, outcome=outcome):
                    a = invoke(tier=tier, outcome=outcome)
                    self.assertEqual(a["sourceRef"], SOURCE_REF)
                    self.assertEqual(a["scopeId"], "candidateOnly")
                    self.assertFalse(a["greenClaim"])
                    self.assertFalse(a["runtimeVerified"])
                    self.assertFalse(a["mutationExecuted"])

    def test_blocked_escalates_only_one_tier(self):
        for tier in range(4):
            self.assertEqual(invoke(tier=tier, outcome="blocked")["nextTier"], min(3, tier + 1))

    def test_unknown_and_conflict_hold(self):
        for outcome in ("unknown", "conflict"):
            self.assertEqual(invoke(tier=2, outcome=outcome)["nextTier"], 2)

    def test_invalid_mode_tier_and_outcome_fail_closed(self):
        for bad in ({"mode": "release"}, {"tier": -1}, {"tier": True},
                    {"tier": 4}, {"outcome": "crowned"}, {"scopeId": ""}):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                invoke(**bad)

    def test_roleplay_does_not_enter_execution(self):
        with self.assertRaises(ValueError):
            invoke(mode="Bless you, my King")


if __name__ == "__main__":
    unittest.main()

"""Unit tests for the source-only Song of the Goddess coordinator."""
import unittest
from tools.songGoddessHarness import Check, four_loop, netplan_like_plan

SHA = "a" * 40
LANES = ("canon", "implementation", "sidecar", "reconciliation")
BEATS = ("inspect", "plan", "test", "verify")

class SongGoddessHarnessTests(unittest.TestCase):
    def test_full_green(self):
        checks = {(lane, beat):
                  (lambda lane=lane, beat=beat:
                   Check(lane, beat, "GREEN", evidence="fixture:" + lane + ":" + beat))
                  for lane in LANES for beat in BEATS}
        result = four_loop(SHA, checks, source_now=lambda: SHA)
        self.assertEqual(result["sourceAuditStatus"], "GREEN")
        self.assertEqual(len(result["checks"]), 16)
        self.assertFalse(result["promotionAuthority"])

    def test_missing_is_null_not_green(self):
        result = four_loop(SHA, {}, source_now=lambda: SHA)
        self.assertEqual(result["counts"]["NULL"], 4)
        self.assertEqual(result["sourceAuditStatus"], "AMBER")

    def test_failure_isolated_by_lane(self):
        checks = {("canon", "inspect"):
                  lambda: Check("canon", "inspect", "RED", reason="fixture")}
        result = four_loop(SHA, checks, source_now=lambda: SHA)
        self.assertEqual(result["counts"]["RED"], 1)
        self.assertEqual(result["counts"]["NULL"], 3)

    def test_source_drift_holds(self):
        result = four_loop(SHA, {}, source_now=lambda: "b" * 40)
        self.assertFalse(result["sourceStable"])
        self.assertEqual(result["sourceAuditStatus"], "AMBER")

    def test_green_requires_evidence(self):
        with self.assertRaises(ValueError):
            Check("canon", "inspect", "GREEN")

    def test_bounded_budget(self):
        with self.assertRaises(ValueError):
            four_loop(SHA, {}, source_now=lambda: SHA, max_checks=17)

    def test_netplan_style_is_plan_only(self):
        result = netplan_like_plan({"dns": "old"}, {"dns": "new"})
        self.assertEqual(len(result["changes"]), 1)
        self.assertFalse(result["applyExecuted"])

if __name__ == "__main__":
    unittest.main()

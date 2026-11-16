#!/usr/bin/env python3
"""No-network, no-device tests of the 4x4 escalation candidate."""
import json
import unittest
from tools.escalationFourByFourPolish import evaluate, load_policy

SHA = "a" * 40

def measure(tier=0, beat="verify", outcome="working", receipts=None, blocker=""):
    return {"taskId":"privateBetaPolish","sourceRef":SHA,"scopeId":"samsungBeta",
            "domain":"technology","tier":tier,"beat":beat,"outcome":outcome,
            "evidenceRefs": [] if receipts is None else receipts,"blocker":blocker}

class FourByFourPolishTests(unittest.TestCase):
    def test_exact_sixteen_cells(self):
        policy=load_policy()
        self.assertEqual(len(policy["cells"]),16)
        self.assertEqual([x["beat"] for x in policy["cells"][:4]],
                         ["hear","resolve","act","verify"])
    def test_beats_have_no_execution_authority(self):
        for beat in ("hear","resolve","act"):
            decision=evaluate(measure(beat=beat))
            self.assertEqual(decision["decision"],"NEXT_BEAT")
            self.assertFalse(decision["mayAutoExecute"])
            self.assertEqual(decision["crownStatus"],"STOP")
    def test_unsupported_early_green_rejected(self):
        with self.assertRaisesRegex(ValueError,"ONLY_VERIFY_DECIDES"):
            evaluate(measure(beat="act",outcome="green",receipts=["CI:1234"]))
    def test_blocked_requires_evidence_and_specific_blocker(self):
        self.assertEqual(evaluate(measure(outcome="blocked"))["decision"],
                         "HOLD_UNPROVEN_BLOCKED")
        self.assertEqual(evaluate(measure(outcome="blocked",receipts=["CI:1234"]))["decision"],
                         "HOLD_UNPROVEN_BLOCKED")
        result=evaluate(measure(outcome="blocked",receipts=["CI:1234"],blocker="owner signer missing"))
        self.assertEqual(result["decision"],"ESCALATE_ONE_TIER")
        self.assertEqual(result["nextTier"],1)
    def test_escalation_never_exceeds_tier_three(self):
        for tier in range(4):
            result=evaluate(measure(tier=tier,outcome="blocked",receipts=["CI:1234"],blocker="same gate red"))
            self.assertEqual(result["nextTier"],min(3,tier+1))
        self.assertEqual(result["decision"],"HOLD_TIER_3_BLOCKER")
    def test_green_deescalates_but_does_not_crown(self):
        for tier in range(4):
            result=evaluate(measure(tier=tier,outcome="green",receipts=["CI:1234"]))
            self.assertEqual(result["nextTier"],max(0,tier-1))
            self.assertFalse(result["maySign"])
            self.assertFalse(result["physicalDeviceProof"])
            self.assertEqual(result["evidenceAttestation"],"UNVERIFIED_INPUT_NOT_INDEPENDENT_PROOF")
        self.assertEqual(evaluate(measure(outcome="green"))["decision"],"HOLD_UNPROVEN_GREEN")
    def test_unknown_conflict_red_fail_closed(self):
        for outcome,decision in (("unknown","HOLD_UNKNOWN"),("conflict","HOLD_CONFLICT"),("red","STOP_RED")):
            self.assertEqual(evaluate(measure(outcome=outcome))["decision"],decision)
    def test_identity_drift_requires_restart(self):
        prev={"taskId":"privateBetaPolish","sourceRef":"b"*40,"scopeId":"samsungBeta"}
        self.assertEqual(evaluate(measure(outcome="green",receipts=["CI:1234"]),prev)["decision"],
                         "HOLD_IDENTITY_DRIFT")
    def test_bad_inputs_rejected(self):
        for change in ({"sourceRef":"main"},{"tier":True},{"evidenceRefs":["x"]},{"domain":"releaseCrown"},{"beat":"publish"}):
            candidate=measure()
            candidate.update(change)
            with self.assertRaises(ValueError):
                evaluate(candidate)

if __name__=="__main__":
    unittest.main()

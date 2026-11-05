"""Release-lane policy tests; no builds or promotion."""
import unittest
from tools.castLaneMap import plan_transition, release_map
SHA = "a" * 40

class CastLaneMapTests(unittest.TestCase):
    def test_controllers(self):
        lanes = release_map()["lanes"]
        self.assertEqual([x["controller"] for x in lanes],
                         ["castBridge", "castBridge", "cast", "cast"])
        self.assertEqual([x["hex"] for x in lanes],
                         ["0x00", "0x01", "0x02", "0x03"])

    def test_no_skip(self):
        self.assertEqual(plan_transition("testing", "beta", {}, source_ref=SHA)["status"],
                         "BLOCKED")

    def test_missing_evidence_is_amber(self):
        self.assertEqual(plan_transition("testing", "proposed", {}, source_ref=SHA)["status"],
                         "AMBER")

    def test_proposed_ready_does_not_execute(self):
        evidence = {"sourceRef": SHA, "candidateBuildOrRun": True,
                    "failureOrSmokeReceipt": True}
        result = plan_transition("testing", "proposed", evidence, source_ref=SHA)
        self.assertEqual(result["status"], "READY_FOR_REVIEW")
        self.assertFalse(result["authorized"])

    def test_beta_requires_professor_gate(self):
        evidence = {key: True for key in release_map()["lanes"][2]["requiredEvidence"]}
        evidence["sourceRef"] = SHA
        result = plan_transition("proposed", "beta", evidence, source_ref=SHA)
        self.assertEqual(result["reason"], "PROFESSOR_GATE")

    def test_lts_is_not_falsely_implemented(self):
        self.assertFalse(release_map()["lts"]["separateLtsGateImplemented"])

if __name__ == "__main__":
    unittest.main()

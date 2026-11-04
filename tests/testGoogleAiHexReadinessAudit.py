"""Negative controls for read-only Google AI 0x00..0x0F source gate."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.googleAiHexReadinessAudit import build_receipt, load_docs

SHA = "a" * 40


class GoogleAiHexReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docs = load_docs()

    def receipt(self, mutate=None, actual=SHA):
        docs = copy.deepcopy(self.docs)
        if mutate:
            mutate(docs)
        return build_receipt(docs, SHA, actual)

    def test_all_sixteen_cells_are_amber_not_green(self):
        r = self.receipt()
        self.assertEqual(r["status"], "AMBER_PROVIDER_PROOF_REQUIRED")
        self.assertEqual((r["checkedCells"], r["passedCells"]), (16, 16))
        self.assertFalse(r["providerApiInvoked"])
        self.assertFalse(r["canSpend"] or r["canMerge"] or r["canDeploy"])

    def test_exact_source_drift_fails(self):
        self.assertEqual(self.receipt(actual="b" * 40)["status"], "RED_SOURCE_POLICY")

    def test_matrix_relabel_cannot_bypass(self):
        r = self.receipt(lambda d: d["hex"]["cells"][0].update(operation="skip"))
        self.assertEqual(r["status"], "RED_SOURCE_POLICY")

    def test_provider_api_false_green_fails(self):
        r = self.receipt(lambda d: d["ent"]["entitlementAxes"]["developerApi"].update(
            apiEnabledState="VERIFIED"))
        self.assertEqual(r["status"], "RED_SOURCE_POLICY")

    def test_billing_or_spend_escalation_fails(self):
        r = self.receipt(lambda d: d["ent"]["entitlementAxes"]["cloudBilling"].update(
            paidCallsAllowed=True))
        self.assertEqual(r["status"], "RED_SOURCE_POLICY")

    def test_network_egress_activation_fails(self):
        r = self.receipt(lambda d: d["proxy"].update(networkEgress="ENABLED"))
        self.assertEqual(r["status"], "RED_SOURCE_POLICY")

    def test_agent_quarantine_override_fails(self):
        r = self.receipt(lambda d: d["hold"].update(activeTaskWorkersAllowed=True))
        self.assertEqual(r["status"], "RED_SOURCE_POLICY")

    def test_unsafe_oidc_on_pull_request_fails(self):
        r = self.receipt(lambda d: d["orchestra"]["github"].update(oidcEnabledByThisWorkflow=True))
        self.assertEqual(r["status"], "RED_SOURCE_POLICY")

    def test_merge_authority_escalation_fails(self):
        r = self.receipt(lambda d: d["hex"]["guarantees"].update(mainMerge=True))
        self.assertEqual(r["status"], "RED_SOURCE_POLICY")


if __name__ == "__main__":
    unittest.main()

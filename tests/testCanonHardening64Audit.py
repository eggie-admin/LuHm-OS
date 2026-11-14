"""Fail-closed testing for LuHm-OS Canon 64 source-only matrix."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.canonHardening64Audit import read_sources, receipt

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = __import__("json").loads((ROOT / "doctrine/canonHardening64V1.json").read_text())
DOCS, DIGESTS = read_sources()
SHA = "a" * 40


class Canon64Tests(unittest.TestCase):
    def run_gate(self, change=None, real_sha=SHA, prior=None):
        m, d = copy.deepcopy(MANIFEST), copy.deepcopy(DOCS)
        if change:
            change(m, d)
        return receipt(m, d, DIGESTS, SHA, real_sha, prior)

    def test_64_exact_amber_source_checks(self):
        r = self.run_gate()
        self.assertEqual((r["checked"], r["passed"], r["failed"]), (64, 64, 0))
        self.assertEqual(r["overallVerdict"], "AMBER_EXTERNAL_PROOF_REQUIRED")
        self.assertEqual(len(r["lanes"]), 16)
        self.assertFalse(r["googleAiExecution"] or r["deployment"] or r["agentActivation"])

    def test_source_sha_drift_rejected(self):
        with self.assertRaises(ValueError):
            self.run_gate(real_sha="b" * 40)

    def test_duplicate_hex_cell_rejected(self):
        with self.assertRaises(ValueError):
            self.run_gate(lambda m, d: m["matrix"][1].update(cell="0x00"))

    def test_manifest_authority_grant_rejected(self):
        with self.assertRaises(ValueError):
            self.run_gate(lambda m, d: m["gates"].update(mainMerge=True))

    def test_unknown_operator_rejected(self):
        with self.assertRaises(ValueError):
            self.run_gate(lambda m, d: m["matrix"][0].update(operator="exec"))

    def test_unknown_json_selector_fails_one_cell(self):
        r = self.run_gate(lambda m, d: m["matrix"][2].update(jsonPath="noSuchField"))
        self.assertEqual((r["passed"], r["failed"]), (63, 1))
        self.assertEqual(r["sourceStatus"], "RED_SOURCE_CHECKS")

    def test_quarantine_authority_cannot_be_modified_for_green(self):
        def change(m, d):
            d["doctrine/companyWideOperationalQuarantineV1.json"]["activeTaskWorkersAllowed"] = True
        with self.assertRaises(ValueError):
            self.run_gate(change)

    def test_false_google_billing_not_green(self):
        def change(m, d):
            d["doctrine/googleAiDeveloperEntitlementsV1.json"]["entitlementAxes"]["cloudBilling"]["paidCallsAllowed"] = True
        with self.assertRaises(ValueError):
            self.run_gate(change)

    def test_false_crown_not_green(self):
        def change(m, d):
            d["doctrine/currentSourceTruthV3.json"]["crownStatus"] = "GREEN"
        with self.assertRaises(ValueError):
            self.run_gate(change)

    def test_escalation_one_tier_per_failed_same_sha(self):
        def change(m, d):
            d["doctrine/projectChatCanonV1.json"]["boss"] = "other"
        first = self.run_gate(change)
        self.assertEqual(first["lanes"][1]["tier"], 1)
        self.assertEqual(first["lanes"][1]["retries"], 1)
        second = self.run_gate(change, prior=first)
        self.assertEqual(second["lanes"][1]["tier"], 2)
        third = self.run_gate(change, prior=second)
        self.assertEqual(third["lanes"][1]["tier"], 3)
        self.assertEqual(third["lanes"][1]["state"], "HOLD_SPECIALIST")

    def test_stale_previous_sha_is_not_proof(self):
        def change(m, d):
            d["doctrine/projectChatCanonV1.json"]["boss"] = "other"
        prior = self.run_gate(change)
        prior["sourceRef"] = "b" * 40
        next_tick = self.run_gate(change, prior=prior)
        self.assertEqual(next_tick["lanes"][1]["tier"], 1)
        self.assertEqual(next_tick["passed"], 63)

    def test_boolean_int_confusion_is_not_pass(self):
        def change(m, d):
            d["doctrine/cloudflareLumOrchestrationV1.json"]["aiOrchestration"]["activeWorkerCount"] = False
        r = self.run_gate(change)
        self.assertEqual(r["failed"], 1)

    def test_configured_not_equal_live(self):
        r = self.run_gate()
        self.assertEqual(r["crownStatus"], "STOP")
        self.assertFalse(r["liveExternalProof"] or r["physicalDeviceProof"])


if __name__ == "__main__":
    unittest.main()

"""Fail-closed Tier-0 private-art routing tests."""
import copy
import json
import unittest
from pathlib import Path

from tools.yumeFastPath import evaluate, sample_packet

ROOT = Path(__file__).resolve().parents[1]
POLICY = json.loads((ROOT / "doctrine/yumeFastPathCanonV1.json").read_text())


class YumeFastPathTests(unittest.TestCase):
    def packet(self, **overrides):
        packet = sample_packet()
        packet.update(overrides)
        return packet

    def assert_gate(self, field, value):
        result = evaluate(self.packet(**{field: value}), POLICY)
        self.assertEqual(result["status"], "FULL_GATE_REQUIRED", field)
        self.assertIs(result["publicationAuthority"], False)
        self.assertIs(result["changesPerformed"], False)
        self.assertIs(result["quarantineLifted"], False)
        self.assertTrue(result["errors"])

    def test_private_original_uses_fast_path(self):
        result = evaluate(self.packet(), POLICY)
        self.assertEqual(result["status"], "FAST_PATH_ELIGIBLE_PLAN_ONLY")
        self.assertEqual(len(result["steps"]), 4)
        self.assertFalse(result["autonomousWorkerExecution"])

    def test_all_safe_task_types(self):
        for kind in POLICY["eligibleWorkTypes"]:
            with self.subTest(kind=kind):
                self.assertEqual(evaluate(self.packet(workType=kind), POLICY)["status"],
                                 "FAST_PATH_ELIGIBLE_PLAN_ONLY")

    def test_license_verified_for_private_use(self):
        result = evaluate(self.packet(provenanceState="verifiedLicensed",
                                      rightsState="licensedForPrivateUse"), POLICY)
        self.assertEqual(result["status"], "FAST_PATH_ELIGIBLE_PLAN_ONLY")

    def test_unknown_packet_denied(self):
        for packet in ({}, [], None, "concept"):
            with self.subTest(packet=packet):
                self.assertEqual(evaluate(packet, POLICY)["status"], "FULL_GATE_REQUIRED")

    def test_missing_fields_denied(self):
        for key in POLICY["requiredPacketFields"]:
            with self.subTest(key=key):
                packet = self.packet()
                packet.pop(key)
                self.assertEqual(evaluate(packet, POLICY)["status"], "FULL_GATE_REQUIRED")

    def test_source_identity_denied(self):
        self.assert_gate("sourceRef", "G" * 40)
        self.assert_gate("sourceRef", "a" * 39)
        self.assert_gate("taskId", "../secret")

    def test_business_and_public_lane_denied(self):
        self.assert_gate("projectLane", "business")
        self.assert_gate("contentLane", "cathedralPublic")
        self.assert_gate("contentLane", "betaAfterDark")
        self.assert_gate("publicAllowed", True)

    def test_non_boolean_public_allowed_denied(self):
        self.assert_gate("publicAllowed", 0)
        self.assert_gate("publicAllowed", "false")

    def test_unknown_rights_and_provenance_denied(self):
        self.assert_gate("rightsState", "unknown")
        self.assert_gate("rightsState", "")
        self.assert_gate("provenanceState", "pending")

    def test_unprotected_or_irreversible_denied(self):
        for flag in ("sourceProtected", "privateOnly", "reversible", "localOnly"):
            self.assert_gate(flag, False)
            self.assert_gate(flag, "true")

    def test_sensitive_actions_denied(self):
        for flag in ("externalProviderCall", "usesCredentials", "changesProduction",
                     "writesOutsideScratch", "agentExecution"):
            self.assert_gate(flag, True)
            self.assert_gate(flag, None)

    def test_cost_fail_closed(self):
        for cost in (0.01, 1, "0", None, True, -1):
            with self.subTest(cost=cost):
                self.assert_gate("estimatedNewCostUsd", cost)

    def test_public_release_work_type_denied(self):
        self.assert_gate("workType", "publicRelease")
        self.assert_gate("workType", "deployment")

    def test_no_permission_from_authority_text(self):
        packet = self.packet()
        packet.update({"approvedBy": "Professor", "autoMerge": True, "crownStatus": "GREEN"})
        result = evaluate(packet, POLICY)
        self.assertFalse(result["publicationAuthority"])
        self.assertFalse(result["autonomousWorkerExecution"])
        self.assertFalse(result["changesPerformed"])
        self.assertEqual(result["crownStatus"], "STOP")

    def test_quarantine_remains_active(self):
        quarantine = json.loads((ROOT / POLICY["quarantineRef"]).read_text())
        self.assertEqual(quarantine["state"], "QUARANTINED")
        self.assertIs(quarantine["activeTaskWorkersAllowed"], False)

    def test_source_truth_is_single_authority(self):
        truth = json.loads((ROOT / "doctrine/currentSourceTruthV3.json").read_text())
        self.assertEqual(truth["creativeLayer"]["yumeFastPathCanon"],
                         "doctrine/yumeFastPathCanonV1.json")
        self.assertEqual(truth["promotion"], False)

    def test_explicit_canonical_source_not_global_crown(self):
        self.assertEqual(POLICY["status"], "CANONICAL_ROUTING_SOURCE")
        self.assertEqual(POLICY["defaultTier"], 0)
        self.assertFalse(POLICY["automaticMutation"])
        self.assertFalse(POLICY["automaticPublish"])
        self.assertEqual(POLICY["crownStatus"], "STOP")

    def test_existing_goddess_cabinet_reference(self):
        cabinet = json.loads((ROOT / "doctrine/yumeArtCabinetHandoffV1.json").read_text())
        self.assertEqual(cabinet["fastPathPolicy"], "doctrine/yumeFastPathCanonV1.json")
        self.assertEqual(cabinet["quarantineRef"], POLICY["quarantineRef"])


if __name__ == "__main__":
    unittest.main()

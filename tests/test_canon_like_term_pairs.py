"""Negative controls for proposed two-by-two Canon term sorting."""
from __future__ import annotations
from copy import deepcopy
import json
from pathlib import Path
import unittest

from tools.canonLikeTermPairsAudit import audit, ROOT, CONTRACT


class CanonLikeTermPairsAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = json.loads((ROOT / CONTRACT).read_text(encoding="utf-8"))

    def run_audit(self, mutate=None):
        candidate = deepcopy(self.index)
        if mutate:
            mutate(candidate)
        return audit(ROOT, candidate)

    def test_current_seed_pairs_exist_without_promotion(self):
        result = self.run_audit()
        self.assertEqual(result["errors"], [], result["errors"])
        self.assertEqual(result["pairCount"], 20)
        self.assertEqual(len(result["domains"]), 9)
        self.assertEqual(result["verdict"], "AMBER_PROPOSED_SOURCE_ONLY")
        self.assertFalse(result["releaseAuthority"])
        self.assertFalse(result["liveRuntimeVerified"])
        self.assertEqual(result["crownStatus"], "STOP")

    def test_unknown_path_is_rejected_not_guessed(self):
        def mutation(data):
            data["pairs"][0]["peerPath"] = "doctrine/noSuchHistoricalProofV1.json"
        result = self.run_audit(mutation)
        self.assertTrue(any(x.startswith("MISSING_OR_UNSAFE_PATH") for x in result["errors"]))

    def test_traversal_is_rejected(self):
        def mutation(data):
            data["pairs"][0]["peerPath"] = "../private/secret.json"
        result = self.run_audit(mutation)
        self.assertTrue(any(x.startswith("MISSING_OR_UNSAFE_PATH") for x in result["errors"]))

    def test_duplicate_pair_does_not_create_second_authority(self):
        def mutation(data):
            data["pairs"].append(deepcopy(data["pairs"][0]))
        result = self.run_audit(mutation)
        self.assertTrue(any(x.startswith("DUPLICATE_OR_SELF_PAIR") for x in result["errors"]))

    def test_false_supersession_is_rejected(self):
        def mutation(data):
            data["pairs"][6]["relation"] = "supersedes"
        result = self.run_audit(mutation)
        self.assertTrue(any(x.startswith("UNSUPPORTED_SUPERSESSION") for x in result["errors"]))

    def test_promotion_or_execution_claim_fails_closed(self):
        def mutation(data):
            data["promotion"] = True
            data["evidenceCeiling"]["automaticMerge"] = True
        result = self.run_audit(mutation)
        self.assertIn("PROMOTION_GUARD", result["errors"])
        self.assertIn("UNSAFE_EVIDENCE_CEILING:automaticMerge", result["errors"])

    def test_changed_relationship_must_use_known_relation(self):
        def mutation(data):
            data["pairs"][0]["relation"] = "automaticallyMerge"
        result = self.run_audit(mutation)
        self.assertTrue(any(x.startswith("INVALID_RELATION") for x in result["errors"]))

    def test_json_schema_and_historical_receipts_not_falsely_mislabeled(self):
        result = self.run_audit()
        self.assertEqual(len(result["reviewedJsonSchemaDefinitions"]), 4)
        self.assertEqual(len(result["reviewedDatedHistoricalReceipts"]), 2)
        self.assertEqual(len(result["reviewedIdenticalLegacyTemplateSchemas"]), 1)
        self.assertEqual(result["doctrineFilesWithoutDeclaredSchema"], [])
        self.assertEqual(result["duplicateDeclaredSchemaIds"], {})

    def test_exception_misclassification_reopens_focused_review(self):
        def mutation(data):
            data["reviewedExceptions"]["jsonSchemaDefinitions"][0] = (
                "doctrine/drive3dAssetMutationRollback-20260925.json"
            )
        result = self.run_audit(mutation)
        self.assertIn("JSON_SCHEMA_DEFINITION_REVIEW_DRIFT", result["errors"])

    def test_legacy_duplicate_registry_must_match_actual_bytes_and_schema(self):
        def mutation(data):
            data["reviewedExceptions"]["identicalLegacyTemplates"][0]["schemaId"] = (
                "luhmOs.aiTaskManifest.v2"
            )
        result = self.run_audit(mutation)
        self.assertTrue(any(x.startswith("LEGACY_DUPLICATE_BYTES_OR_SCHEMA_DRIFT")
                            for x in result["errors"]))


if __name__ == "__main__":
    unittest.main()

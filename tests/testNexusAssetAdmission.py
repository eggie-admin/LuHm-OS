#!/usr/bin/env python3
"""Negative contract tests: no free-download-as-free-asset assumption."""
import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "tools/nexusAssetAdmission.py"
spec = importlib.util.spec_from_file_location("nexus_asset_admission", MODULE)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def sample(stage="referenceOnly"):
    return {"candidateId": "nexus-concept-25", "assetRole": "bodyMorphReference",
            "author": "Verify on source page",
            "sourceUrl": "https://www.nexusmods.com/fallout4/mods/25",
            "stage": stage, "includesBinary": stage != "referenceOnly",
            "fileVersion": "owner-verified-version", "sourceSha256": "a" * 64,
            "contentLane": "privateMutation",
            "aiProcessingPlanned": False,
            "rightsEvidence": {
                "fileRightsVerified": True,
                "modAuthorOwnsOrCanLicenseContent": True,
                "upstreamGamePublisherRightsCleared": True,
                "nexusSiteTermsForThisUseChecked": True,
                "offPlatformUseAllowed": True,
                "modificationAllowed": True,
                "exactFilePermissionSource": "https://www.nexusmods.com/fallout4/mods/25",
                "redistributionAllowed": True, "commercialUseAllowed": True,
                "aiProcessingAllowed": True,
            }}


class NexusAssetAdmissionTests(unittest.TestCase):
    def test_offline_reference_discovery_is_allowed(self):
        self.assertEqual(gate.assess(sample()), [])

    def test_bulk_binary_masquerading_as_reference_denied(self):
        asset = sample()
        asset["includesBinary"] = True
        self.assertIn("REFERENCE_HAS_BINARY", gate.assess(asset))

    def test_reject_mod_download_with_missing_off_game_permission(self):
        asset = sample("permittedPrivatePrototype")
        asset["rightsEvidence"]["offPlatformUseAllowed"] = False
        self.assertIn("RIGHTS_offPlatformUseAllowed", gate.assess(asset))

    def test_reject_unverified_game_publisher_rights(self):
        asset = sample("permittedPrivatePrototype")
        asset["rightsEvidence"]["upstreamGamePublisherRightsCleared"] = False
        self.assertIn("RIGHTS_upstreamGamePublisherRightsCleared", gate.assess(asset))

    def test_reject_unverified_site_terms(self):
        asset = sample("permittedPrivatePrototype")
        asset["rightsEvidence"]["nexusSiteTermsForThisUseChecked"] = False
        self.assertIn("RIGHTS_nexusSiteTermsForThisUseChecked", gate.assess(asset))

    def test_reject_wrong_or_http_mod_link(self):
        asset = sample()
        asset["sourceUrl"] = "http://www.nexusmods.com/fallout4/mods/25"
        self.assertIn("INVALID_NEXUS_MOD_URL", gate.assess(asset))
        asset["sourceUrl"] = "https://other.example/fallout4/mods/25"
        self.assertIn("INVALID_NEXUS_MOD_URL", gate.assess(asset))

    def test_reject_no_sha(self):
        asset = sample("permittedPrivatePrototype")
        asset["sourceSha256"] = "not-a-hash"
        self.assertIn("FILE_SHA256_REQUIRED", gate.assess(asset))

    def test_reject_ai_use_without_permission(self):
        asset = sample("permittedPrivatePrototype")
        asset["aiProcessingPlanned"] = True
        asset["rightsEvidence"]["aiProcessingAllowed"] = False
        self.assertIn("AI_PROCESSING_RIGHTS_REQUIRED", gate.assess(asset))

    def test_reject_redistribution_without_permission_and_human(self):
        asset = sample("distributionCandidate")
        asset["contentLane"] = "cathedralPublic"
        asset["rightsEvidence"]["redistributionAllowed"] = False
        asset["rightsEvidence"]["commercialUseAllowed"] = False
        self.assertIn("RIGHTS_redistributionAllowed", gate.assess(asset))
        self.assertIn("RIGHTS_commercialUseAllowed", gate.assess(asset))
        self.assertIn("PROFESSOR_REVIEW_REQUIRED", gate.assess(asset))

    def test_approved_distribution_is_still_only_structural_candidate(self):
        asset = sample("distributionCandidate")
        asset["contentLane"] = "betaAfterDark"
        asset["professorReviewState"] = "approvedForCandidate"
        self.assertEqual(gate.assess(asset), [])
        # Assertion is about format only; there is no network verification or legal verdict.

    def test_canon_nexus_discovery_is_priority_without_runtime_authority(self):
        spec = json.loads((ROOT / "doctrine/nexusCommunityForgePriorityV1.json").read_text(encoding="utf-8"))
        self.assertIn("Nexus Mods", spec["purpose"])
        self.assertTrue(spec["priority"].startswith("TOP_DISCOVERY"))
        self.assertTrue(spec["rightsLaw"]["attributionAloneNotPermission"])
        self.assertFalse(spec["currentProof"]["releasesAuthorized"])
        community = json.loads((ROOT / "doctrine/yumeCommunityArtResourcesV1.json").read_text(encoding="utf-8"))
        self.assertIn("nexusMods", community["sourceFamilies"])
        self.assertIn("nexusCommunityForgePriorityV1.json", community["priorityIntegration"]["target"])


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Hostile-change tests: study metadata never silently becomes artist/game credit."""
import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("artistCreditIntegrity", ROOT / "tools/artistCreditIntegrity.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def fixture():
    used = json.loads((ROOT / "media/artistCreditsApprovedV1.json").read_text(encoding="utf-8"))
    refs = json.loads((ROOT / "media/yumeReferenceGalleryV1.json").read_text(encoding="utf-8"))
    return used, refs


def approved_sample():
    return {
        "assetId": "sampleAsset", "assetTitle": "Sample",
        "creatorDisplayName": "Artist Example",
        "sourcePlatform": "Sketchfab", "sourceUrl": "https://sketchfab.com/3d-models/sample",
        "sourceRevisionOrVersion": "v1",
        "license": "CC BY 4.0",
        "licenseEvidenceUrl": "https://creativecommons.org/licenses/by/4.0/",
        "exactFilePermissionSource": "https://sketchfab.com/3d-models/sample",
        "attributionText": "Sample by Artist Example, CC BY 4.0",
        "sourceHash": "a" * 64,
        "contentLane": "cathedralPublic", "reviewState": "approvedArt",
        "originalCreatorVerified": True,
        "specificFileLicenseAndPermissionsReviewed": True,
        "actualRuntimeUseVerified": True,
        "publicAllowed": True, "professorArtApproval": True,
        "redistributionAllowed": True, "commercialUseAllowed": True,
    }


class ArtistCreditIntegrityTests(unittest.TestCase):
    def test_real_reference_gallery_does_not_create_credits(self):
        used, refs = fixture()
        self.assertGreater(len(refs["cards"]), 0)
        self.assertEqual(used["approvedAssets"], [])
        issues, credits = module.validate(used, refs)
        self.assertEqual(issues, [])
        self.assertEqual(credits, [])

    def test_verified_usage_generates_attribution_without_endorsement(self):
        used, refs = fixture()
        used["approvedAssets"] = [approved_sample()]
        issues, credits = module.validate(used, refs)
        self.assertEqual(issues, [])
        self.assertEqual(len(credits), 1)
        self.assertFalse(credits[0]["endorsedByCreator"])
        self.assertEqual(credits[0]["role"], "verifiedUsedAsset")

    def test_reference_attempting_game_credit_blocks_whole_index(self):
        used, refs = fixture()
        used["approvedAssets"] = [approved_sample()]
        refs["cards"][0]["approvedGameCredit"] = True
        issues, credits = module.validate(used, refs)
        self.assertIn("REFERENCE_CANNOT_CLAIM_GAME_USE", issues)
        self.assertEqual(credits, [])

    def test_license_must_be_asset_specific_not_assumed(self):
        used, refs = fixture()
        asset = approved_sample()
        asset["license"] = "Creative Commons"
        used["approvedAssets"] = [asset]
        issues, credits = module.validate(used, refs)
        self.assertIn("sampleAsset:LICENSE_NOT_SPECIFIC", issues)
        self.assertEqual(credits, [])

    def test_no_verified_permission_no_public_credit(self):
        used, refs = fixture()
        asset = approved_sample()
        asset["redistributionAllowed"] = False
        used["approvedAssets"] = [asset]
        issues, credits = module.validate(used, refs)
        self.assertIn("sampleAsset:NOT_VERIFIED_redistributionAllowed", issues)
        self.assertEqual(credits, [])

    def test_creator_correction_hold_blocks_release_credit_index(self):
        used, refs = fixture()
        used["approvedAssets"] = [approved_sample()]
        used["correctionHoldAssetIds"] = ["sampleAsset"]
        issues, credits = module.validate(used, refs)
        self.assertIn("sampleAsset:CREATOR_CORRECTION_HOLD", issues)
        self.assertEqual(credits, [])

    def test_creator_removal_request_requires_human_review(self):
        used, refs = fixture()
        sample = approved_sample()
        sample["creatorAskedToRemoveAttribution"] = True
        used["approvedAssets"] = [sample]
        issues, credits = module.validate(used, refs)
        self.assertIn("sampleAsset:CREDIT_REMOVAL_REQUEST_NEEDS_REVIEW", issues)
        self.assertEqual(credits, [])

    def test_reference_only_unknown_license_does_not_falsely_claim_use(self):
        used, refs = fixture()
        refs["cards"][0]["license"] = "unknown"
        issues, credits = module.validate(used, refs)
        self.assertEqual(issues, [])
        self.assertEqual(credits, [])

    def test_broken_or_fake_link_not_accepted_as_permission(self):
        used, refs = fixture()
        sample = approved_sample()
        sample["exactFilePermissionSource"] = "javascript:alert(1)"
        used["approvedAssets"] = [sample]
        issues, credits = module.validate(used, refs)
        self.assertIn("sampleAsset:UNSAFE_OR_MISSING_exactFilePermissionSource", issues)
        self.assertEqual(credits, [])

    def test_modified_asset_requires_modification_permission(self):
        used, refs = fixture()
        sample = approved_sample()
        sample["derivativeCreated"] = True
        used["approvedAssets"] = [sample]
        issues, credits = module.validate(used, refs)
        self.assertIn("sampleAsset:DERIVATIVE_PERMISSION_MISSING", issues)
        self.assertEqual(credits, [])


if __name__ == "__main__":
    unittest.main()

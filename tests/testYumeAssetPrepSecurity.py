"""Adversarial read-only Yume->Godot asset intake tests."""
import copy
import hashlib
import json
import struct
import tempfile
import unittest
from pathlib import Path

from tools.yumeGodotAssetPrep import evaluate_candidate, load_json

ROOT = Path(__file__).resolve().parents[1]
TOOLBOX = load_json(ROOT / "doctrine/yumeGodotArtToolboxV1.json")
LANES = load_json(ROOT / "doctrine/contentLaneDoctrineV1.json")


def glb_bytes(version="2.0"):
    data = json.dumps({"asset": {"version": version}}, separators=(",", ":")).encode()
    data += b" " * (-len(data) % 4)
    return struct.pack("<4sII", b"glTF", 2, 20 + len(data)) + struct.pack("<I4s", len(data), b"JSON") + data


class YumeSafeIntakeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "workspace"
        (self.root / "art").mkdir(parents=True)
        self.file = self.root / "art" / "hero.glb"
        self.file.write_bytes(glb_bytes())
        self.manifest = {
            "assetId": "hero01",
            "characterId": "lum",
            "assetType": "characterModel",
            "contentLane": "privateMutation",
            "sourcePath": "art/hero.glb",
            "sourceSha256": hashlib.sha256(self.file.read_bytes()).hexdigest(),
            "provenance": {"author": "Professor", "license": "original"},
            "canonStatus": "candidateReview",
            "publicAllowed": False,
            "godotProfile": "character3d",
            "maturity": "general",
            "scalePolicy": "meters",
            "rigPolicy": "humanoid",
            "materialPolicy": "PBR",
            "animationPolicy": "embedded",
        }

    def tearDown(self):
        self.temp.cleanup()

    def receipt(self, **edits):
        m = copy.deepcopy(self.manifest)
        m.update(edits)
        return evaluate_candidate(m, self.root, TOOLBOX, LANES)

    def assert_red(self, error, **edits):
        receipt = self.receipt(**edits)
        self.assertEqual(receipt["status"], "RED")
        self.assertIn(error, receipt["errors"])
        self.assertIs(receipt["publicationAuthority"], False)

    def test_valid_private_glb_plan_only(self):
        receipt = self.receipt()
        self.assertEqual(receipt["status"], "GREEN_PLAN_ONLY")
        self.assertEqual(receipt["errors"], [])
        self.assertIs(receipt["publicationAuthority"], False)

    def test_rejects_absolute_paths(self):
        self.assert_red("invalidSourcePath", sourcePath=str(self.file))

    def test_rejects_path_traversal(self):
        outside = self.root.parent / "outside.glb"
        outside.write_bytes(glb_bytes())
        self.assert_red("sourceOutsideRepository", sourcePath="../outside.glb")

    def test_rejects_symlink_escape(self):
        outside = self.root.parent / "outside.glb"
        outside.write_bytes(glb_bytes())
        (self.root / "art" / "escape.glb").symlink_to(outside)
        self.assert_red("sourceOutsideRepository", sourcePath="art/escape.glb")

    def test_rejects_backslash_and_null(self):
        self.assert_red("invalidSourcePath", sourcePath="art\\hero.glb")
        self.assert_red("invalidSourcePath", sourcePath="art/\x00hero.glb")

    def test_rejects_wrong_hash(self):
        self.assert_red("sourceHashMismatch", sourceSha256="0" * 64)
        self.assert_red("invalidSourceHash", sourceSha256="pending")

    def test_rejects_disguised_png_or_glb(self):
        self.file.write_bytes(b"NOT-A-GLB")
        self.assert_red("sourceFormatInvalid")
        self.assert_red("profileFormatMismatch", godotProfile="portrait2d")

    def test_rejects_glb_header_length_mismatch(self):
        self.file.write_bytes(glb_bytes() + b"X")
        self.assert_red("sourceFormatInvalid")

    def test_rejects_glb_missing_asset_version(self):
        self.file.write_bytes(glb_bytes("3.0"))
        self.assert_red("sourceFormatInvalid")

    def test_requires_3d_handoff_policy(self):
        self.assert_red("requiredPolicyMissing:rigPolicy", rigPolicy="")

    def test_public_lane_requires_rights_and_approval(self):
        self.assert_red("publicLicenseEvidenceMissing", contentLane="cathedralPublic", publicAllowed=True)
        self.assert_red("publicCreatorCreditMissing", contentLane="cathedralPublic", publicAllowed=True)
        self.assert_red("publicProfessorApprovalMissing", contentLane="cathedralPublic", publicAllowed=True)

    def test_public_lane_blocks_generative_draft_and_protected_references(self):
        opts = {
            "contentLane": "cathedralPublic",
            "publicAllowed": True,
            "licenseEvidence": "rights-cleared original",
            "creatorCredit": "Professor",
            "professorApproval": {"approved": True, "receipt": "reviewed-asset01"},
        }
        self.assert_red("publicGeneratedAiArtDefaultDenied", **opts, generatedWithAi=True)
        self.assert_red("publicProtectedReferenceForbidden", **opts, protectedReferenceRefs=["privateArchive"])

    def test_rejects_private_asset_public_flag(self):
        self.assert_red("publicAllowedRequiresCathedralPublic", publicAllowed=True)

    def test_rejects_public_flag_not_boolean(self):
        self.assert_red("publicAllowedMustBeBoolean", publicAllowed="true")

    def test_rejects_unknown_maturity(self):
        self.assert_red("unknownMaturity", maturity="UNKNOWN")

    def test_rejects_unknown_provenance(self):
        self.assert_red("provenanceMissingOrUnknown", provenance="pending")

    def test_rejects_missing_id_and_profile(self):
        self.assert_red("invalidIdentity:assetId", assetId="../oops")
        self.assert_red("unknownGodotProfile", godotProfile="unknown")

    def test_rejects_sprite_without_frame_data(self):
        self.assert_red("spriteFrameMetadataMissing", godotProfile="sprite2d")

    def test_rejects_portrait_without_alpha_policy(self):
        self.assert_red("alphaDecisionMissing", godotProfile="portrait2d")

    def test_rejects_public_sexualized_asset(self):
        self.assert_red("sexualizedAssetForbiddenPublic", contentLane="cathedralPublic",
                        publicAllowed=True, sexualizedPresentation=True)

    def test_non_dict_manifest_denied(self):
        receipt = evaluate_candidate([], self.root, TOOLBOX, LANES)
        self.assertEqual(receipt["errors"], ["manifestNotObject"])
        self.assertIs(receipt["publicationAuthority"], False)


if __name__ == "__main__":
    unittest.main()

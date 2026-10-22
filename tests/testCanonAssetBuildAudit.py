"""Adversarial tests for the public Godot canon asset firewall (no Godot needed)."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from tools.canonAssetBuildAudit import validate

BASE = Path(__file__).resolve().parents[1]

class CanonAssetGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for source in ("game/assets/canonRuntimeAssetsV1.json", "game/canon/CHARACTER_CANON_V1.json"):
            target = self.root / source
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((BASE / source).read_bytes())
        self.catalog = self.root / "game/assets/canonRuntimeAssetsV1.json"
        self.asset = self.root / "assets/approved3d/testAsset.glb"
        self.asset.parent.mkdir(parents=True)
        self.asset.write_bytes(b"test glb bytes for gate fixture only")
        self.data = json.loads(self.catalog.read_text())
    def save(self):
        self.catalog.write_text(json.dumps(self.data))
    def approved(self):
        row = self.data["worlds"]["cathedral"] = [{
            "id": "testAsset", "status": "runtimeImportProven",
            "path": "res://assets/approved3d/testAsset.glb",
            "sha256": hashlib.sha256(self.asset.read_bytes()).hexdigest(),
            "license": "originalApproved", "approvedBy": "Professor",
            "publicAllowed": True, "importProven": True
        }]
        self.save()
        return row[0]
    def test_source_slots_keep_procedural_fallback(self):
        self.asset.unlink()
        result = validate(self.root)
        self.assertEqual(result["approvedModels"], 0)
    def test_sha_pinned_approved_binary(self):
        self.approved()
        self.assertEqual(validate(self.root)["approvedModels"], 1)
    def test_corrupt_sha_blocks(self):
        row = self.approved()
        row["sha256"] = "0" * 64
        self.save()
        with self.assertRaisesRegex(ValueError, "ASSET_SHA_MISMATCH"):
            validate(self.root)
    def test_rights_not_granted(self):
        row = self.approved()
        row["license"] = "unreviewed"
        self.save()
        with self.assertRaisesRegex(ValueError, "MISSING_RIGHTS"):
            validate(self.root)
    def test_private_unreviewed_asset_cannot_publish(self):
        row = self.data["characters"]["lum"]
        row["path"] = "res://assets/approved3d/testAsset.glb"
        self.save()
        with self.assertRaisesRegex(ValueError, "UNAPPROVED"):
            validate(self.root)
    def test_unregistered_binary_blocks(self):
        self.save()
        with self.assertRaisesRegex(ValueError, "UNREGISTERED"):
            validate(self.root)
    def test_traversal_blocks(self):
        row = self.approved()
        row["path"] = "res://assets/approved3d/../../../private.glb"
        self.save()
        with self.assertRaisesRegex(ValueError, "RESOURCE_TRAVERSAL"):
            validate(self.root)
    def test_duplicate_asset_blocks(self):
        row = self.approved()
        self.data["worlds"]["neonRiverwalk"] = [dict(row)]
        self.save()
        with self.assertRaisesRegex(ValueError, "DUPLICATE_ASSET_REFERENCE"):
            validate(self.root)

if __name__ == "__main__":
    unittest.main()

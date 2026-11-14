import json
import os
import tempfile
import unittest
from pathlib import Path
from importlib.util import module_from_spec, spec_from_file_location

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "canonTransferIndex.py"
spec = spec_from_file_location("canonTransferIndex", SCRIPT)
module = module_from_spec(spec)
spec.loader.exec_module(module)

class TransferIndexTests(unittest.TestCase):
    def test_duplicates_are_evidence_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "source"
            (root / "a").mkdir(parents=True)
            (root / "b").mkdir()
            (root / "a" / "one.txt").write_bytes(b"exact payload")
            (root / "b" / "two.txt").write_bytes(b"exact payload")
            (root / "b" / "other.txt").write_bytes(b"different")
            (root / "b" / "unused.part").write_bytes(b"ignore")
            (root / "link.txt").symlink_to(root / "a" / "one.txt")
            result = module.inventory(root, "f" * 40)
            self.assertEqual(result["fileCount"], 3)
            self.assertEqual(result["duplicateGroupCount"], 1)
            self.assertEqual(len(result["duplicateGroups"][0]["paths"]), 2)
            self.assertEqual(result["status"], "LOCAL_VERIFIED_PENDING_REMOTE_CHECK")
            self.assertFalse(result["promotionAuthority"])
            self.assertEqual(
                sorted(e["relativePath"] for e in result["entries"]),
                ["a/one.txt", "b/other.txt", "b/two.txt"],
            )

    def test_missing_source_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                module.inventory(Path(tmp) / "missing", "f" * 40)

    def test_empty_source_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = module.inventory(Path(tmp), "0" * 40)
            self.assertEqual(result["fileCount"], 0)
            self.assertEqual(result["duplicateGroups"], [])

if __name__ == "__main__":
    unittest.main()

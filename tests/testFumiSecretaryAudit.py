#!/usr/bin/env python3
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("fumiSecretaryAudit", ROOT / "tools" / "fumiSecretaryAudit.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class FumiSecretaryAuditTests(unittest.TestCase):
    def test_current_contract_is_green(self):
        result = MODULE.audit()
        self.assertEqual(result["status"], "GREEN")
        self.assertFalse(result["directMutationAuthority"])

    def test_rejects_mutation_authority(self):
        doctrine = json.loads(MODULE.DOCTRINE.read_text(encoding="utf-8"))
        doctrine["directMutationAuthority"] = True
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text(json.dumps(doctrine), encoding="utf-8")
            with mock.patch.object(MODULE, "DOCTRINE", path):
                with self.assertRaisesRegex(ValueError, "authority unexpectedly enabled"):
                    MODULE.audit()

    def test_rejects_private_drive_locator_in_public_doctrine(self):
        doctrine = json.loads(MODULE.DOCTRINE.read_text(encoding="utf-8"))
        doctrine["badExample"] = "https://drive.google.com/file/d/private-id/view"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text(json.dumps(doctrine), encoding="utf-8")
            with mock.patch.object(MODULE, "DOCTRINE", path):
                with self.assertRaisesRegex(ValueError, "private locator/secret leaked"):
                    MODULE.audit()


if __name__ == "__main__":
    unittest.main()

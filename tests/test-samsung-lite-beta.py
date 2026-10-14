#!/usr/bin/env python3
"""Negative controls for non-root Samsung beta preflight."""
import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("tablet", ROOT / "tools/samsung-lite-beta.py")
tablet = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tablet)

class SamsungLiteTests(unittest.TestCase):
    def test_proposed_source_contract(self):
        status = tablet.check_source()
        self.assertEqual(status["model"], "SM-X400")
        self.assertEqual(status["expectedAndroidSdk"], 36)
        self.assertIs(status["rootRequired"], False)
    def test_wrong_model_rejected(self):
        props = {"ro.product.model": "SM-X300",
                 "ro.build.version.sdk": "36",
                 "ro.product.cpu.abilist": "arm64-v8a"}
        def fake_run(cmd, timeout=30):
            if cmd[-1] == "devices":
                return "List of devices attached\n123\tdevice\n"
            return props[cmd[-1]]
        with patch.object(tablet, "run", side_effect=fake_run):
            with self.assertRaisesRegex(ValueError, "wrong Samsung model"):
                tablet.adb_identity()
    def test_unapproved_device_rejected(self):
        with patch.object(tablet, "run", return_value="List of devices attached\n123\tunauthorized\n"):
            with self.assertRaisesRegex(ValueError, "exactly one"):
                tablet.adb_identity()
    def test_bad_hash_does_not_run_any_executable(self):
        with tempfile.TemporaryDirectory() as path:
            fake = Path(path) / "bad.apk"
            fake.write_bytes(b"not an apk")
            with patch.object(tablet, "run") as execute:
                with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
                    tablet.verify_apk(fake, "0" * 64)
                execute.assert_not_called()
    def test_upgrade_command_never_deletes_app_data(self):
        script = (ROOT / "tools/samsung-lite-beta.py").read_text()
        self.assertIn('"install", "-r", "-t"', script)
        self.assertNotIn('"uninstall"', script)
        self.assertNotIn('"pm", "clear"', script)
        self.assertNotIn('["su"', script)

if __name__ == "__main__":
    unittest.main(verbosity=2)

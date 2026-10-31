#!/usr/bin/env python3
"""Exercise missing-input failures and ensure diagnostics never echo secret values."""
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "tools/checkSamsungSigningInputs.py"
spec = importlib.util.spec_from_file_location("signing_inputs", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SigningInputs(unittest.TestCase):
    def setUp(self):
        self.inputs = dict(BETA_P12_B64="FAKE_KEY_SENTINEL", BETA_PASSWORD="FAKE_PASSWORD_SENTINEL",
                           BETA_ALIAS="FAKE_ALIAS_SENTINEL", TRUSTED_SIGNER="a" * 64)

    def test_all_missing(self):
        self.assertEqual(len(module.check({})), 4)

    def test_workflow_fails_before_downloads(self):
        workflow = (SCRIPT.parents[1] / ".github/workflows/samsung-lite-signed-beta.yml").read_text()
        self.assertLess(workflow.index("Owner CAST and source gate"), workflow.index("Check signing inputs"))
        self.assertLess(workflow.index("run: python3 tools/checkSamsungSigningInputs.py"), workflow.index("actions/setup-java@"))
        step = workflow.split("- name: Check signing inputs", 1)[1].split("- uses:", 1)[0]
        self.assertNotIn("continue-on-error", step)
        for key, name in module.FIELDS.items():
            self.assertIn(key + ": ${{ secrets." + name + " }}", step)

    def test_each_missing(self):
        for key in self.inputs:
            with self.subTest(key=key):
                values = dict(self.inputs)
                values[key] = ""
                self.assertIn("missing:" + module.FIELDS[key], module.check(values))

    def test_invalid_fingerprint(self):
        for value in ("a" * 63, "G" * 64, "a" * 64 + "\n"):
            self.inputs["TRUSTED_SIGNER"] = value
            self.assertTrue(module.check(self.inputs))

    def test_diagnostics_do_not_echo_values(self):
        for valid in (True, False):
            values = dict(self.inputs)
            if not valid:
                values["TRUSTED_SIGNER"] = "INVALID_SECRET_SENTINEL"
            result = subprocess.run([sys.executable, str(SCRIPT)], env={**os.environ, **values},
                                    capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0 if valid else 2)
            for value in values.values():
                self.assertNotIn(value, result.stdout + result.stderr)
            if valid:
                self.assertIn("PRESENT_ONLY", result.stdout)


if __name__ == "__main__":
    unittest.main()

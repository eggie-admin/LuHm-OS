#!/usr/bin/env python3
"""Offline negative tests for the integrated virgin-install debug lane."""
import importlib.util
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("debug_readiness", ROOT / "tools/debug-readiness.py")
debug = importlib.util.module_from_spec(spec)
spec.loader.exec_module(debug)

class DebugReadinessTests(unittest.TestCase):
    def test_exact_source_and_apk_required(self):
        self.assertEqual(debug.require_exact_source("a" * 40), "a" * 40)
        self.assertEqual(debug.require_exact_apk("b" * 64), "b" * 64)
        for candidate in ("main", "a" * 39, "A" * 40, "../secret", ""):
            with self.assertRaises(ValueError):
                debug.require_exact_source(candidate)
        for candidate in ("old", "b" * 63, "B" * 64, "", "0" * 65):
            with self.assertRaises(ValueError):
                debug.require_exact_apk(candidate)

    def test_expected_scoped_checks_present(self):
        names = [name for name, _ in debug.CHECKS]
        self.assertEqual(len(names), len(set(names)))
        for name in ("godot-android-source", "android-webview-boundary",
                     "plugin-first-install", "jquery-cockpit-contract",
                     "device-collector-negative-tests", "cross-layer-release-boundary"):
            self.assertIn(name, names)

    def test_nonzero_never_passes(self):
        with patch.object(debug.subprocess, "run", return_value=subprocess.CompletedProcess([], 7, "fine", "")):
            item = debug.run_check("negative-case", ("python3", "--version"))
        self.assertEqual(item["status"], "FAIL")
        self.assertEqual(item["exitCode"], 7)
        self.assertNotIn("fine", str(item))

    def test_exception_and_timeout_fail(self):
        with patch.object(debug.subprocess, "run", side_effect=FileNotFoundError()):
            self.assertEqual(debug.run_check("missing", ("no-command",))["failureKind"], "missing-executable")
        with patch.object(debug.subprocess, "run", side_effect=subprocess.TimeoutExpired(["x"], 1)):
            self.assertEqual(debug.run_check("slow", ("x",))["failureKind"], "timeout")

    def test_godot_composition_budget_negative_control(self):
        gate_spec = importlib.util.spec_from_file_location("candidate_gate", ROOT / "tools/candidateGate.py")
        gate = importlib.util.module_from_spec(gate_spec)
        gate_spec.loader.exec_module(gate)
        self.assertTrue(gate.check_orchestrator_budget("line\\n" * 325) <= 350)
        with self.assertRaises(ValueError):
            gate.check_orchestrator_budget("line\\n" * 351)

    def test_failure_classification(self):
        self.assertEqual(debug.failure_kind("Traceback (most recent call last)", 1), "python-exception")
        self.assertEqual(debug.failure_kind("Parse Error: broken", 1), "parse-failure")
        self.assertEqual(debug.failure_kind("AssertionError", 1), "assertion-failure")
        self.assertEqual(debug.failure_kind("anything", 0), "none")

if __name__ == "__main__":
    unittest.main(verbosity=2)

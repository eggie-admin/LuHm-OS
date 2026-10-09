#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "buildPublicPluginPackage", ROOT / "tools/buildPublicPluginPackage.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class BuildPublicPluginPackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plugin, cls.mcp, cls.review_tests, _ = MODULE.load_package_inputs()

    def test_package_contracts_are_portable_and_bounded(self):
        self.assertEqual(MODULE.validate_documents(self.plugin, self.mcp, self.review_tests), [])

    def test_invalid_schema_or_non_https_mcp_fails(self):
        plugin = copy.deepcopy(self.plugin)
        plugin["$schema"] = "unknown"
        mcp = copy.deepcopy(self.mcp)
        mcp["mcpServers"]["luhm"]["url"] = "http://example.invalid/mcp"
        errors = MODULE.validate_documents(plugin, mcp, self.review_tests)
        self.assertTrue(any("schema reference" in error for error in errors))
        self.assertTrue(any("canonical HTTPS endpoint" in error for error in errors))

    def test_review_case_count_drift_fails(self):
        review_tests = copy.deepcopy(self.review_tests)
        review_tests["negative"].pop()
        self.assertTrue(MODULE.validate_documents(self.plugin, self.mcp, review_tests))

    def test_build_is_deterministic_and_receipt_matches_archive(self):
        source_ref = "a" * 40
        with tempfile.TemporaryDirectory() as temp_dir:
            first_dir = Path(temp_dir) / "first"
            second_dir = Path(temp_dir) / "second"
            first = MODULE.build_package(source_ref, first_dir, source_ref)
            second = MODULE.build_package(source_ref, second_dir, source_ref)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            with zipfile.ZipFile(first) as archive:
                self.assertEqual(archive.namelist(), sorted(MODULE.MEMBERS))
                self.assertTrue(all(info.date_time == MODULE.FIXED_TIME for info in archive.infolist()))
            receipt = json.loads((first_dir / "publicPluginPackageBuildReceipt.json").read_text())
            self.assertEqual(receipt["sourceRef"], source_ref)
            self.assertEqual(receipt["members"], sorted(MODULE.MEMBERS))
            self.assertEqual(receipt["packageChecks"]["reviewCases"], "5_positive_3_negative")
            self.assertEqual(receipt["artifact"]["sha256"], hashlib.sha256(first.read_bytes()).hexdigest())

    def test_source_drift_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaisesRegex(SystemExit, "SOURCE_DRIFT"):
                MODULE.build_package("a" * 40, Path(temp_dir), "b" * 40)


if __name__ == "__main__":
    unittest.main()

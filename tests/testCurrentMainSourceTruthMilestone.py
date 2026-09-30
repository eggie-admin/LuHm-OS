#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "currentMainSourceTruthMilestoneAudit",
    ROOT / "tools/currentMainSourceTruthMilestoneAudit.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class CurrentMainSourceTruthMilestoneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = MODULE.load(MODULE.SOURCE_PATH)
        cls.snapshot = MODULE.load(MODULE.SNAPSHOT_PATH)
        cls.milestone = MODULE.load(MODULE.MILESTONE_PATH)
        cls.boundary = MODULE.load(MODULE.BOUNDARY_PATH)

    def errors(self, source=None, snapshot=None, milestone=None, boundary=None):
        return MODULE.validate(
            copy.deepcopy(source or self.source),
            copy.deepcopy(snapshot or self.snapshot),
            copy.deepcopy(milestone or self.milestone),
            copy.deepcopy(boundary or self.boundary),
        )

    def test_current_contract_is_valid(self):
        self.assertEqual(self.errors(), [])

    def test_wrong_main_fails(self):
        source = copy.deepcopy(self.source)
        source["reconciliation"]["observedMain"] = "0" * 40
        self.assertTrue(self.errors(source=source))

    def test_authority_creep_fails(self):
        milestone = copy.deepcopy(self.milestone)
        milestone["publicationAuthority"] = True
        self.assertTrue(self.errors(milestone=milestone))

    def test_crown_promotion_fails(self):
        milestone = copy.deepcopy(self.milestone)
        milestone["crownStatus"] = "GREEN"
        self.assertTrue(self.errors(milestone=milestone))

    def test_missing_snapshot_root_fails(self):
        snapshot = copy.deepcopy(self.snapshot)
        snapshot["roots"] = snapshot["roots"][1:]
        self.assertTrue(self.errors(snapshot=snapshot))

    def test_full_source_green_overclaim_fails(self):
        source = copy.deepcopy(self.source)
        source["status"] = "GREEN_FULL_SOURCE_TRUTH_READY"
        self.assertTrue(self.errors(source=source))


if __name__ == "__main__":
    unittest.main()

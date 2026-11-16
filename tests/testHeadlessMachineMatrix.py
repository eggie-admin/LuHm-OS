#!/usr/bin/env python3
"""LuHm 4x4 headless machine audit: deterministic, no device access."""
from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "headlessMachineMatrixAudit", ROOT / "tools/headlessMachineMatrixAudit.py")
assert SPEC is not None and SPEC.loader is not None
matrix = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(matrix)
SOURCE = "f0cb6ee54066b490c0e80efc2c96200fec76ee2d"


class TestHeadlessMachineMatrix(unittest.TestCase):
    def test_canon_is_exactly_four_by_four(self):
        result = matrix.audit_schema()
        self.assertTrue(result["sourceConsistent"], result["issues"])
        self.assertEqual(result["observedCandidateCells"], 16)
        self.assertFalse(result["physicalMachineVerified"])
        self.assertFalse(result["greenAuthority"])

    def test_each_lane_requires_real_external_proof(self):
        for lane in matrix.EXPECTED_LANES:
            with self.subTest(lane=lane):
                pkt = matrix.plan("matrixTask", SOURCE, "privateScope", lane)
                self.assertEqual(pkt["state"], "HOLD_R1_EXTERNAL_PROOF")
                self.assertEqual(len(pkt["stagePlan"]), 4)
                self.assertEqual(pkt["actualPassesExecuted"], 0)
                self.assertFalse(pkt["liveWorkPerformed"])
                self.assertFalse(pkt["vmConnected"])

    def test_refuses_untrusted_or_nonexistent_lane(self):
        for lane in ("", "shell", "../../system", "RetroArch", "capture"):
            with self.subTest(lane=lane), self.assertRaises(ValueError):
                matrix.plan("matrixTask", SOURCE, "privateScope", lane)
        with self.assertRaises(ValueError):
            matrix.plan("matrixTask", "main", "privateScope", "virtualization")
        with self.assertRaises(ValueError):
            matrix.plan("task one", SOURCE, "privateScope", "virtualization")

    def test_detects_duplicate_cells_and_license_bypass(self):
        contract = matrix.load()
        broken = copy.deepcopy(contract)
        broken["matrix"][1]["stages"][0]["id"] = broken["matrix"][0]["stages"][0]["id"]
        self.assertIn("RED_DUPLICATE_CELL", matrix.audit_schema(broken)["issues"])
        broken = copy.deepcopy(contract)
        broken["security"]["romOrFirmwareDistributionAllowed"] = True
        self.assertIn("RED_ROM_FIRMWARE_RIGHTS", matrix.audit_schema(broken)["issues"])

    def test_detects_missing_anchor_and_wrong_stage_order(self):
        contract = matrix.load()
        broken = copy.deepcopy(contract)
        broken["sourceAnchors"].append("../private.key")
        broken["matrix"][3]["stages"][0]["stage"] = "R4"
        result = matrix.audit_schema(broken)
        self.assertIn("RED_CANON_ANCHOR", result["issues"])
        self.assertIn("RED_STAGE_ORDER", result["issues"])

    def test_conditional_loop_is_bounded_and_never_live(self):
        good = matrix.simulate_continue_on_green(("PASS", "PASS", "PASS", "PASS"))
        self.assertEqual(good["state"], "HOLD_FOR_PROFESSOR")
        self.assertEqual(len(good["passesVisited"]), 4)
        self.assertFalse(good["realProofAccepted"])
        self.assertFalse(good["greenAuthority"])
        stopped = matrix.simulate_continue_on_green(("PASS", "STOP", "PASS"))
        self.assertEqual(stopped["passesVisited"], ["R1", "R2"])
        self.assertEqual(stopped["state"], "STOP")
        missing = matrix.simulate_continue_on_green(("PASS",))
        self.assertEqual(missing["state"], "HOLD")
        with self.assertRaises(ValueError):
            matrix.simulate_continue_on_green(("PASS",) * 5)


if __name__ == "__main__":
    unittest.main()

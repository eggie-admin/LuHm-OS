#!/usr/bin/env python3
"""Composite source authority and quarantine assertions."""
from __future__ import annotations
import importlib.util
import unittest
from pathlib import Path

p=Path(__file__).resolve().parents[1]/"tools/finalThreeMachineGate.py"
s=importlib.util.spec_from_file_location("finalThreeMachineGate",p)
assert s and s.loader
m=importlib.util.module_from_spec(s)
s.loader.exec_module(m)

class TestFinalThree(unittest.TestCase):
    def test_three_mutations_present_exactly_once(self):
        r=m.audit()
        self.assertEqual(r["state"],"THREE_SOURCE_CANDIDATES",r["issues"])
        self.assertEqual([x["id"] for x in r["mutations"]],
            ["retroTileText","portableOsRecipe","rTuning"])
        self.assertEqual(r["candidateCells"],48)

    def test_source_only_is_not_cast_or_hardware(self):
        x=m.audit()
        for k in ("realKernelTuned","newBiosProduced","androidSystemImageBuilt",
                  "retroCommercialDataImported","realAiAgentLaunched",
                  "rCIExecutionProvenByThisAudit","castRuntimeProven",
                  "ownerApproval","greenAuthority","crownAuthority"):
            with self.subTest(k=k):
                self.assertIs(x[k],False)

if __name__=="__main__":
    unittest.main()

#!/usr/bin/env python3
"""Negative controls: no fabricated proof or authority promotion."""
import copy
import unittest
from tools.openAiCanonEscalationAudit import ROOT, LEDGER, load, adjudicate

class CanonEscalationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline=load(ROOT,LEDGER)
    def check(self, data):
        return adjudicate(ROOT,data,"0"*40)
    def test_baseline_amber_not_crown(self):
        x=self.check(copy.deepcopy(self.baseline))
        self.assertEqual(x["sourceErrors"],[])
        self.assertEqual(x["status"],"AMBER_EXTERNAL_GATES_SOURCE_AUDITED")
        self.assertFalse(x["fullBackupVerified"])
        self.assertFalse(x["autoRepairExecuted"])
        self.assertEqual(x["crownStatus"],"STOP")
    def test_crown_fabrication_rejected(self):
        x=copy.deepcopy(self.baseline);x["promotion"]=True
        self.assertIn("snapshotCrownBoundary",self.check(x)["sourceErrors"])
    def test_backup_fabrication_rejected(self):
        x=copy.deepcopy(self.baseline);x["snapshot"]["scope"]="COMPLETE_BACKUP"
        self.assertIn("fabricatedFullBackup",self.check(x)["sourceErrors"])
    def test_visual_fabrication_rejected(self):
        x=copy.deepcopy(self.baseline);x["externalObservations"]["visualMount"]="GREEN"
        self.assertIn("fabricatedVisualMountProof",self.check(x)["sourceErrors"])
    def test_render_false_green_rejected(self):
        x=copy.deepcopy(self.baseline)
        x["externalObservations"]["renderHarness"]["matchesGitHubMain"]=True
        self.assertIn("fabricatedRenderEquivalenceOrAuthority",self.check(x)["sourceErrors"])
    def test_mcp_drift_rejected(self):
        x=copy.deepcopy(self.baseline);x["source"]["mcpUrl"]="https://invalid.example/mcp"
        self.assertIn("mcpEndpointDrift",self.check(x)["sourceErrors"])
    def test_site_and_portable_distinction_rejected(self):
        x=copy.deepcopy(self.baseline);x["externalObservations"]["differentPluginIdentities"]=False
        self.assertIn("sitePackageIdentityConflated",self.check(x)["sourceErrors"])
    def test_host_drift_remains_amber_not_autofix(self):
        x=self.check(copy.deepcopy(self.baseline))
        self.assertIn("siteResourceDrift",[v["id"] for v in x["amberFindings"]])
        self.assertIn("historicalRuntimeReceipt",[v["id"] for v in x["amberFindings"]])
        self.assertIn("renderLiveSourceLag",[v["id"] for v in x["amberFindings"]])
        self.assertTrue(all(v["autoFixPermitted"] is False for v in x["amberFindings"]))
if __name__=="__main__":
    unittest.main()

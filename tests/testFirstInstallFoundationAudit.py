"""Fail-closed negative controls for first-install source identity and rights."""
import copy
import json
import unittest
from pathlib import Path
from tools.firstInstallFoundationAudit import ROOT, audit, validate_policy

POLICY = json.loads((ROOT / "doctrine/firstInstallFoundationV1.json").read_text(encoding="utf-8"))

class FirstInstallFoundationAuditTest(unittest.TestCase):
    def test_actual_repo_baseline(self):
        self.assertEqual(audit(), [])
    def test_refuse_fifth_untracked_foundation(self):
        mutant = copy.deepcopy(POLICY)
        mutant["foundations"].append({"id": "shadow", "source": ["README.md"], "runtimeState": "GREEN"})
        self.assertIn("fourFoundations", validate_policy(mutant))
    def test_refuse_fake_live_green(self):
        mutant = copy.deepcopy(POLICY)
        mutant["foundations"][0]["runtimeState"] = "GREEN"
        self.assertIn("noFalseRuntimeGreen", validate_policy(mutant))
    def test_refuse_overwriting_site_binding(self):
        mutant = copy.deepcopy(POLICY)
        mutant["pluginTopology"]["separateSite"]["name"] = "LuHm package override"
        self.assertIn("keepSeparateSite", validate_policy(mutant))
    def test_refuse_public_release_of_unknown_art(self):
        mutant = copy.deepcopy(POLICY)
        mutant["legal"]["doNotAssumeAllAssetsApproved"] = False
        self.assertIn("rights", validate_policy(mutant))
    def test_refuse_unreviewed_dns(self):
        mutant = copy.deepcopy(POLICY)
        mutant["release"]["cloudflareDnsChange"] = True
        self.assertIn("noPublicMutation", validate_policy(mutant))
    def test_refuse_relicensing(self):
        mutant = copy.deepcopy(POLICY)
        mutant["legal"]["repoCodeLicense"] = "MIT"
        self.assertIn("preserveGpl", validate_policy(mutant))

if __name__ == "__main__":
    unittest.main()

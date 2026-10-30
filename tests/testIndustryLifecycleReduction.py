import copy
import tempfile
import unittest
from pathlib import Path
from tools.industryLifecycleReductionAudit import audit, evaluate, inspect_workflows

MAIN = "f0cb6ee54066b490c0e80efc2c96200fec76ee2d"
class LifecycleReductionTests(unittest.TestCase):
    def test_live_source_invariants_only(self):
        from tools.industryLifecycleReductionAudit import ROOT
        x = audit(ROOT, MAIN)
        self.assertEqual(x["sourceGuard"], "PASS", x["errors"])
        self.assertEqual(x["lane"], "PROPOSED_SOURCE_ONLY")
        self.assertFalse(x["legacyBranchesMerged"])
        self.assertFalse(x["workflowReductionExecuted"])
        self.assertFalse(x["publicBetaReady"])
        self.assertFalse(x["marketingPublished"])
        self.assertEqual(x["crown"], "STOP")
        self.assertGreaterEqual(x["workflows"]["count"], 1)
    def test_fake_public_marketing_and_crown_denied(self):
        from tools.industryLifecycleReductionAudit import ROOT, load, POLICY
        p=load(ROOT,POLICY);b=load(ROOT,"doctrine/premonitionEnterpriseBrandV1.json")
        t=load(ROOT,"doctrine/currentSourceTruthV3.json");r=load(ROOT,"doctrine/finalFormPublicReleaseGateV1.json")
        self.assertEqual(evaluate(p,b,t,r), [])
        fake=copy.deepcopy(p);fake["execution"]["autoPublish"]=True
        self.assertIn("unsafeExecution:autoPublish",evaluate(fake,b,t,r))
        fake=copy.deepcopy(p);fake["lanes"][4]["releaseAllowed"]=True
        self.assertIn("unapprovedReleaseLane",evaluate(fake,b,t,r))
        brand=copy.deepcopy(b);brand["authorizations"]["publicMarketing"]=True
        self.assertIn("brandPermissionDrift",evaluate(p,brand,t,r))
        bad=copy.deepcopy(r);bad["fullPublicReleasePublished"]=True
        self.assertIn("publicReleaseNotHeld",evaluate(p,b,t,bad))
    def test_invalid_source_denied(self):
        from tools.industryLifecycleReductionAudit import ROOT
        with self.assertRaises(ValueError):audit(ROOT,"main")
    def test_exact_duplicates_and_action_pins_are_candidates_not_auto_deleted(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)
            (folder/"a.yml").write_text("on: pull_request\njobs:\n  x:\n    steps:\n    - uses: actions/checkout@v4\n")
            (folder/"b.yml").write_text("on: pull_request\njobs:\n  x:\n    steps:\n    - uses: actions/checkout@v4\n")
            (folder/"c.yml").write_text("on: push\njobs:\n  x:\n    steps:\n    - uses: actions/checkout@" + "a"*40 + "\n")
            d=inspect_workflows(folder)
            self.assertEqual(d["count"],3)
            self.assertEqual(d["exactDuplicateGroups"],[["a.yml","b.yml"]])
            names={x["workflow"]:x["flags"] for x in d["reviewCandidates"]}
            self.assertIn("actionNotPinnedToFullCommit",names["a.yml"])
            self.assertNotIn("c.yml",names)
if __name__=="__main__":
    unittest.main()

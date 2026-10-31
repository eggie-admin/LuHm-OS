"""Offline fail-closed tests; distinguish assessed slots from independently tested runtime."""
import copy
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from tools.crownEscalationMatrix import ROOT,PROFILE,assess,git_source_verified,git_commit_has_path

class CrownEscalationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile=json.loads((ROOT/PROFILE).read_text(encoding="utf-8"))
        cls.sha="a"*40

    def test_full_cardinality_with_honest_evidence(self):
        x=assess(ROOT,copy.deepcopy(self.profile),self.sha)
        self.assertEqual((x["level4x4"]["evaluated"],x["level8x8"]["evaluated"],x["level16x16"]["evaluated"]),(16,64,256))
        self.assertEqual(x["totalEvidenceSlots"],336)
        self.assertEqual(x["sourceErrors"],[])
        self.assertEqual(x["level4x4"]["counts"]["PASS_SOURCE"],16)
        self.assertGreater(x["level8x8"]["counts"]["UNVERIFIED"],0)
        self.assertGreater(x["level16x16"]["counts"]["UNVERIFIED"],0)
        self.assertEqual(x["level16x16"]["counts"]["BLOCKED"],16)
        self.assertFalse(x["publicReleaseAuthorized"])
        self.assertFalse(x["realDeviceVerified"])

    def test_hex_shaped_sha_does_not_prove_source_bound(self):
        result=assess(ROOT,self.profile,self.sha)
        self.assertFalse(result["sourceRefIndependentlyChecked"])
        cells=[c for c in result["level8x8"]["cells"] if c["id"].endswith("/sourceBound")]
        self.assertEqual(len(cells),8)
        self.assertTrue(all(c["status"]=="UNVERIFIED" for c in cells))

    def test_exact_clean_git_checkout_and_tracked_blob_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            subprocess.run(["git","init","-q"],cwd=root,check=True)
            (root/"anchor.txt").write_text("source proof\\n",encoding="utf-8")
            subprocess.run(["git","add","anchor.txt"],cwd=root,check=True)
            subprocess.run(["git","-c","user.name=CI Fixture","-c",
                            "user.email=ci@example.invalid","commit","-qm","fixture"],
                           cwd=root,check=True)
            sha=subprocess.check_output(["git","rev-parse","HEAD"],cwd=root,text=True).strip()
            self.assertTrue(git_source_verified(root,sha))
            self.assertTrue(git_commit_has_path(root,sha,"anchor.txt"))
            self.assertFalse(git_source_verified(root,"a"*40))
            (root/"untracked.txt").write_text("not in commit",encoding="utf-8")
            self.assertFalse(git_commit_has_path(root,sha,"untracked.txt"))
            (root/"anchor.txt").write_text("changed",encoding="utf-8")
            self.assertFalse(git_source_verified(root,sha))

    def test_no_fake_auto_release(self):
        p=copy.deepcopy(self.profile)
        p["invariants"]["autoDeploy"]=True
        with self.assertRaisesRegex(ValueError,"UNSAFE_POLICY"):assess(ROOT,p,self.sha)

    def test_no_fake_crown(self):
        p=copy.deepcopy(self.profile)
        p["invariants"]["blockCrown"]=False
        with self.assertRaisesRegex(ValueError,"UNSAFE_POLICY"):assess(ROOT,p,self.sha)

    def test_unknown_sha_not_accepted(self):
        with self.assertRaisesRegex(ValueError,"EXACT_SHA_REQUIRED"):
            assess(ROOT,self.profile,"main")

    def test_four_grid_cannot_be_silently_shrunk(self):
        p=copy.deepcopy(self.profile)
        p["fourByFour"]["columns"].pop()
        with self.assertRaisesRegex(ValueError,"FOUR_BY_FOUR_SCHEMA_DRIFT"):
            assess(ROOT,p,self.sha)

    def test_eight_grid_cannot_be_shrunk(self):
        p=copy.deepcopy(self.profile)
        p["eightByEight"]["components"].pop()
        with self.assertRaisesRegex(ValueError,"EIGHT_BY_EIGHT_SCHEMA_DRIFT"):
            assess(ROOT,p,self.sha)

    def test_sixteen_grid_cannot_be_shrunk(self):
        p=copy.deepcopy(self.profile)
        p["sixteenBySixteen"]["proofs"].pop()
        with self.assertRaisesRegex(ValueError,"SIXTEEN_BY_SIXTEEN_SCHEMA_DRIFT"):
            assess(ROOT,p,self.sha)

    def test_missing_source_component_fails_source_gate(self):
        p=copy.deepcopy(self.profile)
        p["eightByEight"]["components"][0]["path"]="does-not-exist.example"
        result=assess(ROOT,p,self.sha)
        self.assertEqual(result["sourceGuard"],"RED_SOURCE")
        self.assertIn("frontEnd/exists",result["sourceErrors"])

    def test_external_systems_cannot_be_marked_green_by_inventory(self):
        report=assess(ROOT,self.profile,self.sha)
        slots=report["level16x16"]["cells"]
        for target in ("cloudflareWorker","renderService"):
            matching=[s for s in slots if s["id"].startswith(target+"/")]
            self.assertEqual(len(matching),16)
            self.assertFalse(any(s["status"]=="PASS_SOURCE" for s in matching))

    def test_all_ids_unique(self):
        report=assess(ROOT,self.profile,self.sha)
        ids=sum(([x["id"] for x in report[level]["cells"]]
                 for level in ("level4x4","level8x8","level16x16")),[])
        self.assertEqual(len(ids),len(set(ids)))

if __name__=="__main__":unittest.main()

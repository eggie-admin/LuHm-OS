"""Offline fail-closed tests; distinguish assessed slots from independently tested runtime."""
import copy
import json
import unittest
from pathlib import Path
from tools.crownEscalationMatrix import ROOT,PROFILE,assess

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

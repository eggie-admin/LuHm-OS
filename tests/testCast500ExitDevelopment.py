"""500 distinct per-slot checks plus fail-closed release-gate mutations."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import samsungCast500Audit as samsung
from cast500ExitDevelopment import audit, inventory

CONFIG=json.loads((ROOT/"doctrine/cast500ExitDevelopmentGateV1.json").read_text(encoding="utf-8"))


class Cast500ExitDevelopmentTests(unittest.TestCase):
    def test_500_distinct_slot_contracts(self):
        rows=samsung.assess(samsung.load(),run_runner=False)
        self.assertEqual(len(rows),500)
        checks=inventory(rows,runner=False)
        self.assertEqual(checks["evaluated"],500)
        self.assertEqual(checks["errors"],[])
        # 500 subtests each independently checks key, provenance and no false green.
        for row in rows:
            with self.subTest(control=row["id"]):
                self.assertEqual(row["id"],"/".join((row["target"],row["domain"],row["control"])))
                self.assertEqual(row["verdict"],"UNVERIFIED")
                self.assertNotIn(row["target"], ("unknown", "production"))

    def test_source_preflight_and_release_block(self):
        result=audit()
        self.assertEqual(result["sourceErrors"],[])
        self.assertEqual(result["slotInventory"]["evaluated"],500)
        self.assertFalse(result["productionGo"])
        self.assertFalse(result["castAuthorized"])
        self.assertEqual(result["crown"],"STOP")

    def test_reject_fake_samsung_green(self):
        rows=samsung.assess(samsung.load(),run_runner=False)
        rows[0]["verdict"]="PASS"
        rows[0]["evidence"]="synthetic_device_claim"
        self.assertIn("UNSUPPORTED_PASS_CLAIM",inventory(rows,runner=False)["errors"])

    def test_reject_runner_green_without_supported_primitive(self):
        rows=samsung.assess(samsung.load(),run_runner=False)
        target=next(x for x in rows if x["target"]=="githubRunner")
        target["verdict"]="PASS"
        target["evidence"]="unverified_magic"
        self.assertIn("UNSUPPORTED_PASS_CLAIM",inventory(rows,runner=True)["errors"])

    def test_reject_duplicate_slot(self):
        rows=samsung.assess(samsung.load(),run_runner=False)
        rows[1]=dict(rows[0])
        self.assertIn("NONCANONICAL_OR_DUPLICATE_SLOT",inventory(rows,runner=False)["errors"])

    def test_reject_missing_slot(self):
        rows=samsung.assess(samsung.load(),run_runner=False)
        self.assertIn("MISSING_OR_EXTRANEOUS_SLOTS",inventory(rows[:-1],runner=False)["errors"])

    def test_reject_false_production_evidence(self):
        x=copy.deepcopy(CONFIG)
        x["promotionProof"]["samsungSameArtifactInstallAndLaunch"]=True
        self.assertIn("proofPending",audit(config_override=x)["sourceErrors"])

    def test_reject_implicit_merge(self):
        x=copy.deepcopy(CONFIG)
        x["actions"]["writeMain"]=True
        self.assertIn("noSideEffects",audit(config_override=x)["sourceErrors"])

    def test_reject_cast_dispatch_claim(self):
        x=copy.deepcopy(CONFIG)
        x["actions"]["dispatchCast"]=True
        self.assertIn("noSideEffects",audit(config_override=x)["sourceErrors"])

    def test_reject_release_green_claim(self):
        x=copy.deepcopy(CONFIG)
        x["crownStatus"]="GREEN"
        self.assertIn("crownStop",audit(config_override=x)["sourceErrors"])

    def test_reject_pseudo_500_count(self):
        x=copy.deepcopy(CONFIG)
        x["assessment"]["slots"]=499
        self.assertIn("matrixDimensions",audit(config_override=x)["sourceErrors"])

    def test_reject_release_phase_auto_ready(self):
        x=copy.deepcopy(CONFIG)
        x["releasePhases"]["publicStable"]["ready"]=True
        self.assertIn("promotionDisabled",audit(config_override=x)["sourceErrors"])


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Four-lane read-only routing tests plus canonical namespace/edge prohibitions."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
sp=importlib.util.spec_from_file_location("universalFourLanePlan",ROOT/"tools/universalFourLanePlan.py")
router=importlib.util.module_from_spec(sp)
sp.loader.exec_module(router)

class UniversalFourLaneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ref=router.exact_sha()
        cls.policy=router.contract()

    def test_four_release_four_transport_full_matrix(self):
        for lane in router.LANES:
            for transport in router.TRANSPORTS:
                out=router.plan(lane,"sourceStatus",transport,"test-one",self.ref)
                self.assertEqual(out["lane"],lane)
                self.assertEqual(out["transport"],transport)
                self.assertFalse(out["routeAvailable"])
                self.assertFalse(out["workerExecuted"])
                self.assertFalse(out["authorizedToMutate"])
                self.assertEqual(out["crownStatus"],"STOP")

    def test_four_capabilities_canonical_six_role_selection(self):
        for cap in router.CAPABILITIES:
            out=router.plan("beta",cap,"offlineFallback","test-two",self.ref)
            self.assertIn(out["proposedRole"],self.policy["agents"]["proposalSix"])

    def test_bad_route_fails(self):
        with self.assertRaises(ValueError):
            router.plan("nightly","shellExec","offlineFallback","bad",self.ref)

    def test_bad_source_ref_fails(self):
        with self.assertRaises(ValueError):
            router.plan("lts","sourceStatus","offlineFallback","bad","b"*40)

    def test_task_injection_fails(self):
        with self.assertRaises(ValueError):
            router.plan("lts","sourceStatus","offlineFallback","../secret",self.ref)

    def test_all_15_workers_still_quarantined(self):
        quarantine=json.loads((ROOT/"doctrine/companyWideOperationalQuarantineV1.json").read_text())
        self.assertEqual(quarantine["registeredCount"],15)
        self.assertFalse(quarantine["activeTaskWorkersAllowed"])
        self.assertEqual(self.policy["agents"]["workersActive"],0)
        self.assertEqual(len(self.policy["agents"]["proposalSix"]),6)

    def test_edge_preserves_direct_render_and_no_location_check(self):
        edge=self.policy["transport"]
        self.assertFalse(edge["existingPublicMcp"]["cloudflareProxy"])
        self.assertFalse(edge["existingPublicMcp"]["tunnel"])
        self.assertFalse(edge["candidateVm"]["deployed"])
        self.assertFalse(edge["noClientGeolocationWithoutConsent"] is False)
        self.assertTrue(edge["noLocationCollection"])
        self.assertTrue(edge["noPublicOriginPort"])
        self.assertTrue(edge["noRawSqlRoute"])

    def test_no_unreviewed_vendor_activation(self):
        self.assertEqual(self.policy["runtime"]["lightningScript"],"UNRESOLVED_UNMAPPED_NAMESPACE")
        self.assertEqual(self.policy["runtime"]["piForge"],"UNRESOLVED_NAME_NO_RENAME")
        self.assertFalse(self.policy["engines"]["optionalDoNotBundle"] is False)
        self.assertFalse(self.policy["safety"]["alterGplLicenses"])
        self.assertEqual(self.policy["safety"]["crownStatus"],"STOP")

    def test_four_packages_separate_from_lanes(self):
        self.assertEqual(self.policy["fourByFour"]["packageFormats"],["dev","npm","dmg","apk"])
        self.assertEqual(self.policy["fourByFour"]["releaseLanes"],["nightly","beta","lts","legacy"])
        self.assertEqual(len(self.policy["fourByFour"]["layers"]),4)

if __name__=="__main__":
    unittest.main()

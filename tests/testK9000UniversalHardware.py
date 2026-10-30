#!/usr/bin/env python3
"""Negative controls for the universal hardware and provider boundary."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("universalAudit",ROOT/"tools/k9000UniversalHardwareAudit.py")
auditmod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(auditmod)
spec2=importlib.util.spec_from_file_location("headless",ROOT/"host/api/k9000HeadlessCore.py")
backend=importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(backend)

class UniversalHardwareTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        def read(path):return json.loads((ROOT/path).read_text())
        cls.hw=read("doctrine/k9000UniversalHardwareV1.json")
        cls.vendors=read("doctrine/k9000UniversalVendorSurfaceV1.json")
        cls.truth=read("doctrine/currentSourceTruthV3.json")
        cls.canon=read("doctrine/k9000CrownCathedralReleaseV1.json")
        cls.hold=read("doctrine/companyWideOperationalQuarantineV1.json")
        cls.backend=(ROOT/"host/api/k9000HeadlessCore.py").read_text()
    def check_fail(self,mutate,expected):
        x=[copy.deepcopy(t) for t in (self.hw,self.vendors,self.truth,self.canon,self.hold)]
        mutate(*x)
        checks=auditmod.evaluate(*x,self.backend)
        self.assertIn(expected,[k for k,v in checks.items() if not v])
    def test_current_contract(self):
        result=auditmod.audit()
        self.assertEqual([],result["failed"])
        self.assertEqual("SOURCE_GREEN_ONLY",result["verdict"])
        self.assertGreaterEqual(result["sourceChecks"],40)
    def test_driver_cannot_claim_green_without_hardware(self):
        self.check_fail(lambda h,*_:h["inventory"][-2].update(verifiedRuntime=True),"noDriverPretend")
    def test_unidentified_bluetooth_jack_not_green(self):
        self.check_fail(lambda h,*_:h["inventory"][-1].update(model="Verified interface"),"bluetoothJackPending")
    def test_no_google_entitlement_inferred(self):
        self.check_fail(lambda h,v,*_:v["vendors"]["google"]["catalog"]["gemini"].update(readiness="CONNECTED"),"geminiNotAutoAuth")
    def test_no_change_in_compatibility_authority(self):
        self.check_fail(lambda h,v,*_:v["priority"].update(changeToPrimaryOrder="CROWNED"),"oldCanonPrecedencePreserved")
    def test_no_remote_binding(self):
        with self.assertRaises(ValueError):
            backend.LocalOnlyHTTP(("0.0.0.0",0),backend.Handler)
    def test_real_headless_loopback_and_sql_smoke(self):
        result=backend.smoke()
        self.assertEqual(result["status"],"HEADLESS_LOOPBACK_SMOKE_GREEN")
        self.assertEqual(result["sqlite"],"IN_MEMORY_GREEN")
        self.assertFalse(result["publicEndpoint"])
if __name__=="__main__":
    unittest.main()

#!/usr/bin/env python3
"""Negative Samsung firmware gates and honest 500-slot/mo-cap evidence."""
import copy
import importlib.util
import json
import math
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]

def load(name,rel):
    sp=importlib.util.spec_from_file_location(name,ROOT/rel)
    mod=importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod)
    return mod
cast=load("samsungCast500Audit","tools/samsungCast500Audit.py")
cam=load("sixCamTimingAudit","tools/sixCamTimingAudit.py")

class SamsungCastTests(unittest.TestCase):
    def setUp(self):
        self.policy=cast.load()
    def test_500_distinct_slots_four_layers(self):
        rows=cast.assess(self.policy,False)
        self.assertEqual(len(rows),500)
        self.assertEqual(len({r["id"] for r in rows}),500)
        self.assertEqual(sum(map(len,cast.DOMAINS.values())),100)
        self.assertEqual(cast.checks(self.policy),[])
    def test_400_hardware_unknown(self):
        rows=cast.assess(self.policy,True)
        physical=[r for r in rows if r["target"]!="githubRunner"]
        self.assertEqual(len(physical),400)
        self.assertTrue(all(r["verdict"]=="UNVERIFIED" for r in physical))
    def test_firmware_flash_policy_red(self):
        p=copy.deepcopy(self.policy)
        p["approval"]["firmwareFlash"]=True
        self.assertIn("ALL_DESTRUCTIVE_BLOCKED",cast.checks(p))
    def test_deX_on_lite_falsification_red(self):
        p=copy.deepcopy(self.policy)
        p["samsung"]["s10LiteDex"]="FULL_DEX"
        self.assertIn("DEX_LIMIT",cast.checks(p))
    def test_fake_npu_red(self):
        p=copy.deepcopy(self.policy)
        p["studio"]["npuPresent"]=True
        self.assertIn("NO_INVENTED_NPU",cast.checks(p))
    def test_risky_bootloader_red(self):
        p=copy.deepcopy(self.policy)
        p["approval"]["grubWrite"]=True
        self.assertIn("ALL_DESTRUCTIVE_BLOCKED",cast.checks(p))
    def test_agents_remain_quarantined(self):
        p=copy.deepcopy(self.policy)
        p["ai"]["activeWorkers"]=15
        self.assertIn("NO_PROVIDER_AUTO_USE",cast.checks(p))
    def test_six_cameras_missing_rejected(self):
        with self.assertRaises(ValueError):
            cam.assess({"cam0":[i/30 for i in range(40)]})
    def test_six_synthetic_time_series_pass_not_hardware_proof(self):
        x={f"cam{i}":[j/30+i/2000 for j in range(40)] for i in range(6)}
        y=cam.assess(x)
        self.assertEqual(y["verdict"],"PASS_SUBMITTED_TIMESTAMPS_ONLY")
        self.assertFalse(y["cameraDevicesOpened"])
        self.assertFalse(y["calibrationProven"])
    def test_bad_camera_timestamps_rejected(self):
        x={f"cam{i}":[j/30 for j in range(40)] for i in range(6)}
        x["cam3"][5]=float("nan")
        with self.assertRaises(ValueError):cam.assess(x)
    def test_sync_gap_reported_without_claiming_real_stream(self):
        x={f"cam{i}":[j/30+(0.1 if i==5 else 0.0) for j in range(40)] for i in range(6)}
        r=cam.assess(x)
        self.assertEqual(r["verdict"],"GAP_TIMING")
        self.assertFalse(r["framesCaptured"])
    def test_samsung_source_and_licenses_not_mutated(self):
        self.assertTrue((ROOT/"LICENSE").is_file())
        p=json.loads((ROOT/"doctrine/vendorApacheReadinessV1.json").read_text())
        self.assertFalse(p["licenseChangeAllowed"])
        self.assertFalse(self.policy["approval"]["mainMerge"])

if __name__=="__main__":
    unittest.main()

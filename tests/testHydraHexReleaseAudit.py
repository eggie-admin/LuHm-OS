#!/usr/bin/env python3
"""Deterministic source-only tests; no package installation or cloud access."""
import importlib.util
from pathlib import Path
from copy import deepcopy
import unittest
from unittest import mock

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("hydraHex",ROOT/"tools/hydraHexReleaseAudit.py")
hydra=importlib.util.module_from_spec(spec)
spec.loader.exec_module(hydra)

class HexReleaseTests(unittest.TestCase):
    def test_256_base_has_4_formats_and_exact_hex_addressing(self):
        receipt=hydra.assess(256)
        self.assertEqual(receipt["cellCount"],256)
        self.assertEqual(receipt["profilesAssessed"],4)
        self.assertEqual((receipt["hexFirst"],receipt["hexLast"]),("0x000","0x0ff"))
        self.assertEqual({c["family"] for c in receipt["cells"]},{"deb","dmg","apk","npm"})
        self.assertEqual([x["hex"] for x in receipt["cells"]],[f"0x{i:03x}" for i in range(256)])
        self.assertEqual(sum(receipt["counts"].values()),256)
        self.assertEqual(receipt["crownStatus"],"STOP")
    def test_512_and_1024_add_distinct_profiles_not_recast_green(self):
        r512=hydra.assess(512)
        r1024=hydra.assess(1024)
        self.assertEqual((r512["cellCount"],r512["profilesAssessed"],r512["hexLast"]),(512,8,"0x1ff"))
        self.assertEqual((r1024["cellCount"],r1024["profilesAssessed"],r1024["hexLast"]),(1024,16,"0x3ff"))
        self.assertEqual(len({(x["family"],x["profile"]) for x in r1024["cells"]}),16)
        for receipt in (r512,r1024):
            self.assertFalse(receipt["apkInstalled"])
            self.assertFalse(receipt["dmgNotarized"])
            self.assertFalse(receipt["npmPublished"])
            self.assertFalse(receipt["googleDriveWrite"])
    def test_release_never_promoted_by_source_checks(self):
        for slots in (256,512,1024):
            rows=hydra.assess(slots)["cells"]
            self.assertTrue(all(c["stage"]=="source" for c in rows if c["status"]=="GREEN_SOURCE"))
            self.assertTrue(all(c["status"]=="BLOCKED_CROWN" for c in rows if c["stage"]=="release"))
            self.assertTrue(all(c["status"]!="GREEN_SOURCE" for c in rows if c["control"]=="deviceOrHostSmoke"))
            self.assertTrue(any(c["status"].startswith("AMBER") for c in rows))
    def test_unknown_or_mismatched_source_ref_is_denied(self):
        with self.assertRaisesRegex(ValueError,"RED_SOURCE_REF_MISMATCH"):
            hydra.assess(256,source_ref="0"*40)
        with self.assertRaisesRegex(ValueError,"RED_UNAPPROVED_SCALE"):
            hydra.assess(200)
    def test_forced_release_authority_is_red(self):
        original=hydra.load_json
        def tampered(path):
            data=deepcopy(original(path))
            if path=="doctrine/hydraHexReleaseMatrixV1.json":
                data["crownStatus"]="GREEN"
            return data
        with mock.patch.object(hydra,"load_json",side_effect=tampered):
            with self.assertRaisesRegex(ValueError,"RED_MATRIX_CANON_DRIFT"):
                hydra.assess(256)
    def test_company_quarantine_conflict_is_red(self):
        original=hydra.load_json
        def tampered(path):
            data=deepcopy(original(path))
            if path=="doctrine/companyWideOperationalQuarantineV1.json":
                data["activeTaskWorkersAllowed"]=True
            return data
        with mock.patch.object(hydra,"load_json",side_effect=tampered):
            with self.assertRaisesRegex(ValueError,"RED_WORKER_AUTHORITY_CHANGED"):
                hydra.assess(256)

if __name__=="__main__":
    unittest.main()

#!/usr/bin/env python3
"""Portable flavor/source recipe tests: no actual UEFI, firmware, root or install."""
from __future__ import annotations
import copy
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

P=Path(__file__).resolve().parents[1]/"tools/portableOsRecipeAudit.py"
s=importlib.util.spec_from_file_location("portableOsRecipeAudit",P)
assert s and s.loader
m=importlib.util.module_from_spec(s)
s.loader.exec_module(m)
SHA="f0cb6ee54066b490c0e80efc2c96200fec76ee2d"


class TestPortableOs(unittest.TestCase):
    def test_four_by_four_source_stops_at_device_boundaries(self):
        a=m.source_audit()
        self.assertEqual(a["state"],"SOURCE_ONLY",a["issues"])
        self.assertEqual(a["matrixCells"],16)
        self.assertFalse(a["kernelCompiled"])
        self.assertFalse(a["biosFlashed"])
        self.assertFalse(a["debianImageProduced"])
        self.assertFalse(a["ubuntuOfficialFlavor"])

    def test_linux_debian_ubuntu_rpi_android_as_separate_recipe_targets(self):
        for target,arch in (("debian","x86_64"),("ubuntu","aarch64"),
                            ("androidGki","aarch64"),("raspberryPi","aarch64")):
            with self.subTest(target=target):
                p=m.plan(target=target,architecture=arch,source_ref=SHA,
                         requested_packages=[] if target=="androidGki" else ["git","python3"])
                self.assertEqual(p["target"],target)
                self.assertEqual(len(p["fourEvidenceCells"]),4)
                self.assertFalse(p["bootImageBuilt"])
                self.assertFalse(p["vendorDriversReplaced"])
                self.assertFalse(p["packageInstallationPerformed"])
                self.assertFalse(p["releaseOrDistributionAuthorized"])
                self.assertEqual(p["packages"],[] if target=="androidGki" else ["git","python3"])

    def test_rejects_shell_injection_bad_arch_invalid_packages_and_fake_commit(self):
        cases=(
            dict(target="rootShell"),
            dict(architecture="mips"),
            dict(source_ref="main"),
            dict(requested_packages=["sudo apt update"]),
            dict(requested_packages=["python3","python3"]),
            dict(requested_packages=["x"]*9),
            dict(requested_packages=["LD_PRELOAD"]),
            dict(target="androidGki",requested_packages=["python3"]),
            dict(target="raspberryPi",architecture="x86_64"),
        )
        for changed in cases:
            with self.subTest(changed=changed),self.assertRaises(ValueError):
                m.plan(**dict(target="debian",architecture="x86_64",source_ref=SHA,
                              requested_packages=[],**changed)) if not changed else m.plan(
                    **{**dict(target="debian",architecture="x86_64",
                       source_ref=SHA,requested_packages=[]),**changed})

    def test_forged_source_firmware_flash_and_universal_bios_claim_fail_closed(self):
        original=m._read
        def forged(path):
            d=original(path)
            if path==m.POLICY:
                d=copy.deepcopy(d)
                d["platform"]["noFirmwareFlash"]=False
                d["platform"]["commonInterface"]="ONE_BIOS_FOR_EVERYTHING"
            return d
        with patch.object(m,"_read",side_effect=forged):
            out=m.source_audit()
        self.assertIn("RED_OS_AUTHORITY",out["issues"])
        self.assertIn("RED_OS_FALSE_UNIVERSAL_BIOS",out["issues"])
        with patch.object(m,"_read",side_effect=forged):
            plan=m.plan(target="debian",architecture="x86_64",source_ref=SHA,
                        requested_packages=[])
        self.assertEqual(plan["state"],"STOP_SOURCE_DRIFT")

if __name__=="__main__":
    unittest.main()

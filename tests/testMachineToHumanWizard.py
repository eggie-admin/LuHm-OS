#!/usr/bin/env python3
"""Read-only and synthetic-host tests for the machine-to-human wizard."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("machineWizard",ROOT/"tools/machineToHumanWizard.py")
wizard=importlib.util.module_from_spec(spec)
spec.loader.exec_module(wizard)

class MachineWizardTests(unittest.TestCase):
    def testFourLevelsAndNoPrivilegedOperations(self):
        contract=json.loads((ROOT/"doctrine/machineToHumanWizardV1.json").read_text())
        self.assertEqual([x["id"] for x in contract["phases"]],["machine","vendor","services","human"])
        self.assertTrue(contract["readOnlyDefault"])
        self.assertTrue(contract["noPrivilegedCalls"])
        self.assertTrue(contract["noAutoInstall"])
        self.assertTrue(contract["noFirmwareWrites"])
    def testProfilesAndKnownVendorConstraints(self):
        rows=[
          ({"system":"Android","machine":"aarch64","vendor":{"model":"SM-X400","verifiedBoot":"green","bootloaderLocked":"1"}},"androidSamsung",False,False),
          ({"system":"Android","vendor":{"model":"Pixel","verifiedBoot":"green","bootloaderLocked":"1"}},"androidGeneric",False,False),
          ({"system":"Linux","machine":"x86_64","vendor":{}},"linuxHost",True,False),
          ({"system":"Windows","vendor":{}},"windowsHost",False,True),
          ({"system":"Darwin","vendor":{}},"macHost",False,False),
        ]
        for facts,profile,gparted,rufus in rows:
            with self.subTest(profile=profile):
                result=wizard.evaluate(facts,synthetic=True)
                self.assertEqual(result["hostProfile"],profile)
                self.assertEqual(result["gpartedEligibleHost"],gparted)
                self.assertEqual(result["rufusEligibleHost"],rufus)
                self.assertFalse(result["physicalDeviceVerified"])
                self.assertFalse(result["diskWritesPerformed"])
                self.assertFalse(result["bootloaderChanged"])
                self.assertFalse(result["packagesInstalled"])
                self.assertEqual(result["crownStatus"],"STOP")
    def testUnknownAndMissingAndroidBootEvidence(self):
        result=wizard.evaluate({"system":"Android","vendor":{"model":"SM-X400"}},synthetic=True)
        self.assertTrue(result["bootProtectionUndetermined"])
        self.assertEqual(result["escalation"],"NO_AUTOMATIC_ESCALATION")
        unknown=wizard.evaluate({"system":"Other","vendor":{}},synthetic=True)
        self.assertFalse(unknown["hostSupported"])
    def testShellCommandsAreFixedReadOnlyAllowlist(self):
        for args in [
          ["mkfs.ext4","/dev/sda"],["lsblk","-o","SERIAL"],
          ["getprop","ro.serialno"],["sudo","gparted"],
          ["rufus","--format"],["lsblk","--json"]]:
            with self.subTest(args=args),self.assertRaises(ValueError):
                wizard._safeCommand(args)
    def testAndroidProbeDoesNotReadDisk(self):
        with mock.patch.object(wizard,"_safeCommand",return_value="SM-X400") as probe:
            with mock.patch.object(wizard.Path,"exists",return_value=True):
                facts=wizard.observe(includeDisks=True)
            self.assertEqual(facts["system"],"Android")
            self.assertIsNone(facts["diskInventory"])
            self.assertTrue(all(call.args[0][0]=="getprop" for call in probe.call_args_list))
    def testNoCommandsRunForFixture(self):
        with mock.patch.object(wizard,"subprocess") as process:
            out=wizard.evaluate({"system":"Linux","machine":"x86_64","vendor":{}},synthetic=True)
            self.assertEqual(out["hostProfile"],"linuxHost")
            process.run.assert_not_called()

if __name__=="__main__":
    unittest.main()

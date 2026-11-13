"""Read-only canon smoke checks for Linux collaboration and Apple release authority.

This test makes no network requests, reads no credentials, and never invokes ADB.
"""
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "doctrine/linuxStudioAppleCollaborationV1.json"
TRUTH = ROOT / "doctrine/currentSourceTruthV3.json"


class LinuxStudioAppleCollaborationCanonTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        cls.truth = json.loads(TRUTH.read_text(encoding="utf-8"))

    def test_source_of_truth_pointer(self):
        pointer = self.truth["linuxStudioCollaboration"]
        self.assertEqual(pointer["contract"], "doctrine/linuxStudioAppleCollaborationV1.json")
        self.assertFalse(pointer["promotion"])
        self.assertEqual(pointer["crownStatus"], "STOP")
        self.assertEqual(self.truth["crownStatus"], "STOP")
        self.assertFalse(self.truth["publicationAuthority"])

    def test_canonical_repository_and_roles(self):
        value = self.contract
        self.assertEqual(value["canonicalRepository"], "eggie-admin/LuHm-OS")
        self.assertEqual(value["authority"], "Professor")
        self.assertEqual(value["developerWorkstations"]["professor"]["platform"], "linux")
        self.assertEqual(value["developerWorkstations"]["alex"]["platform"], "linux")
        self.assertFalse(value["developerWorkstations"]["professor"]["hostVerified"])
        self.assertFalse(value["developerWorkstations"]["alex"]["hostVerified"])
        self.assertEqual(value["releaseMatrix"]["apple"]["engineeringAdmin"], "alex")

    def test_apple_release_gates(self):
        apple = self.contract["releaseMatrix"]["apple"]
        self.assertIn("PROFESSOR", apple["stableMerge"])
        self.assertIn("PROFESSOR", apple["stableDeploy"])
        self.assertIn("macos", apple["buildOn"].lower())
        self.assertFalse(apple["noAndroidReleaseAuthorityFromAppleRole"] is False)
        self.assertFalse(self.contract["promotion"])
        self.assertFalse(self.contract["publicationAuthority"])
        self.assertFalse(self.contract["releaseAuthority"])
        self.assertEqual(self.contract["crownStatus"], "STOP")

    def test_python_lemp_stack_is_not_php(self):
        stack = self.contract["runtimeStack"]
        self.assertEqual(stack["definition"], {
            "L": "Linux", "E": "NGINX (Engine-X)",
            "M": "MariaDB", "P": "Python 3",
        })
        self.assertEqual(stack["backendRuntime"], "python3")
        self.assertFalse(stack["phpRequirement"])
        self.assertTrue(stack["noAutomaticServiceStart"])
        self.assertTrue(stack["noProductionServiceProof"])
        runbook = (ROOT / "manual/professor-ubuntu2604-basement.md").read_text(encoding="utf-8")
        self.assertIn("LuHm-OS LEMP (Python variant)", runbook)
        self.assertIn("PHP-FPM and Apache are not required", runbook)

    def test_unverified_hardware_remains_unverified(self):
        proof = self.contract["deviceProof"]
        self.assertEqual(proof["linuxAndroidWirelessDebug"]["pairingState"], "UNVERIFIED")
        self.assertEqual(proof["bluetoothVoice"]["dualMicWithoutCaptureProof"], "UNVERIFIED")
        self.assertFalse(self.contract["verification"]["adbPairingProven"])
        self.assertFalse(self.contract["verification"]["bluetoothInputRoutingProven"])
        self.assertFalse(self.contract["verification"]["macNativeDmgBuilt"])
        self.assertFalse(self.contract["verification"]["signedFdroidRepoPublished"])

    def test_public_contract_contains_no_private_device_identifiers(self):
        source = CONTRACT.read_text(encoding="utf-8")
        for sensitive in ("LumOS dictation", "192.168.", "10.0.", "adb pair ", "pairingCode"):
            self.assertNotIn(sensitive, source)
        self.assertTrue(self.contract["privacy"]["noBluetoothDeviceNamesInPublicSource"])


if __name__ == "__main__":
    unittest.main()

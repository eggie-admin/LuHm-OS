"""Canon hardware profiles are source-only; never probe actual private device IDs."""
import unittest
from tools import machineHarnessSeal as m
SHA = "a"*40

def facts(system="Linux", boardModel="", brand="unknown", net=None, bluetooth=False):
    return {"system":system,"boardModel":boardModel,"machine":"aarch64",
            "androidBrand":brand,"networkInterfaces":list(net or []),
            "bluetoothPresent":bluetooth}

class MachineHarnessTests(unittest.TestCase):
    def test_zero_two_has_single_otg_role_and_csi_not_dsi(self):
        r=m.evaluate(facts(boardModel="Raspberry Pi Zero 2 W Rev 1.0",net=["usb"],bluetooth=True),SHA,True)
        self.assertEqual(r["profileId"],"piZero2W")
        self.assertTrue(r["usbGadgetCandidate"])
        self.assertIs(r["usbHostAndGadgetSimultaneous"],False)
        self.assertEqual(r["displayPort"],"CSI_CAMERA_NOT_DSI_DISPLAY")
        self.assertFalse(r["ribbonDisplayVerified"])
        self.assertFalse(r["slimlineSataPowerVerified"])
        self.assertFalse(r["physicalDeviceVerified"])
    def test_pi_three_dsi_and_usb_host_no_usb_gadget(self):
        x=m.evaluate(facts(boardModel="Raspberry Pi 3 Model B Rev 1.2"),SHA,True)
        self.assertEqual(x["profileId"],"pi3ModelB")
        self.assertFalse(x["usbGadgetCandidate"])
        self.assertTrue(x["usbHostCandidate"])
    def test_pico_is_not_a_linux_container_host(self):
        r=m.evaluate(facts(boardModel="Raspberry Pi Pico W"),SHA,True)
        self.assertEqual(r["profileId"],"picoW")
        self.assertFalse(r["hostLinuxCandidate"])
    def test_android_families_no_firmware_claim(self):
        for brand,expected in [("samsung","androidSamsung"),("pixel","androidPixel")]:
            x=m.evaluate(facts("Android","",brand),SHA,True)
            self.assertEqual(x["profileId"],expected)
            self.assertFalse(x["vendorFirmwareVerified"])
            self.assertFalse(x["firmwareFlashes"])
    def test_unknown_board_is_amber_not_guessed(self):
        x=m.evaluate(facts(boardModel="Pico Pi Zero W 3"),SHA,True)
        self.assertEqual(x["profileId"],"unresolvedHardware")
        self.assertEqual(x["status"],"AMBER_DEVICE_PROOF_REQUIRED")
    def test_reject_secrets_and_network_ids(self):
        with self.assertRaisesRegex(ValueError,"RED_UNEXPECTED"):m.evaluate(dict(facts(),serial="1234"),SHA,True)
        with self.assertRaisesRegex(ValueError,"RED_INTERFACE"):m.evaluate(facts(net=["02:aa:bb:cc:dd:ee"]),SHA,True)
        with self.assertRaisesRegex(ValueError,"RED_INTERFACE"):m.evaluate(facts(net=["wlan0"]),SHA,True)
    def test_fail_exact_source_and_no_mutation(self):
        with self.assertRaisesRegex(ValueError,"RED_SOURCE"):m.evaluate(facts(), "main", True)
        x=m.evaluate(facts(),SHA,True)
        for k in ("diskWrites","bootChanges","firmwareFlashes","networkChanges","agentWorkersActivated"):
            self.assertFalse(x[k],k)
        self.assertEqual(x["crownStatus"],"STOP")
    def test_container_and_branded_routes_are_source_only(self):
        from pathlib import Path
        root=Path(__file__).resolve().parents[1]
        docker=(root/"machine-harness/Dockerfile").read_text()
        compose=(root/"machine-harness/compose.yaml").read_text()
        app=(root/"host/machineHarness/app.py").read_text()
        self.assertIn("USER 10001:10001",docker)
        self.assertIn("127.0.0.1:8765:8765",compose)
        self.assertIn("cap_drop: [ALL]",compose)
        self.assertIn('read_only: true',compose)
        self.assertIn('agents":"QUARANTINED"',app)
        self.assertNotIn("sudo",app)
        self.assertNotIn("fastboot",app)

if __name__ == "__main__": unittest.main()

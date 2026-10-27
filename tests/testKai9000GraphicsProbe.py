"""KAI9000 vendor/ROMhacking graphics toolchain and zero-mutation probe tests."""
import importlib.util
import json
from pathlib import Path
from unittest import TestCase, main
from unittest.mock import patch
import yaml

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("kai9000GraphicsProbe", ROOT / "tools/kai9000GraphicsProbe.py")
probe = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(probe)


class DriverSourceTests(TestCase):
    def test_vendor_reference_and_read_only_policy(self):
        config = yaml.safe_load((ROOT/"doctrine/kai9000RomHackingGraphicsResearchV1.yaml").read_text())
        self.assertEqual(config["schema"], "luhmOs.kai9000RomHackingGraphicsResearch.v1")
        self.assertEqual(config["status"], "SOURCE_CANDIDATE_RESEARCH_ONLY")
        self.assertEqual(config["researchMethod"]["directUtilityCatalogAccess"], "BLOCKED_403")
        self.assertEqual(config["sourceEvidence"]["romPatcherJs"]["adoption"], "REFERENCE_ONLY")
        self.assertEqual(config["sourceEvidence"]["imHex"]["packageIntoPublicApk"], False)
        self.assertEqual(config["samsungDiagnosis"]["firstReadOnlyProbe"], "tools/kai9000GraphicsProbe.py")
        self.assertTrue(config["samsungDiagnosis"]["requiresExactDeviceEvidence"])
        self.assertEqual(config["samsungDiagnosis"]["currentTabletEvidence"], "NOT_CAPTURED")
        self.assertEqual(config["samsungDiagnosis"]["currentPhoneEvidence"], "NOT_CAPTURED")
        for name in ("noKernelFlash", "noOdinFlash", "noUnlockBootloader",
                     "noRootRequired", "noSystemwideAngleSwitch", "noArbitraryGlesDriverInjection"):
            self.assertTrue(config["driverBoundaries"][name], name)
        self.assertTrue(config["driverBoundaries"]["linuxKernelDriversAreNotNpmModules"])
        maintenance = config["userHardwareMaintenanceLaw"]
        for required in ("noHexEditorAsPrerequisite", "noBiosRewriteAsPrerequisite",
                         "noFirmwarePatchingAsPrerequisite", "noOdinRecoveryAsPrerequisite",
                         "neverConvertHistoricalHexHackingExpertiseIntoMaintenanceObligation"):
            self.assertTrue(maintenance[required], required)
        self.assertEqual(maintenance["ifOnlyUnsupportedFirmwareFixRemains"], "STOP_AND_REPORT_UNSUPPORTED")
        self.assertEqual(config["shipping"]["crownStatus"], "STOP")
        self.assertTrue(config["shipping"]["noLiveDeviceMutation"])

    def test_probe_fails_closed_on_command_injection(self):
        for bad in (("shell","sh","-c","getprop"), ("shell","setprop","x","1"),
                    ("install", "a.apk"), ("shell","reboot"), ("-s","serial","shell","getprop","ro.hardware")):
            with self.assertRaisesRegex(ValueError, "RED_ADB_COMMAND_OUTSIDE_READ_ONLY_ALLOWLIST"):
                probe.run_command(bad)

    def test_readonly_inventory_redacts_fingerprint_and_unknown_fields(self):
        calls = []
        def reader(cmd):
            calls.append(cmd)
            if cmd == ("shell","getprop","ro.build.fingerprint"):
                return "Samsung/raw-fingerprint-secret"
            if cmd == ("shell","pm","list","features"):
                return "feature:android.hardware.vulkan.level\nfeature:android.hardware.sensor.camera\nfeature:android.hardware.vulkan.version\n"
            if cmd == ("shell","dumpsys","webviewupdate"):
                return "Current WebView package (name, version): com.google.android.webview 141.0.1\nPrivate line"
            return "SM-X400"
        report = probe.collect(reader)
        packed = json.dumps(report, sort_keys=True)
        self.assertNotIn("Samsung/raw-fingerprint-secret", packed)
        self.assertNotIn("Private line", packed)
        self.assertNotIn("sensor.camera", packed)
        self.assertEqual(report["properties"]["buildFingerprintSha256"].__len__(), 64)
        self.assertEqual(len(calls), len(probe.ALLOWED))
        self.assertTrue(set(calls).issubset(set(probe.ALLOWED)))
        self.assertTrue(report["driverModified"] is False)

    def test_without_probe_performs_no_adb(self):
        with patch.object(probe.subprocess, "run", side_effect=AssertionError("adb should not run")):
            with patch("sys.argv", ["kai9000GraphicsProbe.py"]):
                self.assertEqual(probe.main(), 0)

    def test_subprocess_probed_command_is_exactly_whitelisted(self):
        class Response:
            returncode=0
            stdout="SM-X400\n"
        with patch.object(probe.subprocess, "run", return_value=Response()) as proc:
            self.assertEqual(probe.run_command(("shell","getprop","ro.product.model")), "SM-X400")
            self.assertEqual(proc.call_args.args[0], ["adb","shell","getprop","ro.product.model"])
            self.assertEqual(proc.call_args.kwargs["timeout"], 8)
            self.assertFalse(proc.call_args.kwargs["check"])

if __name__ == "__main__":
    main()

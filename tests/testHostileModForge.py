#!/usr/bin/env python3
"""Fail-closed 4x4 VM/system variables/USB/BT/mods/law source tests."""
from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "hostileModForgeAudit", ROOT / "tools/hostileModForgeAudit.py")
assert spec and spec.loader
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
SHA40 = "f0cb6ee54066b490c0e80efc2c96200fec76ee2d"
SHA64 = "a" * 64
PATCH = {
    "taskId": "homebrewTask", "sourceRef": SHA40, "scopeId": "localStudy",
    "format": "BPS", "inputSha256": "a" * 64,
    "outputSha256": "b" * 64, "patchSha256": "c" * 64,
    "offsetHex": "0x00babe12", "originalRights": "homebrewOwned"
}


class TestHostileModForge(unittest.TestCase):
    def test_4x4_and_rights_no_real_hardware(self):
        result = gate.audit()
        self.assertEqual(result["status"], "SOURCE_CANDIDATE_ONLY", result["issues"])
        self.assertEqual(result["fourByFourCells"], 16)
        self.assertEqual(result["upstreamReferenceCount"], 17)
        self.assertEqual(len(result["registryIdentitySha256"]), 64)
        self.assertFalse(result["actualHostEnvironmentRead"])
        self.assertEqual(result["observedUsbDevices"], 0)
        self.assertEqual(result["forksMade"], 0)
        self.assertEqual(result["patchesApplied"], 0)
        self.assertFalse(result["crownAuthority"])

    def test_safe_source_env_inherited_no_secret_or_real_process_change(self):
        output = gate.environment_plan({"LUHM_STAGE": "testing",
                                        "LUHM_DISPLAY_BACKEND": "wayland",
                                        "LUHM_DEBUG_PROFILE": "redacted"})
        self.assertEqual(output["state"], "SOURCE_FLAGS_ONLY")
        self.assertEqual(output["values"]["LUHM_BLUETOOTH_ENABLED"], "off")
        self.assertFalse(output["hostEnvironmentModified"])
        self.assertFalse(output["hostEnvironmentRead"])
        self.assertFalse(output["workerStarted"])

    def test_unrecognized_env_privilege_and_injection_rejected(self):
        for value in ({"LD_PRELOAD": "./evil.so"},
                      {"DISPLAY": ":0"}, {"LUHM_API_KEY": "secret"},
                      {"GIT_SSH_COMMAND": "sh"}, {"LUHM_DEBUG_PROFILE": "all"},
                      {"LUHM_STAGE": "public"}, {"LUHM_USB_ENABLED": "write"},
                      {"LUHM_UNKNOWN": "test"}):
            with self.subTest(value=value), self.assertRaises(ValueError):
                gate.environment_plan(value)
        with self.assertRaises(ValueError):
            gate.environment_plan({"LUHM_STAGE": None})

    def test_requested_usb_bluetooth_still_requires_actual_os_permission(self):
        x = gate.environment_plan({"LUHM_USB_ENABLED": "readOnly",
                                   "LUHM_BLUETOOTH_ENABLED": "readOnly",
                                   "LUHM_INPUT_MODE": "userAuthorized"})
        self.assertEqual(x["state"], "HOLD_OS_PERMISSION_OR_HOST_RUNTIME")
        self.assertEqual(len(x["blockers"]), 3)
        self.assertFalse(x["deviceOpened"])

    def test_device_hex_and_service_uuid_are_opaque_not_security_approval(self):
        d = gate.device_metadata(transport="usb", vendor_id="0bda", product_id="8153")
        self.assertEqual(len(d["opaqueHashSha256"]), 64)
        self.assertFalse(d["rawSerialOrMacStored"])
        self.assertFalse(d["realDevicePresent"])
        self.assertFalse(d["permissionGranted"])
        bt = gate.device_metadata(transport="bluetooth",
                service_uuid="0000180f-0000-1000-8000-00805f9b34fb")
        self.assertEqual(bt["status"], "UNTRUSTED_IDENTIFIER_ONLY")
        self.assertNotEqual(bt["opaqueHashSha256"], d["opaqueHashSha256"])

    def test_malformed_or_unauthorized_usb_bt_identifiers_rejected(self):
        for pair in [("zzzz", "8153"), ("0BDA", "8153"),
                     ("0bda", "1"), ("0bda", "8153;rm"), ("0bda", "")]:
            with self.subTest(pair=pair), self.assertRaises(ValueError):
                gate.device_metadata(transport="usb",
                                     vendor_id=pair[0], product_id=pair[1])
        with self.assertRaises(ValueError):
            gate.device_metadata(transport="bluetooth",
                                 service_uuid="aa:bb:cc:dd:ee:ff")
        with self.assertRaises(ValueError):
            gate.device_metadata(transport="bluetooth",
                                 service_uuid="0000180F-0000-1000-8000-00805f9b34fb")
        with self.assertRaises(ValueError):
            gate.device_metadata(transport="usb", vendor_id="0bda",
                                 product_id="8153", service_uuid="abc")

    def test_vendor_claims_never_infer_mod_redistribution(self):
        for name, lic in (("godot", "MIT"), ("reshade", "BSD-3-Clause"),
                          ("bodySlide", "GPL-3.0-or-later"),
                          ("duckstation", "CC-BY-NC-ND_CUSTOM_RESTRICTIONS"),
                          ("nexusMods", "unknown")):
            with self.subTest(name=name):
                result = gate.community_candidate(
                    source_id=name, claimed_license=lic, claimed_sha256=SHA64)
                self.assertTrue(result["licenseClaimMatchesResearch"] if
                                lic != "unknown" else not result["licenseClaimMatchesResearch"])
                self.assertFalse(result["mayFork"])
                self.assertFalse(result["mayCopyMedia"])
                self.assertFalse(result["mayInstall"])
                self.assertFalse(result["actualBinaryVerified"])
                self.assertFalse(result["greenAuthority"])
        with self.assertRaises(ValueError):
            gate.community_candidate(source_id="bad", claimed_license="Apache-2.0",
                                     claimed_sha256=SHA64)
        with self.assertRaises(ValueError):
            gate.community_candidate(source_id="godot", claimed_license="MIT",
                                     claimed_sha256="not-a-digest")

    def test_legal_homebrew_patch_hex_metadata_only(self):
        plan = gate.synthetic_patch_plan(PATCH)
        self.assertEqual(plan["state"], "HOLD_LICENSE_AND_USER_SUPPLIED_IMAGE_REVIEW")
        self.assertEqual(plan["offsetHex"], "0x00babe12")
        self.assertFalse(plan["originalRomOpened"])
        self.assertFalse(plan["patchApplied"])
        self.assertFalse(plan["copyProtectionCircumvented"])
        self.assertFalse(plan["filesDownloaded"])

    def test_ROM_contents_urls_and_unknown_rights_are_denied(self):
        for key, value in [("originalRights", "abandonware"),
                           ("originalRights", "downloadedROM"),
                           ("format", "EXE"), ("offsetHex", "-1"),
                           ("offsetHex", "0x123456789"),
                           ("sourceRef", "main"),
                           ("inputSha256", "a" * 63)]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                gate.synthetic_patch_plan({**PATCH, key: value})
        with self.assertRaises(ValueError):
            gate.synthetic_patch_plan({**PATCH, "romBytes": "AAEEFF"})
        with self.assertRaises(ValueError):
            gate.synthetic_patch_plan({**PATCH, "downloadUrl": "https://example.org/rom"})

    def test_forged_source_allows_no_autofork_x11_or_rights(self):
        original = gate.load
        def forged(path):
            data = original(path)
            if path == gate.POLICY:
                data = copy.deepcopy(data)
                data["cells"][2]["states"][1]["mutationAuthorized"] = True
                data["display"]["mayStartXorg"] = True
                data["modding"]["noAutoFork"] = False
                data["licensing"]["noBlanketRelicense"] = False
                data["admission"]["networkRequests"] = 1
            return data
        with patch.object(gate, "load", side_effect=forged):
            result = gate.audit()
        for flag in ("RED_MATRIX_IMPLIED_RUNTIME", "RED_DISPLAY_BACKEND",
                     "RED_MOD_BINARY_BOUNDARY", "RED_LICENSE_RELABEL",
                     "RED_FAKE_RUNTIME_networkRequests"):
            self.assertIn(flag, result["issues"])


if __name__ == "__main__":
    unittest.main()

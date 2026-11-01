#!/usr/bin/env python3
"""Four-family hardware/source/IPS gates: no VM, BIOS, ROM or hardware used."""
from __future__ import annotations
import copy
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "machineFourArchitectureAudit", ROOT / "tools/machineFourArchitectureAudit.py")
assert spec and spec.loader
machine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(machine)
SHA = "f0cb6ee54066b490c0e80efc2c96200fec76ee2d"
BASE = dict(task_id="taskForge", source_ref=SHA, scope_id="machineScope",
            architecture="x86_64", layer="memoryIo", ram_bytes=8*1024**3,
            bus_kind="pciVendorId", bus_hex="8086")


def tiny_ips(offset=0x1234, content=b"AB"):
    return b"PATCH" + offset.to_bytes(3, "big") + len(content).to_bytes(2, "big") + content + b"EOF"


class TestMachineForge(unittest.TestCase):
    def test_source_four_families_four_layers_and_no_runtime(self):
        r = machine.source_audit()
        self.assertEqual(r["state"], "SOURCE_CANDIDATE_ONLY", r["issues"])
        self.assertEqual(r["architectureFamilies"], 4)
        self.assertEqual(r["machineLayers"], 4)
        self.assertEqual(r["matrixCells"], 16)
        self.assertEqual(r["candidateUpstreams"], 14)
        self.assertEqual(r["hardwareDiscovered"], 0)
        self.assertEqual(r["firmwareFlashes"], 0)
        self.assertEqual(r["ipsPatchesApplied"], 0)
        self.assertFalse(r["greenAuthority"])

    def test_arch_matrix_deterministic_numerical_order_not_performance(self):
        for i, arch in enumerate(machine.ARCH):
            for j, layer in enumerate(machine.LAYERS):
                with self.subTest(arch=arch, layer=layer):
                    p = machine.machine_plan(**{**BASE, "architecture": arch, "layer": layer})
                    self.assertEqual(p["machineSortOrdinal"], i * 4 + j)
                    self.assertFalse(p["modelProven"])
                    self.assertFalse(p["memoryMeasured"])
                    self.assertFalse(p["permissionToFlash"])
                    self.assertEqual(p["ramBytesDecimal"], 8589934592)
                    self.assertEqual(p["deviceId"]["valueHex"], "8086")

    def test_hex_sort_uses_fixed_domains_width_numeric_and_byte_order(self):
        pairs = [
            ("usbVendorId", "a", "000a", 16), ("usbProductId", "0bda", "0bda", 16),
            ("pciDeviceId", 4660, "1234", 16),
            ("cpuidLeaf", "1", "00000001", 32),
            ("ipsOffset", "f", "00000f", 24),
            ("uefiGuid", "a" * 32, "a" * 32, 128),
            ("sourceRef", SHA, SHA, 160),
            ("artifactSha256", "f" * 64, "f" * 64, 256)
        ]
        for kind, value, canonical, bits in pairs:
            with self.subTest(kind=kind):
                p = machine.fixed_hex(kind, value)
                self.assertEqual(p["valueHex"], canonical)
                self.assertEqual(p["widthBits"], bits)
                self.assertEqual(p["sortKey"], kind + ":" + canonical)
                self.assertFalse(p["trustedHardwareIdentity"])
        normalized = [machine.fixed_hex("cpuidLeaf", k)["sortKey"]
                      for k in ("0f","01","10")]
        self.assertEqual(sorted(normalized), [
            "cpuidLeaf:00000001", "cpuidLeaf:0000000f", "cpuidLeaf:00000010"])

    def test_hex_rejects_unknown_domain_overflow_bad_endian_string_and_mixed_case(self):
        for kind, value in [
            ("bad","1"),("usbVendorId","0x1234"),("usbVendorId","ABC"),
            ("usbVendorId","10000"),("usbVendorId",-1),
            ("cpuidLeaf",2**32),("ipsOffset","1234567"),
            ("sourceRef","abc"),("artifactSha256","a"*63),
            ("pciVendorId","-1"),("uefiGuid","{deadbeef}"),
            ("usbVendorId", True),
        ]:
            with self.subTest(kind=kind, value=value), self.assertRaises(ValueError):
                machine.fixed_hex(kind,value)

    def test_plan_denies_guesswork_and_malicious_text(self):
        changes=[
            {"source_ref":"main"},{"task_id":"../shadow"},{"scope_id":"scope space"},
            {"architecture":"mips"},{"layer":"biosFlash"},{"ram_bytes":-1},
            {"ram_bytes":True},{"ram_bytes":1<<63},{"bus_kind":"sourceRef"},
            {"bus_hex":"FFFF"},
        ]
        for change in changes:
            with self.subTest(change=change), self.assertRaises(ValueError):
                machine.machine_plan(**{**BASE, **change})

    def test_synthetic_ips_24bit_offsets_and_sha_without_applying(self):
        r=machine.inspect_synthetic_ips(tiny_ips())
        self.assertEqual(r["recordCount"],1)
        self.assertEqual(r["records"][0]["offsetHex"],"0x001234")
        self.assertEqual(r["records"][0]["size"],2)
        self.assertFalse(r["patchBytesReturned"])
        self.assertFalse(r["romOpened"])
        self.assertFalse(r["firmwareImageOpened"])
        self.assertFalse(r["patchApplied"])
        self.assertEqual(len(r["patchSha256"]),64)
        self.assertEqual(machine.inspect_synthetic_ips(b"PATCHEOF")["recordCount"],0)
        rle=b"PATCH"+b"\x00\x01\x02"+b"\x00\x00"+b"\x00\x03"+b"Z"+b"EOF"
        self.assertTrue(machine.inspect_synthetic_ips(rle)["records"][0]["rle"])

    def test_ips_truncation_overlap_extra_content_overflow_rights_rejected(self):
        double=(b"PATCH"+b"\x00\x00\x01"+b"\x00\x02"+b"AA"
                  +b"\x00\x00\x02"+b"\x00\x02"+b"BB"+b"EOF")
        oversized=b"PATCH"+b"\xff\xff\xfe"+b"\x00\x04"+b"ABCD"+b"EOF"
        bad=[
            b"", b"PATCH", b"PATCHEO", b"PATCHEOFX",
            tiny_ips()[:-1], double, oversized,
            b"PATCH"+b"\x00\x01\x00"+b"\x00\x04"+b"A"+b"EOF",
            b"PATCH"+b"\x00\x00\x01"+b"\x00\x00"+b"\x00\x00"+b"A"+b"EOF",
            b"PATCH"+b"\x00\x00\x01"+b"\x00\x00"+b"\x00\x05"+b"EOF",
        ]
        for v in bad:
            with self.subTest(raw=v[:12]), self.assertRaises(ValueError):
                machine.inspect_synthetic_ips(v)
        with self.assertRaises(ValueError):
            machine.inspect_synthetic_ips(tiny_ips(), rights="abandonware")
        with self.assertRaises(ValueError):
            machine.inspect_synthetic_ips(tiny_ips(), asset_class="retailFirmware")

    def test_hostile_source_fails_on_fake_flash_or_changed_bus_width(self):
        base=machine._read
        def forged(path):
            data=base(path)
            if path==machine.POLICY:
                data=copy.deepcopy(data)
                data["matrix4x4"][0]["cells"][0]["flashed"]=True
                data["firmwareRules"]["noFlash"]=False
                data["sort"]["fixedHexNormalization"]["usbVendorId"]["digits"]=8
                data["release"]["noAutoDeploy"]=False
            return data
        with patch.object(machine,"_read",side_effect=forged):
            r=machine.source_audit()
        self.assertIn("RED_MACHINE_PROOF_FABRICATED",r["issues"])
        self.assertIn("RED_MACHINE_FIRMWARE_BYPASS",r["issues"])
        self.assertIn("RED_MACHINE_HEX_WIDTHS",r["issues"])
        self.assertIn("RED_MACHINE_RELEASE_AUTHORITY",r["issues"])


if __name__ == "__main__":
    unittest.main()

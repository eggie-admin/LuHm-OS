#!/usr/bin/env python3
"""Safety and schema tests for the Debian machine-only source snapshot."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from tools import machineDebianSnapshot as m

class DebianFourLayerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline=json.loads(m.CONTRACT.read_text(encoding="utf-8"))

    def testFourByFourSourceReceiptNoFakeHardware(self):
        r=m.snapshot(self.baseline)
        self.assertEqual(r["mode"],"source")
        self.assertEqual(r["verdict"],"AMBER_SOURCE_ONLY")
        self.assertEqual(r["matrixCells"],16)
        self.assertEqual(r["logicalHex"],[f"0x{i:02X}" for i in range(16)])
        self.assertEqual(r["sql"]["db"],"SQLITE_MEMORY_STRICT")
        self.assertEqual(r["sql"]["records"],len(self.baseline["requestedReads"]))
        self.assertTrue(r["machineSnapshotComplete"])
        self.assertFalse(r["runtimeSnapshotComplete"])
        self.assertIsNone(r["hostEvidence"])
        for key in ("physicalDeviceVerified","kernelBuilt","kernelModified",
                    "bootloaderModified","partitionModified","emulatorRun","ffmpegRendered",
                    "actualBackendDeployed"):
            self.assertFalse(r[key])
        self.assertEqual(r["crownStatus"],"STOP")

    def testHexValuesAreAuditCoordinatesOnly(self):
        for mutation in ({"hex":"0xDEADBEEF"}, {"status":"PHYSICAL_GREEN"},
                         {"physicalProof":True}):
            with self.subTest(mutation=mutation):
                b=copy.deepcopy(self.baseline)
                b["matrix"][3].update(mutation)
                with self.assertRaisesRegex(m.MachineAuditError,"MACHINE_LOGICAL_HEX"):
                    m.check_contract(b)

    def testPlatformCannotSelfPromoteKernelFork(self):
        for key,value in (("kernelFork","ENABLED"),("actualKconfigVerified",True),
                          ("driverBindingVerified",True),("sameBinaryAcrossAbis",True)):
            b=copy.deepcopy(self.baseline)
            b["target"][key]=value
            with self.subTest(key=key),self.assertRaisesRegex(m.MachineAuditError,
                                                               "MACHINE_KERNEL_TRUTH"):
                m.check_contract(b)

    def testNoDestructivePrivilegeGateCanBeCleared(self):
        for guard in m.EXPECTED_GUARDS:
            b=copy.deepcopy(self.baseline)
            b["safety"][guard]=False
            with self.subTest(guard=guard), self.assertRaisesRegex(m.MachineAuditError,
                                                                    "MACHINE_PRIVILEGE_BARRIER"):
                m.check_contract(b)

    def testHeadlessDoesNotInheritDesktopAndServers(self):
        b=copy.deepcopy(self.baseline)
        b["profiles"][0]["packages"].append("mariadb-server")
        with self.assertRaisesRegex(m.MachineAuditError,"MACHINE_HEADLESS_VENDOR_FAT"):
            m.check_contract(b)
        b=copy.deepcopy(self.baseline)
        b["optionalDesktops"][1]["default"]=True
        with self.assertRaisesRegex(m.MachineAuditError,"MACHINE_DESKTOP_MINIMUM"):
            m.check_contract(b)

    def testNoGPLProjectOrBiosCopiedIntoMainProduct(self):
        b=copy.deepcopy(self.baseline)
        b["studyOnly"][0]["copyToLuHmCore"]=True
        with self.assertRaisesRegex(m.MachineAuditError,"MACHINE_EMULATOR_POLICY"):
            m.check_contract(b)
        b=copy.deepcopy(self.baseline)
        b["studyOnly"][1]["license"]="Apache-2.0"
        with self.assertRaisesRegex(m.MachineAuditError,"MACHINE_LICENSE_POLICY"):
            m.check_contract(b)

    def testStrictSanitizeFactsRejectSecretsAndFalseIntegers(self):
        for row in ({"serial":"PRIVATE123"},{"kernelRelease":"6.12;rm -rf /"},
                    {"pageBytes":True},{"logicalCpuCount":-1},{"arch":"x"*100},
                    {"distroVersion":"13\nCOOKIE=abc"}):
            with self.subTest(row=row),self.assertRaises(m.MachineAuditError):
                m.sanitize_facts(row)
        good={"system":"Linux","arch":"x86_64","kernelRelease":"6.12.48",
              "distroId":"debian","distroVersion":"13","logicalCpuCount":4,
              "pageBytes":4096,"memTotalBytes":8589934592,
              "memAvailableBytes":4294967296}
        out=m.snapshot(self.baseline,"fixture",good)
        self.assertEqual(out["mode"],"fixture")
        self.assertEqual(out["verdict"],"AMBER_SYNTHETIC_FIXTURE")
        self.assertFalse(out["physicalDeviceVerified"])
        self.assertEqual(out["hostEvidence"]["pageBytes"],4096)

    def testOsReleaseAndMeminfoParseWithoutExecution(self):
        self.assertEqual(m.parse_os_release('ID=debian\nVERSION_ID="13"\nBAD=$(curl evil)'),
                         {"distroId":"debian","distroVersion":"13"})
        result=m.parse_kib_meminfo("MemTotal: 12345 kB\nMemAvailable: 6789 kB\nSerial: secret")
        self.assertEqual(result["memTotalBytes"],12345*1024)
        self.assertEqual(result["memAvailableBytes"],6789*1024)
        self.assertNotIn("Serial",result)

    def testNoSourceSymlinkOrTraversal(self):
        for value in ("../secret","/tmp/absolute","dir\\escape"):
            with self.assertRaises(m.MachineAuditError):
                m.safe_source(m.ROOT,value)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/"item").write_text("test",encoding="utf-8")
            (root/"link").symlink_to("item")
            with self.assertRaisesRegex(m.MachineAuditError,"SOURCE_MISSING_OR_LINK"):
                m.safe_source(root,"link")

    def testHostInventoryNeverCalledInSourceMode(self):
        original=m.host_observe
        try:
            m.host_observe=lambda: (_ for _ in ()).throw(RuntimeError("called host"))
            result=m.snapshot(self.baseline)
            self.assertEqual(result["mode"],"source")
        finally:
            m.host_observe=original

    def testTrustedOfficialReferencesAndStableCellCount(self):
        b=copy.deepcopy(self.baseline)
        b["officialRefs"][0]="https://www.debian.org.evil.example/releases/"
        with self.assertRaisesRegex(m.MachineAuditError,"MACHINE_UPSTREAM_REFS"):
            m.check_contract(b)
        b=copy.deepcopy(self.baseline)
        b["matrix"].pop()
        with self.assertRaisesRegex(m.MachineAuditError,"MACHINE_4X4"):
            m.check_contract(b)

if __name__=="__main__":
    unittest.main()

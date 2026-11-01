#!/usr/bin/env python3
"""Safety negatives for compute-only GPU/CPU/memory/firmware profile."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from tools import computeFourCoreAudit as core

class ComputeFourCoreTests(unittest.TestCase):
    def setUp(self):
        self.policy=json.loads(core.CONTRACT.read_text(encoding="utf8"))
        self.docker=(core.ROOT/self.policy["image"]["path"]).read_text(encoding="utf8")

    def testReadOnlyFourByFourAndServerlessPackages(self):
        r=core.audit(self.policy)
        self.assertEqual(r["matrixCells"],16)
        self.assertEqual(r["computePackages"],11)
        self.assertEqual(r["serverPackages"],0)
        self.assertFalse(r["actualDockerBuild"])
        self.assertFalse(r["physicalGpuTested"])
        self.assertFalse(r["hostMutations"])

    def testNoWebsiteMailOrDatabasePackages(self):
        for pkg in ("nginx","postfix","mariadb-server","dnsmasq","nodejs","certbot"):
            with self.subTest(pkg=pkg):
                tampered=self.docker.replace("blender ffmpeg","blender "+pkg+" ffmpeg")
                with self.assertRaises(core.FourCoreError):
                    core.verify_dockerfile(tampered,self.policy)

    def testRejectPublicPortsAndAutoStart(self):
        for line in ("EXPOSE 80","EXPOSE 443","ENTRYPOINT [\"nginx\"]","CMD [\"nginx\"]","RUN systemctl enable nginx"):
            with self.subTest(line=line),self.assertRaises(core.FourCoreError):
                core.verify_dockerfile(self.docker+"\n"+line+"\n",self.policy)

    def testNoFakedGpuAttestation(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/"dev/dri").mkdir(parents=True)
            (root/"dev/dri/renderD128").touch()
            r=core.runner_probe(root)
            self.assertTrue(r["gpuRenderNodePresentHint"])
            self.assertFalse(r["gpuHardwareAccelerationVerified"])
            self.assertFalse(r["samsungAvbVerified"])

    def testStrictCgroupParsing(self):
        self.assertEqual(core.parse_memory_max("1073741824\n"),1073741824)
        self.assertIsNone(core.parse_memory_max("max\n"))
        for bad in (0,True,"-1","", "0", "garbage","12GiB",str(2**55),"2.5","10"*40):
            with self.subTest(bad=bad),self.assertRaises(core.FourCoreError):
                core.parse_memory_max(bad)

    def testBoundedReadAndMemoryBudget(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            p=root/"sys/fs/cgroup"
            p.mkdir(parents=True)
            (p/"memory.max").write_text("134217728\n",encoding="ascii")
            r=core.runner_probe(root)
            self.assertEqual(r["memoryCgroupLimitBytesHint"],134217728)
            self.assertEqual(r["memoryWorkingSetBytesAdvisory"],33554432)
            self.assertFalse(r["hostSettingsModified"])

    def testNoMemoryLimitDoesNotClaimSafeBudget(self):
        with tempfile.TemporaryDirectory() as d:
            r=core.runner_probe(Path(d))
            self.assertIsNone(r["memoryCgroupLimitBytesHint"])
            self.assertIsNone(r["memoryWorkingSetBytesAdvisory"])

    def testCpuHintsNotPhysicalOrOverclocked(self):
        self.assertEqual(core.advisory_cpu_workers(256),4)
        self.assertEqual(core.advisory_cpu_workers(2),2)
        self.assertIsNone(core.advisory_cpu_workers(None))
        for bad in (True,"4",0,-1,2**30):
            with self.subTest(bad=bad),self.assertRaises(core.FourCoreError):
                core.advisory_cpu_workers(bad)

    def testNoBootChanges(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/"sys/firmware/efi").mkdir(parents=True)
            r=core.runner_probe(root)
            self.assertTrue(r["firmwareEfiDirectoryPresentHint"])
            self.assertFalse(r["uefiFirmwareVerified"])
            self.assertFalse(r["grubInstalledVerified"])

    def testNoMutationClaims(self):
        for flag in ("biosChange","grubChange","cpuGovernorChange","memoryClockChange","gpuDriverInstall",
                     "dmaOrKernelModuleLoad","agentActivated","networkListener"):
            with self.subTest(flag=flag):
                s=copy.deepcopy(self.policy)
                s["runtime"][flag]=True
                with self.assertRaisesRegex(core.FourCoreError,"FALSE_DEVICE_OR_TUNING_CLAIM"):
                    core.audit(s)

    def testNoClaimedDockerBuild(self):
        s=copy.deepcopy(self.policy)
        s["image"]["actualImageBuilt"]=True
        with self.assertRaisesRegex(core.FourCoreError,"IMAGE_FALSE_RUNTIME"):
            core.audit(s)

    def testNoExtraCapabilitiesByDoctrineChange(self):
        s=copy.deepcopy(self.policy)
        s["notRequired"].remove("mailServer")
        with self.assertRaisesRegex(core.FourCoreError,"SERVICE_SCOPE_CREEP"):
            core.audit(s)

    def testRejectMissingGodotIntegrity(self):
        with self.assertRaisesRegex(core.FourCoreError,"GODOT_PIN_DRIFT"):
            core.verify_dockerfile(self.docker.replace("sha256sum --check","sha256sum --help"),self.policy)

    def testNoLiveProbeToTestContract(self):
        with mock.patch.object(core,"runner_probe",side_effect=AssertionError("host probe forbidden")):
            r=core.audit(self.policy)
            self.assertEqual(r["status"],"AMBER_SOURCE_ONLY")

if __name__=="__main__":
    unittest.main()

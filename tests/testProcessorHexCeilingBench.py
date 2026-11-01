#!/usr/bin/env python3
"""No root, no network, no hardware mutation. Verify byte-ceiling and boot boundaries."""
import copy
import hashlib
import json
import unittest
from tools import processorHexCeilingBench as bench

class ProcessorHexCeilingTests(unittest.TestCase):
    def setUp(self):
        self.policy=json.loads(bench.CONTRACT.read_text(encoding="utf-8"))

    def test16SourceRoutesAndUnchangedKernelBoundary(self):
        receipt=bench.validate(self.policy)
        self.assertEqual(receipt["sourceRoutes"],16)
        self.assertEqual(receipt["status"],"AMBER_SOURCE_ONLY")
        self.assertFalse(receipt["runnerBenchmarked"])
        self.assertFalse(receipt["kernelMutations"])
        self.assertFalse(receipt["androidDeviceBenchmarked"])

    def testByteLadderExactlyFourK64KOneMiB(self):
        self.assertEqual(bench.SIZES,(4096,65536,1048576))
        self.assertEqual([f"0x{s:06X}" for s in bench.SIZES],
                         ["0x001000","0x010000","0x100000"])
        for size in (0,1,2048,1048577,4*1024*1024,True,1.5,"4096"):
            with self.subTest(size=size),self.assertRaises(bench.ProcessorCeilingError):
                bench.synthetic_payload(size)

    def testExactSyntheticDigestAndBoundedSample(self):
        for size in bench.SIZES:
            with self.subTest(size=size):
                payload=bench.synthetic_payload(size)
                self.assertEqual(len(payload),size)
                self.assertEqual(hashlib.sha256(payload).hexdigest(),hashlib.sha256(bench.synthetic_payload(size)).hexdigest())

    def testRealRunnerMicrobenchIsAdvisory(self):
        result=bench.measure_synthetic()
        self.assertEqual(len(result["observedScores"]),3)
        self.assertTrue(result["advisoryOnly"])
        self.assertTrue(result["repeatabilityUnproven"])
        self.assertIn(result["bestObservedChunkBytes"],bench.SIZES)
        for score in result["observedScores"]:
            self.assertEqual(score["sampleCount"],3)
            self.assertEqual(score["payloadBytes"],1048576)
            self.assertGreaterEqual(score["medianDurationNs"],1)
            self.assertGreaterEqual(score["estimatedMiBPerSecond"],0)

    def testCannotInflateSamplesOrSizes(self):
        for sizes,reps in (((4096,),3),((4096,65536,2097152),3),(bench.SIZES,4),(bench.SIZES,True)):
            with self.subTest(sizes=sizes,reps=reps),self.assertRaises(bench.ProcessorCeilingError):
                bench.measure_synthetic(sizes,reps)

    def testWorkerCapNeverOverSubscribes(self):
        self.assertEqual(bench.select_worker_ceiling(1),1)
        self.assertEqual(bench.select_worker_ceiling(2),2)
        self.assertEqual(bench.select_worker_ceiling(256),4)
        for value in (0,-1,True,3.5,"4"):
            with self.subTest(value=value),self.assertRaises(bench.ProcessorCeilingError):
                bench.select_worker_ceiling(value)

    def testAndroidHasNoGrub(self):
        bad=copy.deepcopy(self.policy)
        bad["platforms"]["androidSamsung"]["grubMayBeUsed"]=True
        with self.assertRaisesRegex(bench.ProcessorCeilingError,"BOOT_CHAIN_CONFLATION"):
            bench.validate(bad)

    def testNeverWriteCpuGovernorOrGrub(self):
        for key in ("clockGovernorChange","ramFrequencyChange","irqAffinityChange","socketBufferSet","threadsSpawned"):
            with self.subTest(key=key):
                bad=copy.deepcopy(self.policy)
                bad["optimization"][key]=True
                with self.assertRaisesRegex(bench.ProcessorCeilingError,"SYSTEM_TUNING_NOT_AUTHORIZED"):
                    bench.validate(bad)
        bad=copy.deepcopy(self.policy)
        bad["platforms"]["pcLinux"]["bootWriteAuthorized"]=True
        with self.assertRaisesRegex(bench.ProcessorCeilingError,"BOOT_WRITE_AUTHORITY"):
            bench.validate(bad)

    def testNoPhysicalDeviceOrKernelProofFromRunner(self):
        for key,value in (("physicalDeviceVerified",True),("hostKernelModified",True),
                          ("anySystemSettingsChanged",True),("workersActive",4)):
            with self.subTest(key=key):
                bad=copy.deepcopy(self.policy)
                bad[key]=value
                with self.assertRaises(bench.ProcessorCeilingError):
                    bench.validate(bad)

    def test16CellCoordinatesAreUnique(self):
        addresses=[row["address"] for row in self.policy["matrix"]]
        self.assertEqual(addresses,[f"0x{i:02X}" for i in range(16)])
        bad=copy.deepcopy(self.policy)
        bad["matrix"][15]["address"]="0xA0"
        with self.assertRaisesRegex(bench.ProcessorCeilingError,"FOUR_BY_FOUR_CELL"):
            bench.validate(bad)

    def testNoFalseCpuThrottleOrQuotaClaim(self):
        facts=bench.observed_cpu_context()
        self.assertFalse(facts["actualClockFrequencyProven"])
        self.assertFalse(facts["physicalCoreCountProven"])
        self.assertFalse(facts["cgroupQuotaProven"])
        self.assertFalse(facts["kernelGovernorChanged"])

if __name__=="__main__":
    unittest.main()

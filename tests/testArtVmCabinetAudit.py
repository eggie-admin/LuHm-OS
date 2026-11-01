#!/usr/bin/env python3
"""Adversarial source-only LuHm art VM cabinet checks."""
import copy
import json
import unittest
from tools import artVmCabinetAudit as a

class ArtVmCabinetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = json.loads(a.CONTRACT.read_text(encoding="utf-8"))

    def testSafeFourByFourAndNoWorkerActivation(self):
        r = a.audit(self.model)
        self.assertEqual(r["cells"], 16)
        self.assertEqual(r["warningsHistorical"], 4)
        self.assertEqual(r["skillBindingsVerified"], 3)
        self.assertTrue(r["sourceOnly"])
        self.assertFalse(r["actualArtVmStarted"])
        self.assertFalse(r["workerActivated"])
        self.assertFalse(r["firmwareMutated"])
        self.assertEqual(r["crownStatus"], "STOP")

    def testHexNotPhysicalRegisters(self):
        m = copy.deepcopy(self.model)
        m["matrix"][8]["hex"] = "0xDEADBEEF"
        with self.assertRaisesRegex(a.CabinetAuditError, "4X4_LOGICAL_HEX_OR_PROOF"):
            a.audit(m)

    def testNoUnprovenIosVmOrSamsungBootWrite(self):
        for i, field, value in ((2,"execution","bootLinuxGuest"),
                                (1,"firmware","unlockedBootloader"),
                                (0,"firmware","guestControlled")):
            with self.subTest(surface=i):
                m=copy.deepcopy(self.model)
                m["surfaces"][i][field]=value
                with self.assertRaises(a.CabinetAuditError):
                    a.audit(m)

    def testSourceGitShaIsNotSha256(self):
        m=copy.deepcopy(self.model)
        m["historicalWarnings"][1]["sourceSha"]="a"*64
        with self.assertRaisesRegex(a.CabinetAuditError,"HISTORICAL_SOURCE_IDENTITY"):
            a.audit(m)

    def testNoHistoricalLogDropped(self):
        m=copy.deepcopy(self.model)
        m["historicalWarnings"].pop()
        with self.assertRaisesRegex(a.CabinetAuditError,"HISTORICAL_LOG_ORDER"):
            a.audit(m)

    def testNoAgentOrDevicePromotion(self):
        for field in ("agentWorkerReleased","physicalSamsungProven","googleGpuVmStarted",
                      "actualDockerComputeImageBuilt","iosVmSupportedAsGeneralGuest"):
            with self.subTest(field=field):
                m=copy.deepcopy(self.model)
                m["sourceObservations"][field]=True
                with self.assertRaisesRegex(a.CabinetAuditError,"FALSE_DEVICE_OR_AGENT_PROOF"):
                    a.audit(m)

    def testNoPrivilegeOrPublicationExpansion(self):
        for field in ("noSelfApproval","noHiddenAsync","noAdditionalVendorServices"):
            m=copy.deepcopy(self.model)
            m[field]=False
            with self.subTest(field=field),self.assertRaisesRegex(a.CabinetAuditError,
                                                                  "REQUIRED_SAFETY_GUARD"):
                a.audit(m)
        m=copy.deepcopy(self.model)
        m["allowedMutations"].append("productionMerge")
        with self.assertRaisesRegex(a.CabinetAuditError,"MUTATION_AUTHORITY_ESCALATION"):
            a.audit(m)

    def testNoStaleOrArbitraryOfficialDocs(self):
        m=copy.deepcopy(self.model)
        m["referenceDocs"][0]["url"]="https://docs.cloud.google.com.evil.invalid/"
        with self.assertRaisesRegex(a.CabinetAuditError,"UNTRUSTED_REFERENCE_URL"):
            a.audit(m)

    def testNoFileTraversal(self):
        for path in ("../secret.json", "/tmp/secret.json"):
            with self.assertRaises(a.CabinetAuditError):
                a.verified_file(a.ROOT,path)

if __name__ == "__main__":
    unittest.main()

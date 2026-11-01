#!/usr/bin/env python3
"""Negative controls: CAST industry comparison stays advisory and fails closed."""
import copy
import json
import unittest
from tools import castIndustryArchitectureAudit as a

class IndustryArchitectureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = json.loads(a.CONTRACT.read_text(encoding="utf-8"))

    def testCanonicalFourByFourAndLifecycle(self):
        r = a.audit(self.base)
        self.assertEqual(r["platforms"],4)
        self.assertEqual(r["matrixCells"],16)
        self.assertEqual(r["functionClasses"],4)
        self.assertIn("Python 3.10",r["observedExpired"])
        self.assertFalse(r["softwareInstalled"])
        self.assertEqual(r["crownStatus"],"STOP")

    def testHexMustStayLogicalAndContiguous(self):
        c=copy.deepcopy(self.base)
        c["matrix"][7]["hex"]="0xDEADBEEF"
        with self.assertRaisesRegex(a.IndustryAuditError,"MATRIX_HEX_IDENTITY"):
            a.audit(c)

    def testBootDiskRequiresSeparationAndBackup(self):
        for tool,field in (("grub","androidBootAllowed"),("gparted","needsBackup")):
            c=copy.deepcopy(self.base)
            for item in c["tools"]:
                if item["id"]==tool:
                    item[field]=not item[field]
            with self.assertRaises(a.IndustryAuditError):
                a.audit(c)

    def testNoCodeCannotAddNewUnreviewedVendor(self):
        c=copy.deepcopy(self.base)
        next(x for x in c["tools"] if x["id"]=="n8n")["state"]="ADOPT_EXISTING"
        with self.assertRaisesRegex(a.IndustryAuditError,"NO_CODE_VENDOR_BOUNDARY"):
            a.audit(c)

    def testMissingProvenanceAndEolAreBlocked(self):
        for field,value in (("source","http://evil.example"),("decision","SUPPORTED_CANDIDATE")):
            c=copy.deepcopy(self.base)
            c["lifecycle"][0][field]=value
            with self.assertRaises(a.IndustryAuditError):
                a.audit(c)

    def testNoHostMutationOrFalseHardwareProof(self):
        for key in self.base["limits"]:
            c=copy.deepcopy(self.base)
            c["limits"][key]=False
            with self.subTest(key=key),self.assertRaisesRegex(a.IndustryAuditError,"MUTATION_BARRIER_REMOVED"):
                a.audit(c)

    def testRejectUntrustedDocsAndLostReviewGate(self):
        c=copy.deepcopy(self.base)
        c["tools"][0]["doc"]="https://github.com.evil.example/unsafe"
        with self.assertRaisesRegex(a.IndustryAuditError,"TOOLS_UNTRUSTED_DOCS"):
            a.audit(c)
        c=copy.deepcopy(self.base)
        c["reviewGates"].remove("androidNative16KiBPageAlignment")
        with self.assertRaisesRegex(a.IndustryAuditError,"MISSING_RELEASE_REVIEW_GATES"):
            a.audit(c)

if __name__=="__main__":
    unittest.main()

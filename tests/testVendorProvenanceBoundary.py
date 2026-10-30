#!/usr/bin/env python3
"""Vendor provenance mutation negatives; no network, package installs or device IO."""
import copy
import importlib.util
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m
import sys
sys.path.insert(0,str(ROOT/"tools"))
v=load("vendorProvenanceBoundaryAudit","tools/vendorProvenanceBoundaryAudit.py")
z=load("zipInteropAudit","tools/zipInteropAudit.py")

class ProvenanceBoundaryTests(unittest.TestCase):
    def setUp(self):self.p=v.load()
    def test_original_source_contract(self):
        self.assertEqual(v.check(self.p),[])
        self.assertEqual(len(self.p["vendorRows"]),16)
        self.assertEqual(len(self.p["firstPartyCandidates"]),3)
    def test_no_first_party_apache_without_proof(self):
        p=copy.deepcopy(self.p)
        p["firstPartyCandidates"][0]["apacheReleaseEligible"]=True
        self.assertIn("NO_UNPROVEN_APACHE_ELIGIBILITY:portableZipPolicy",v.check(p))
    def test_no_vendor_source_copy(self):
        p=copy.deepcopy(self.p)
        p["vendorRows"][2]["sourceFilesCopied"]=True
        self.assertIn("NO_THIRD_PARTY_COPY:firefoxGeckoView",v.check(p))
    def test_no_runtime_fabrication(self):
        p=copy.deepcopy(self.p)
        p["devices"]["remoteVmHealth"]="GREEN"
        self.assertIn("DEVICE_RUNTIME_NOT_PROVEN",v.check(p))
    def test_base44_is_not_encoding(self):
        p=copy.deepcopy(self.p)
        p["transport"]["base44IsEncoding"]=True
        self.assertIn("ENCODING_AND_EDGE",v.check(p))
    def test_no_cloud_or_agent(self):
        p=copy.deepcopy(self.p)
        p["ai"]["activeAgents"]=1
        p["approvals"]["cloudProvision"]=True
        e=v.check(p)
        self.assertIn("LUM_QUARANTINE",e)
        self.assertIn("NO_UNATTENDED_ACTION",e)
    def test_java_entry_sha_not_claimed(self):
        p=copy.deepcopy(self.p)
        p["artifactContract"]["javaPerFileSha256Verification"]=True
        self.assertIn("NO_FALSE_JAVA_APK_PROOF",v.check(p))
    def test_zip_portable_paths(self):
        for bad in ("luhmos-dev/CON.txt","luhmos-dev/a.txt:stream",
                    "luhmos-dev/dir/a.","luhmos-dev/é.txt"):
            with self.subTest(bad=bad):self.assertFalse(z.portable_name(bad))
        self.assertTrue(z.portable_name("luhmos-dev/host/api/k9000HeadlessCore.py"))
    def test_no_license_swap(self):
        p=copy.deepcopy(self.p)
        p["repository"]["relicenseThirdParty"]=True
        self.assertIn("LICENSE_HOLD",v.check(p))
    def test_samsung_native_dex_not_claimed(self):
        p=copy.deepcopy(self.p)
        p["devices"]["samsungLiteNativeDex"]=True
        self.assertIn("DEVICE_SAFETY",v.check(p))
    def test_source_ref_exact(self):
        self.assertRegex(v.source_ref(),r"^[a-f0-9]{40}$")

if __name__=="__main__":
    unittest.main()

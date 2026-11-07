#!/usr/bin/env python3
"""No build or remote changes; verify proposed four-package encapsulation gates."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from fourTargetPluginEncapsulationAudit import audit

class FourTargetPluginEncapsulationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads((ROOT / "doctrine/fourTargetPluginEncapsulationV1.json").read_text())
        cls.source = json.loads((ROOT / "doctrine/currentSourceTruthV3.json").read_text())
        cls.remote = json.loads((ROOT / "doctrine/selfHostedRemoteUpdatesV1.json").read_text())
        cls.stable = json.loads((ROOT / "doctrine/stablePluginUpdateSpineV1.json").read_text())

    def problems(self, mutated=None):
        return audit(copy.deepcopy(self.doc if mutated is None else mutated),
                     self.source, self.remote, self.stable)

    def test_current_candidate_passes_source_contract(self):
        self.assertEqual(self.problems(), [])

    def test_four_native_artifact_families(self):
        by_id = {row["id"]: row for row in self.doc["fourBuildFamilies"]}
        self.assertEqual(set(by_id), {"androidSamsung","iosIphone","linuxDesktop","windowsDesktop"})
        self.assertTrue(all("requiredProof" in row for row in by_id.values()))

    def test_cannot_claim_ipa_is_apk(self):
        changed = copy.deepcopy(self.doc)
        changed["fourBuildFamilies"][1]["packageBeta"] = "android.apk"
        self.assertIn("IOS_BUILD_PROOF_DRIFT", self.problems(changed))

    def test_cannot_erase_pi_target(self):
        changed = copy.deepcopy(self.doc)
        changed["fourBuildFamilies"][2]["target"] = "Linux x86_64"
        self.assertIn("PI_ARM64_PACKAGING_MISSING", self.problems(changed))

    def test_cannot_reclassify_private_pack_as_published(self):
        changed = copy.deepcopy(self.doc)
        changed["defaultAssets"]["rightsStatus"] = "PUBLIC_APPROVED"
        self.assertIn("ART_RIGHTS_OR_RUNTIME_GREEN_FABRICATION", self.problems(changed))

    def test_cannot_drop_baseline_fallback(self):
        changed = copy.deepcopy(self.doc)
        changed["defaultAssets"]["requiredBaselineClasses"].remove("fallbackCopy")
        self.assertIn("OFFLINE_DEFAULTS_MISSING", self.problems(changed))

    def test_cannot_add_remote_executable_loader(self):
        changed = copy.deepcopy(self.doc)
        changed["remoteUpdate"]["clientMayNotLoadExecutableCodeFromManifest"] = False
        self.assertIn("REMOTE_EXECUTION_OR_INSTALL_BYPASS", self.problems(changed))

    def test_cannot_auto_install_binaries(self):
        changed = copy.deepcopy(self.doc)
        changed["remoteUpdate"]["clientMayNotAutoInstallApkIpaLinuxOrWindowsBinaries"] = False
        self.assertIn("REMOTE_EXECUTION_OR_INSTALL_BYPASS", self.problems(changed))

    def test_cannot_fake_live_plugin_mutation(self):
        changed = copy.deepcopy(self.doc)
        changed["boundary"]["privateSiteBackendChanged"] = True
        self.assertIn("RUNTIME_OR_CROWN_FALSE_CLAIM", self.problems(changed))

    def test_release_lanes_are_gated(self):
        changed = copy.deepcopy(self.doc)
        changed["deliveryLanes"][-1]["publication"] = True
        self.assertIn("UNAUTHORIZED_PUBLICATION", self.problems(changed))

if __name__ == "__main__":
    unittest.main()

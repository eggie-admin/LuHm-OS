import copy
import json
import tempfile
import unittest
from pathlib import Path
from tools.communityForkChannelAudit import evaluate, ROOT, POLICY

class ForkChannelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy = json.loads((ROOT / POLICY).read_text(encoding="utf8"))

    def check_fault(self, transform, code):
        p = copy.deepcopy(self.policy)
        transform(p)
        self.assertIn(code, evaluate(p))

    def test_live_policy_source_only(self):
        self.assertEqual(evaluate(self.policy), [])

    def test_isolated_jquery_pin_removed_but_legacy_retained(self):
        pins = {(p["manifest"],p["name"]) for p in self.policy["vendorPins"]}
        self.assertNotIn(("frontEnd/prototypes/glassWorld/package.json","jquery"),pins)
        self.assertIn(("frontEnd/package.json","jquery"),pins)

    def test_no_automatic_vendor_forks(self):
        self.check_fault(lambda p: p.update(autoForkVendors=True), "UNSAFE_autoForkVendors")

    def test_release_requires_separate_evidence(self):
        self.check_fault(lambda p: p["channels"][1].update(publication="PUBLISHED"), "RELEASE_LANE_BYPASS")

    def test_no_fake_signer(self):
        self.check_fault(lambda p: p["channels"][1].update(signerVerified=True), "FALSE_SIGNING_PROOF")

    def test_no_unsafe_custom_nodes(self):
        self.check_fault(lambda p: p["optionalVendors"][0].update(customNodeExecutionAllowed=True),
                         "OPTIONAL_UNTRUSTED_EXECUTION")

    def test_no_unknown_license_as_approved(self):
        self.check_fault(lambda p: p.update(upstreamLicensesIndividuallyVerified=True),
                         "FALSE_PROOF_upstreamLicensesIndividuallyVerified")

    def test_pin_drift_is_detected(self):
        self.check_fault(lambda p: p["vendorPins"][0].update(version="999.0.0"), "NPM_PIN_DRIFT:jquery")

    def test_no_path_traversal(self):
        self.check_fault(lambda p: p["vendorPins"][0].update(manifest="../secret"),
                         "MANIFEST_PATH_ESCAPE")

    def test_no_fake_forks(self):
        self.check_fault(lambda p: p.update(vendorForksCreated=11), "FAKE_FORKS")

    def test_limited_exact_manifests(self):
        self.check_fault(lambda p: p["vendorPins"][0].update(version="^3.7.1"), "NONEXACT_PIN:('frontEnd/package.json', 'jquery', 'npm')")

if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Negative controls for the manually reviewed beta upgrade baseline."""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("betaBaseline", ROOT / "tools/checkBetaReleaseBaseline.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
CERT = "a" * 64
PRIOR_HASH = "b" * 64


class BetaBaselineTests(unittest.TestCase):
    def base(self):
        return {
            "schema": "luhmOs.androidBetaReleaseBaseline.v1",
            "status": "VERIFIED_PREVIOUS_BETA",
            "applicationId": "art.eggiebagelface.luhmos.beta",
            "initialReleaseApproved": False,
            "previousVersionCode": 200500,
            "previousSignerCertificateSha256": CERT,
            "previousApkSha256": PRIOR_HASH,
            "evidenceRef": "github-release-or-signed-artifact-evidence"
        }

    def test_prior_update(self):
        self.assertEqual(module.check(self.base(), 200501, CERT)["nextVersionCode"], 200501)

    def test_refuse_downgrade_and_same_version(self):
        for code in (200499, 200500):
            with self.subTest(code=code), self.assertRaisesRegex(ValueError, "non_monotonic"):
                module.check(self.base(), code, CERT)

    def test_refuse_signer_rotation(self):
        with self.assertRaisesRegex(ValueError, "signer_mismatch"):
            module.check(self.base(), 200501, "c" * 64)

    def test_refuse_missing_proof(self):
        rec = self.base()
        rec["evidenceRef"] = None
        with self.assertRaisesRegex(ValueError, "evidence_ref"):
            module.check(rec, 200501, CERT)

    def test_refuse_missing_prior_apk_hash(self):
        rec = self.base()
        rec["previousApkSha256"] = None
        with self.assertRaisesRegex(ValueError, "prior_apk_hash"):
            module.check(rec, 200501, CERT)

    def test_refuse_unverified_default(self):
        rec = self.base()
        rec["status"] = "UNVERIFIED"
        with self.assertRaisesRegex(ValueError, "unverified"):
            module.check(rec, 200501, CERT)

    def test_first_release_requires_explicit_owner_review(self):
        rec = self.base()
        rec.update(status="VERIFIED_FIRST_BETA", initialReleaseApproved=True,
                   previousVersionCode=None, previousSignerCertificateSha256=None,
                   previousApkSha256=None)
        self.assertEqual(module.check(rec, 200001, CERT)["historyStatus"], "VERIFIED_FIRST_BETA")
        rec["initialReleaseApproved"] = False
        with self.assertRaisesRegex(ValueError, "owner_approval"):
            module.check(rec, 200001, CERT)


if __name__ == "__main__":
    unittest.main(verbosity=2)

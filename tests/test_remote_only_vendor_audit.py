import tempfile
import unittest
from pathlib import Path
from tools.remote_only_vendor_audit import audit

class RemoteOnlyAuditTests(unittest.TestCase):
    def test_repo_report_never_claims_deploy(self):
        result = audit()
        self.assertEqual(result["status"], "SOURCE_ONLY_NO_DEPLOY")
        self.assertFalse(result["remoteExecutionVerified"])
        self.assertFalse(result["oneAppRuntimeVerified"])
        self.assertTrue(result["sourceLicensesMustBeAudited"])
        self.assertEqual(result["canonicalRepository"], "eggie-admin/LuHm-OS")

    def test_missing_files_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            result = audit(Path(d))
            self.assertEqual(result["status"], "BLOCKED")
            self.assertTrue(result["missing"])

if __name__ == "__main__":
    unittest.main()

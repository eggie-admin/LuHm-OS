"""Fail closed on weakened source-policy, leaked keys or workflow privilege."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from deepDungeonSecurityAudit import inspect, scan_added_patch


class DeepDungeonSecurityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy_path=ROOT/"doctrine/dataProtectionLadderV1.json"

    def test_policy(self):
        self.assertEqual(inspect()["failedCategories"],[])

    def test_reject_private_key(self):
        self.assertIn("private_key_material",scan_added_patch("diff --git a/a.txt b/a.txt\n+++ b/a.txt\n+-----BEGIN PRIVATE KEY-----"))

    def test_reject_private_file(self):
        self.assertIn("private_file_added",scan_added_patch("diff --git a/a b/folder/keys.p12\n+++ b/folder/keys.p12\n+dummy"))

    def test_reject_github_token(self):
        value="ghp_"+"x"*36
        self.assertEqual(scan_added_patch("diff --git a/foo b/foo\n+++ b/foo\n+token="+value),["github_token"])

    def test_reject_unsafe_trigger(self):
        patch="diff --git a/.github/workflows/x.yml b/.github/workflows/x.yml\n+++ b/.github/workflows/x.yml\n+pull_request_target:\n"
        self.assertIn("unsafe_workflow_trigger_or_permission",scan_added_patch(patch))

    def test_reject_write_all(self):
        patch="diff --git a/.github/workflows/x.yml b/.github/workflows/x.yml\n+++ b/.github/workflows/x.yml\n+permissions: write-all\n"
        self.assertIn("unsafe_workflow_trigger_or_permission",scan_added_patch(patch))

    def test_ignore_deleted_secret(self):
        self.assertEqual(scan_added_patch("diff --git a/foo b/foo\n--- a/foo\n+++ b/foo\n-ghp_"+"x"*36),[])

    def test_harmless_readme(self):
        self.assertEqual(scan_added_patch("diff --git a/README.md b/README.md\n+++ b/README.md\n+Never commit API keys.\n"),[])

    def test_disallow_weak_crypto_policy(self):
        policy=json.loads(self.policy_path.read_text(encoding="utf-8"))
        self.assertEqual(policy["classes"]["restrictedPersonal"]["localAtRest"],"ENCRYPTED_STORAGE_AND_ACCESS_CONTROL_REQUIRED")

    def test_public_release_not_authorized(self):
        policy=json.loads(self.policy_path.read_text(encoding="utf-8"))
        self.assertFalse(policy["brandRelease"]["publicPublish"])
        self.assertFalse(policy["privacy"]["permissionMutationAuthorized"])
        self.assertEqual(policy["crownStatus"],"STOP")


if __name__=="__main__":
    unittest.main()

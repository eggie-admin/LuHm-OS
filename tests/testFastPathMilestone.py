"""Fast-path milestone test: no fake protected merge, host, or active agents."""
from __future__ import annotations
import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("fastPath", ROOT / "tools/fastPathMilestone.py")
fast = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fast)
SHA = "a" * 40


def fixture():
    snapshot = {
        "main": {"protected": False, "commit": {"sha": "b" * 40}},
        "ruleset": {"id": 25699963, "enforcement": "active",
                    "conditions": {"ref_name": {"include": ["refs/heads/main"]}}, "rules": []},
        "pr": {"number": 386, "state": "open", "merged": False,
               "head": {"sha": SHA}, "base": {"ref": "main"}},
        "checks": {
            "verifiedCommit": SHA, "check_runs": [
                {"app": {"slug": "github-actions"}, "status": "completed", "conclusion": "success"},
                {"app": {"slug": "github-actions"}, "status": "completed", "conclusion": "skipped"},
                {"app": {"slug": "cloudflare-workers-and-pages"}, "status": "completed", "conclusion": "failure"},
            ],
        },
    }
    hold = {
        "schema": "luhmOs.companyWideOperationalQuarantine.v1",
        "state": "QUARANTINED", "activeTaskWorkersAllowed": False,
        "registeredCount": 15, "crownStatus": "STOP",
    }
    return snapshot, hold


def protect(snapshot):
    snapshot["main"]["protected"] = True
    snapshot["ruleset"]["rules"] = [
        {"type": name} for name in ("pull_request", "non_fast_forward", "deletion")
    ]


class FastPathMilestoneTests(unittest.TestCase):
    def report(self, snapshot=None, policy=None):
        s, p = fixture()
        return fast.reconcile(snapshot or s, policy or p, source_ref=SHA)

    def test_real_unprotected_main_is_hard_blocker(self):
        result = self.report()
        self.assertEqual(result["stage"], "P0_ADMIN_GATE")
        self.assertEqual(result["oneNextAction"], "RESTORE_MAIN_PROTECTION_RULESET_25699963")
        self.assertFalse(result["executionAuthorized"])
        self.assertEqual(result["modelWorkersStarted"], 0)
        self.assertFalse(result["agentReleaseAuthorized"])

    def test_missing_admin_api_is_unknown_not_proven_unprotected(self):
        s, p = fixture()
        s["ruleset"] = {}
        self.assertEqual(self.report(s, p)["stage"], "P0_ADMIN_VERIFY")

    def test_fake_boolean_protection_without_rules_denied(self):
        s, p = fixture()
        s["main"]["protected"] = True
        self.assertEqual(self.report(s, p)["stage"], "P0_ADMIN_GATE")

    def test_readiness_is_exact_ci_and_protected_review(self):
        s, p = fixture()
        protect(s)
        self.assertEqual(self.report(s, p)["stage"], "P1_MERGE_GATE")
        s["checks"]["check_runs"][0]["conclusion"] = "failure"
        self.assertEqual(self.report(s, p)["stage"], "P1_CI_GATE")

    def test_source_drift_denied(self):
        s, p = fixture()
        protect(s)
        s["pr"]["head"]["sha"] = "c" * 40
        self.assertEqual(self.report(s, p)["stage"], "P1_SOURCE_GATE")

    def test_pending_ci_never_green(self):
        s, p = fixture()
        protect(s)
        s["checks"]["check_runs"][0]["status"] = "in_progress"
        self.assertEqual(self.report(s, p)["stage"], "P1_CI_GATE")

    def test_merge_only_advances_to_real_host_proof(self):
        s, p = fixture()
        protect(s)
        s["pr"].update(state="closed", merged=True, merge_commit_sha="d" * 40)
        result = self.report(s, p)
        self.assertEqual(result["stage"], "P2_HOST_GATE")
        self.assertEqual(result["facts"]["hostInstalled"], "UNKNOWN_NOT_READ_FROM_CI")
        self.assertEqual(result["facts"]["agentActivation"], "NOT_AUTHORIZED")
        self.assertTrue(result["facts"]["externalBuildRed"])

    def test_fake_host_value_has_no_authority(self):
        s, p = fixture()
        protect(s)
        s["pr"].update(state="closed", merged=True, merge_commit_sha="d" * 40)
        s["hostInstalled"] = True
        self.assertEqual(self.report(s, p)["stage"], "P2_HOST_GATE")

    def test_quarantine_drift_stops_all_progress(self):
        s, p = fixture()
        protect(s)
        p["activeTaskWorkersAllowed"] = True
        self.assertEqual(self.report(s, p)["stage"], "POLICY_DRIFT_STOP")

    def test_bad_source_never_claims_milestone(self):
        s, p = fixture()
        with self.assertRaisesRegex(ValueError, "sourceRef"):
            fast.reconcile(s, p, source_ref="main")


if __name__ == "__main__":
    unittest.main()

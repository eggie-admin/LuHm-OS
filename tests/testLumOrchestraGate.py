"""Fail-closed Lum orchestra tests: passing source tests never imply deployment."""
import importlib.util
import json
import unittest
from unittest.mock import patch
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "tools/lumOrchestraGate.py"
spec = importlib.util.spec_from_file_location("lumOrchestraGate", MODULE)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
SHA = "a" * 40

def packet(kind="research", provider="deterministicLocal", stage="sanityCheck"):
    routes = {
        "read": ["lum", "kiri"],
        "research": ["lum", "skuldResearch"],
        "proof": ["lum", "urdDoctorGoddess"],
        "patch": ["lum", "kugi", "urdDoctorGoddess"],
        "build": ["lum", "kugi", "tetsu", "kaji", "urdDoctorGoddess"],
    }
    return {
        "schema": "luhmOs.lumOrchestraTask.v1",
        "taskId": "testTask", "scopeId": "candidateScope", "sourceRef": SHA,
        "kind": kind, "requestedStage": stage, "providerId": provider,
        "workers": routes[kind],
        "budget": {"maxRequests": 2, "maxParallel": 1, "maxPasses": 2},
        "receipts": [],
        "authority": {"mutation": False, "green": False, "crown": False},
    }

class OrchestraGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg = json.loads((MODULE.parents[1] / "doctrine/lumOrchestraHardeningV1.json").read_text())

    def evaluate(self, task):
        return gate.assess(task, SHA, self.cfg)

    def test_read_only_candidate_never_green(self):
        self.assertEqual(self.evaluate(packet()), ([], "STRUCTURAL_CANDIDATE_ONLY"))

    def test_dual_build_twins_are_bounded(self):
        self.assertEqual(self.evaluate(packet("build")), ([], "STRUCTURAL_CANDIDATE_ONLY"))

    def test_wrong_source_rejected(self):
        task = packet()
        task["sourceRef"] = "b" * 40
        self.assertIn("RED_SOURCE_MISMATCH", self.evaluate(task)[0])

    def test_unknown_provider_denied(self):
        task = packet()
        task["providerId"] = "unapprovedCloud"
        self.assertIn("RED_PROVIDER_ID", self.evaluate(task)[0])

    def test_google_subscription_does_not_enable_api(self):
        findings, state = self.evaluate(packet(provider="googleAi"))
        self.assertEqual(state, "REVIEW_ONLY")
        self.assertIn("AMBER_GOOGLE_DEVELOPER_API_BILLING_QUOTA_AND_IDENTITY_UNVERIFIED", findings)

    def test_authenticated_execution_is_required(self):
        task = packet("patch", stage="mutation")
        receipt = lambda name: {
            "stage": name, "taskId": task["taskId"], "scopeId": task["scopeId"],
            "sourceRef": SHA, "status": "GREEN", "evidenceRefs": ["sha256:" + "0" * 64],
        }
        task["receipts"] = [receipt(x) for x in ("sanityCheck", "audit", "ingest")]
        self.assertEqual(self.evaluate(task)[1], "STOP")

    def test_stale_receipt_rejected(self):
        task = packet(stage="audit")
        task["receipts"] = [{
            "stage": "sanityCheck", "taskId": "testTask", "scopeId": "candidateScope",
            "sourceRef": "b" * 40, "status": "GREEN", "evidenceRefs": ["sha256:" + "0" * 64],
        }]
        self.assertIn("RED_RECEIPT_IDENTITY", self.evaluate(task)[0])

    def test_excess_support_workers_denied(self):
        task = packet()
        task["workers"].extend(["yume", "koe", "sumi", "shiori"])
        self.assertIn("RED_WORKER_ROUTE", self.evaluate(task)[0])

    def test_receipt_gap_denied(self):
        self.assertIn("RED_RECEIPT_ORDER_OR_GAP", self.evaluate(packet(stage="ingest"))[0])

    def test_credential_field_denied(self):
        task = packet()
        task["apiKey"] = "not-a-real-key"
        self.assertIn("RED_CREDENTIAL_FIELD", self.evaluate(task)[0])

    def test_forged_crown_denied(self):
        task = packet()
        task["authority"]["crown"] = True
        self.assertIn("RED_UNTRUSTED_AUTHORITY", self.evaluate(task)[0])

    def test_overbudget_denied(self):
        task = packet()
        task["budget"]["maxParallel"] = 4
        self.assertIn("RED_TASK_BUDGET", self.evaluate(task)[0])

    def test_duplicate_json_denied(self):
        with self.assertRaisesRegex(ValueError, "RED_DUPLICATE_JSON_KEY"):
            json.loads('{"taskId":"a","taskId":"b"}', object_pairs_hook=gate.unique_pairs)

    def check_modified_google_policy(self, updater):
        real_load = gate.load_json
        def tamper(path):
            obj = real_load(path)
            if path.name == "googleAiDeveloperEntitlementsV1.json":
                updater(obj)
            return obj
        with patch.object(gate, "load_json", side_effect=tamper):
            errors, _, _ = gate.policy_check(MODULE.parents[1])
        return errors

    def test_google_consumer_plan_cannot_grant_vertex_or_api(self):
        errors = self.check_modified_google_policy(
            lambda data: data["entitlementAxes"]["consumerSubscription"].update({"grantsDeveloperApi": True}))
        self.assertIn("RED_GOOGLE_CONSUMER_TO_API_ESCALATION", errors)

    def test_google_credit_promise_cannot_grant_paid_execution(self):
        errors = self.check_modified_google_policy(
            lambda data: data["entitlementAxes"]["developerProgramBenefits"].update({"grantApiExecution": True}))
        self.assertIn("RED_GOOGLE_UNREDEEMED_CREDIT_AUTHORITY", errors)

    def test_google_unresolved_billing_warning_cannot_be_cleared_by_agent(self):
        errors = self.check_modified_google_policy(
            lambda data: data["entitlementAxes"]["cloudBilling"].update({"paidCallsAllowed": True}))
        self.assertIn("RED_GOOGLE_BILLING_WARNING_SUPPRESSED", errors)

    def test_google_provider_cannot_self_authorize(self):
        errors = self.check_modified_google_policy(
            lambda data: data["executionLaw"].update({"noProviderCanGrantGreen": False}))
        self.assertIn("RED_GOOGLE_EXECUTION_AUTHORITY", errors)

    def test_unrelated_canonical_worker_cannot_join_route(self):
        task = packet()
        task["workers"].append("kugi")
        self.assertIn("RED_WORKER_ROUTE", self.evaluate(task)[0])

if __name__ == "__main__":
    unittest.main()

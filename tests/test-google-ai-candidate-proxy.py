"""Google AI candidate proxy: no network unless every gate is specifically true."""
import importlib.util
import io
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "google_ai_candidate_proxy", HERE / "host/api/google-ai-candidate-proxy.py")
proxy = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = proxy
SPEC.loader.exec_module(proxy)
PACKET = {
    "schema": "luhmOs.googleAiCandidateReview.v1", "providerId": "googleAi",
    "capabilityId": "candidateReview", "taskId": "cast-review-one",
    "scopeId": "proposed-studio", "sourceRef": "a"*40,
    "reviewText": "Review public GitHub test conclusions, no private artwork.",
}
GATES = {
    "GOOGLE_AI_ACCOUNT_BOUND": "YES",
    "GOOGLE_AI_DEVELOPER_API_VERIFIED": "YES",
    "GOOGLE_AI_BILLING_QUOTA_VERIFIED": "YES",
    "GOOGLE_AI_PROFESSOR_COST_APPROVED": "YES",
    "GOOGLE_AI_MAX_REQUESTS": "1",
    "GOOGLE_AI_NETWORK_ENABLED": "YES",
    "GEMINI_API_KEY": "test-placeholder-do-not-call",
    "GOOGLE_AI_MODEL": "gemini-2.5-flash",
}


class fake_response:
    status = 200
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass
    def read(self, number):
        return json.dumps({
            "candidates": [{"content": {"parts": [{"text": "One advisory review."}]}}]
        }).encode("utf-8")


class proxy_tests(unittest.TestCase):
    def test_dry_run_requires_no_key_and_never_runs(self):
        out = proxy.proposal(PACKET, environ={})
        self.assertFalse(out["providerCalled"])
        self.assertFalse(out["readiness"]["executionAllowed"])
        self.assertEqual(out["state"], "SOURCE_ONLY")
        self.assertEqual(len(out["payloadSha256"]), 64)

    def test_each_gate_blocks_before_network(self):
        for key in GATES:
            with self.subTest(gate=key):
                env = dict(GATES)
                env.pop(key)
                called = []
                def fake(req, timeout):
                    called.append(True)
                    return fake_response()
                with self.assertRaisesRegex(RuntimeError, "RED_GOOGLE_AI_ENTITLEMENT"):
                    proxy.execute(PACKET, environ=env, opener=fake)
                self.assertFalse(called)

    def test_sanitizer_rejects_private_payloads_and_wrong_scope(self):
        for review_text in ["email x@example.com", "my password=secret",
                            "file at drive.google.com/abc", ""]:
            with self.subTest(text=review_text):
                bad = dict(PACKET, reviewText=review_text)
                with self.assertRaisesRegex(ValueError, "RED_REVIEW_TEXT"):
                    proxy.validate(bad)
        with self.assertRaisesRegex(ValueError, "RED_PACKET_FIELDS"):
            proxy.validate(dict(PACKET, permissions={"mutation": True}))

    def test_only_approved_exact_google_endpoint_is_used(self):
        seen = []
        def fake(request, timeout):
            seen.append((request.full_url, request.get_method(), timeout,
                         dict(request.header_items()), request.data))
            return fake_response()
        receipt = proxy.execute(PACKET, environ=GATES, opener=fake)
        self.assertEqual(len(seen), 1)
        self.assertEqual(seen[0][1:3], ("POST", 15))
        self.assertEqual(seen[0][0], proxy.API_ORIGIN + "/v1beta/models/gemini-2.5-flash:generateContent")
        self.assertEqual(seen[0][3]["X-goog-api-key"], GATES["GEMINI_API_KEY"])
        self.assertEqual(receipt["state"], "ADVISORY_RESPONSE_RECEIVED")
        self.assertFalse(receipt["projectGreen"])
        self.assertFalse(receipt["publicationAuthority"])
        self.assertEqual(receipt["crown"], "STOP")

    def test_no_response_secrets_are_printed(self):
        self.assertFalse(proxy.readiness(environ=GATES).get("GEMINI_API_KEY"))
        self.assertNotIn(GATES["GEMINI_API_KEY"], json.dumps(proxy.proposal(PACKET, environ=GATES)))


if __name__ == "__main__":
    unittest.main()

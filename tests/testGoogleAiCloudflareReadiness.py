"""Google Big Brother and Cloudflare edge compatibility safety tests.

Real source contract is checked; all network responses below are fixtures.
"""
import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "readiness", ROOT / "tools/googleAiCloudflareReadiness.py")
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


class ProviderEdgeTests(unittest.TestCase):
    def test_current_canon_and_layer_order(self):
        contracts = probe.policies(ROOT)
        self.assertEqual(probe.check_contract(contracts), [])
        self.assertEqual(
            [(x["priority"], x["id"])
             for x in contracts["doctrine/studioCompatibilityFastMeshV1.json"]["compatibilityPriority"]],
            [(1, "chatGptOpenAi"), (2, "github")])

    def test_cannot_redirect_mcp_through_unverified_cloudflare_proxy(self):
        docs = probe.policies(ROOT)
        docs["doctrine/cloudflareLumOrchestrationV1.json"]["trafficLanes"]["publicMcp"]["cloudflareProxy"] = "ON"
        self.assertIn("MCP_DIRECT_NO_PROXY_NO_CACHE", probe.check_contract(docs))

    def test_google_ai_must_remain_billable_stopped(self):
        docs = probe.policies(ROOT)
        docs["doctrine/studioCompatibilityFastMeshV1.json"]["workhorse"]["googleAi"]["permittedBillableCalls"] = True
        self.assertIn("GOOGLE_NO_UNPROVEN_SPENDING", probe.check_contract(docs))

    def test_cloudflare_cannot_become_agent_or_ai_provider(self):
        docs = probe.policies(ROOT)
        docs["doctrine/cloudflareAirTrafficControllerV1.json"]["authorityBoundary"]["aiProvider"] = True
        self.assertIn("CLOUDFLARE_NETWORK_ONLY", probe.check_contract(docs))

    def test_google_without_key_makes_no_network_call(self):
        def forbidden(*args, **kwargs):
            raise AssertionError("unexpected API request")
        result = probe.google_readiness(key=None, probe=forbidden)
        self.assertEqual(result["state"], "NOT_VERIFIED_NO_CREDENTIAL")
        self.assertFalse(result["modelGenerationCalled"])
        self.assertFalse(result["identityAndEntitlementVerified"])

    def test_google_metadata_only_receipt(self):
        def fake(url, *, api_key=None, method="GET"):
            self.assertEqual(url, probe.GOOGLE_MODELS)
            self.assertEqual(method, "GET")
            self.assertEqual(api_key, "fixture-secret-value")
            return (200, json.dumps({"models": [{"name": "models/example-test-model"}]}).encode())
        result = probe.google_readiness(key="fixture-secret-value", probe=fake)
        self.assertEqual(result["state"], "AUTHENTICATED_MODEL_METADATA")
        self.assertTrue(result["modelMetadataAccessVerified"])
        self.assertFalse(result["identityAndEntitlementVerified"])
        self.assertFalse(result["billingEntitlementVerified"])
        self.assertFalse(result["costApproval"])
        self.assertFalse(result["modelWorkerDeployed"])
        self.assertNotIn("fixture-secret-value", json.dumps(result))

    def test_google_invalid_response_and_auth_deny(self):
        for response in ((403, b""), (200, b'{"models":[]}'), (200, b'not json')):
            with self.subTest(response=response):
                result = probe.google_readiness(
                    key="fixture", probe=lambda *a, **kw: response)
                self.assertNotEqual(result["state"], "AUTHENTICATED_MODEL_METADATA")
                self.assertFalse(result["costApproval"])

    def test_dns_record_observed_but_not_proxy_or_mcp_proof(self):
        def fake(url, *, method="GET"):
            if url == probe.DNS_ENDPOINT:
                return 200, b'{"Status":0,"Answer":[{"type":5,"data":"example.onrender.com."}]}'
            if url == probe.MCP_ENDPOINT:
                self.assertEqual(method, "HEAD")
                return 405, b""
            raise AssertionError("unexpected URL")
        result = probe.cloudflare_readiness(probe=fake)
        self.assertEqual(result["dnsState"], "PUBLIC_CNAME_OBSERVED")
        self.assertEqual(result["directMcpOrigin"], "ORIGIN_PROTOCOL_BOUNDARY_REACHABLE_NOT_MCP_PROOF")
        self.assertFalse(result["mcpSessionNegotiated"])
        self.assertFalse(result["cloudflareProxyEnabled"])
        self.assertFalse(result["dnsChanged"])

    def test_missing_cname_does_not_claim_edge_green(self):
        def fake(url, *, method="GET"):
            if url == probe.DNS_ENDPOINT:
                return 200, b'{"Status":0,"Answer":[]}'
            return 503, b""
        result = probe.cloudflare_readiness(probe=fake)
        self.assertEqual(result["dnsState"], "NO_PUBLIC_CNAME_OBSERVED")
        self.assertEqual(result["directMcpOrigin"], "ORIGIN_SERVER_ERROR_503")

    def test_key_never_sent_to_edge_or_unknown_url(self):
        with self.assertRaisesRegex(ValueError, "RED_UNAPPROVED_PROBE_ENDPOINT"):
            probe.request_status("https://example.org")
        with self.assertRaisesRegex(ValueError, "RED_PROVIDER_KEY_ON_WRONG_ENDPOINT"):
            probe.request_status(probe.DNS_ENDPOINT, api_key="bad")

    def test_exact_source_required_before_receipt(self):
        with self.assertRaisesRegex(ValueError, "exact SHA"):
            probe.receipt(ROOT, "main")
        with self.assertRaisesRegex(ValueError, "checkout does not match"):
            probe.receipt(ROOT, "a" * 40)


if __name__ == "__main__":
    unittest.main()

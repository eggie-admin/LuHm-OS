#!/usr/bin/env python3
"""Four-service Canon, namespace, safety and forward/reverse DNS negative controls."""
from __future__ import annotations
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from fourServiceCompatibilityAudit import audit
from fqdnForwardReverseProbe import canonical_hostname, inspect


class FourServiceCompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads((ROOT / "doctrine/fourServiceCompatibilityCanonV1.json").read_text())
        cls.source = json.loads((ROOT / "doctrine/currentSourceTruthV3.json").read_text())
        cls.network = json.loads((ROOT / "doctrine/networkSpineV1.json").read_text())
        cls.cloudflare = json.loads((ROOT / "doctrine/cloudflareLumOrchestrationV1.json").read_text())
        cls.quarantine = json.loads((ROOT / "doctrine/companyWideOperationalQuarantineV1.json").read_text())

    def errors(self, d=None):
        return audit(self.doc if d is None else d, self.source,
                     self.network, self.cloudflare, self.quarantine)

    def test_source_policy_passes(self):
        self.assertEqual(self.errors(), [])

    def test_google_ai_is_not_falsely_green(self):
        changed = copy.deepcopy(self.doc)
        changed["providerLanes"][2]["runtime"] = "LIVE"
        self.assertIn("GOOGLE_AI_FALSE_LIVE", self.errors(changed))

    def test_cloudflare_is_not_automatically_active(self):
        changed = copy.deepcopy(self.doc)
        changed["providerLanes"][3]["runtime"] = "LIVE"
        self.assertIn("CLOUDFLARE_FALSE_LIVE", self.errors(changed))

    def test_provider_ids_must_remain_camelhump(self):
        changed = copy.deepcopy(self.doc)
        changed["providerLanes"][2]["id"] = "google_ai"
        self.assertIn("FOUR_PROVIDERS_CHANGED", self.errors(changed))
        self.assertIn("NON_CAMELHUMP_PROVIDER_ID", self.errors(changed))

    def test_chatgpt_library_is_not_an_rsync_endpoint(self):
        changed = copy.deepcopy(self.doc)
        changed["storage"]["chatGptLibraryDirectRsyncSupported"] = True
        self.assertIn("CHATGPT_LIBRARY_RSYNC_FABRICATION", self.errors(changed))

    def test_sync_cannot_arm_silently(self):
        changed = copy.deepcopy(self.doc)
        changed["storage"]["defaultArmed"] = True
        self.assertIn("RCLONE_PENDING_SOURCE_LAW", self.errors(changed))

    def test_reversed_labels_are_not_ip_ptr(self):
        changed = copy.deepcopy(self.doc)
        changed["fqdn"]["reversedLabelNamespace"]["isPtrRecord"] = True
        self.assertIn("REVERSE_NAMESPACE_NOT_PTR", self.errors(changed))

    def test_no_cloudflare_proxy_without_streaming_proof(self):
        changed = copy.deepcopy(self.doc)
        changed["fqdn"]["forward"][0]["allowProxyBeforeStreamProof"] = True
        self.assertIn("UNAPPROVED_PROXY_SWITCH", self.errors(changed))

    def test_site_and_quarantine_not_mutated(self):
        changed = copy.deepcopy(self.doc)
        changed["safeMutations"]["newAgentActivation"] = True
        self.assertIn("UNAUTHORIZED_PRODUCTION_MUTATION", self.errors(changed))

    def test_hostname_validation_rejects_unsafe_input(self):
        for value in ("foo.local", "http://mcp.eggiebagelface.art",
                      "mcp.eggiebagelface.art/secret", "-bad.eggiebagelface.art"):
            if value == "foo.local":
                self.assertEqual(canonical_hostname(value), value)
            else:
                with self.assertRaises(ValueError):
                    canonical_hostname(value)
        self.assertEqual(canonical_hostname("MCP.EGGIEBAGELFACE.ART."),
                         "mcp.eggiebagelface.art")

    def test_dns_fixture_produces_observation_not_host_promotion(self):
        def fixture(host, kind):
            if kind == "CNAME" and host == "mcp.eggiebagelface.art":
                return {"rcode": 0, "answers": ["luhm-os-harness-green.onrender.com."]}
            if kind == "NS":
                return {"rcode": 0, "answers": ["example.ns.cloudflare.com."]}
            return {"rcode": 0, "answers": []}
        result = inspect(self.doc, fixture)
        self.assertFalse(result["ipPtr"]["provisioningAttempted"])
        self.assertFalse(result["internalReverseLabels"]["isPtrRecord"])
        self.assertEqual(result["tlsAndMcpHostVerification"], "NOT_CHECKED")
        self.assertEqual(result["overallNetworkReady"], "UNVERIFIED_REQUIRES_OWNER_ZONE_AND_TLS_MCP_PROOF")
        self.assertTrue(result["forward"][0]["candidateMcpCnameTargetMatch"])

    def test_dns_probe_fails_closed_on_resolver_failure(self):
        def failure(host, kind):
            raise OSError("Synthetic offline resolver")
        result = inspect(self.doc, failure)
        self.assertEqual(result["nameserverAndSoaEvidence"]["NS"]["status"], "UNKNOWN")
        self.assertEqual(result["forward"][0]["forwardEvidence"], "UNVERIFIED_FORWARD")
        self.assertEqual(result["crownStatus"], "STOP")


if __name__ == "__main__":
    unittest.main()

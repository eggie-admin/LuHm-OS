"""Tests for source-only CAST API alignment."""
import unittest
from tools.castApiAlignment import audit_contracts, route_plan

class CastApiAlignmentTests(unittest.TestCase):
    def test_current_canon_contracts(self):
        result = audit_contracts()
        self.assertEqual(result["status"], "GREEN", result["issues"])
        self.assertFalse(result["authorityGranted"])
        self.assertFalse(result["googleRuntimeVerified"])

    def test_capability_routing(self):
        expected = {"source": "github", "ci": "github", "reasoning": "googleAi",
                    "conversation": "chatGpt", "dns": "cloudflare", "runtime": "render"}
        for capability, provider in expected.items():
            with self.subTest(capability=capability):
                plan = route_plan(capability)
                self.assertEqual(plan["provider"], provider)
                self.assertFalse(plan["executed"])

    def test_unknown_fails_closed(self):
        self.assertEqual(route_plan("productionDeploy")["status"], "BLOCKED")

if __name__ == "__main__":
    unittest.main()

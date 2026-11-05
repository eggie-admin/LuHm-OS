import unittest
from tools.castAutoPromotion import evaluate_auto_promotion, cockpit_default

SHA = "a" * 40
def good():
    return {"sourceRef": SHA, "classification": "PUBLIC_DISPOSABLE",
            **{k: True for k in ("exactHeadCi", "cleanDiff", "noSecrets",
                "noPersonalData", "noProtectedAssets", "noPrivilegedOperations",
                "isolatedCandidate", "sourceAuditGreen")}}

class TestCastAutoPromotion(unittest.TestCase):
    def test_safe_eligible(self):
        x = evaluate_auto_promotion("testing", "proposed", good(), source_ref=SHA)
        self.assertEqual(x["status"], "ELIGIBLE_FOR_BOUNDED_AUTOMATION")
        self.assertFalse(x["executed"])
    def test_unknown_sensitivity_blocked(self):
        x = good(); x.pop("classification")
        self.assertEqual(evaluate_auto_promotion("testing","proposed",x,source_ref=SHA)["status"],"BLOCKED")
    def test_no_release_auto(self):
        self.assertEqual(evaluate_auto_promotion("proposed","beta",good(),source_ref=SHA)["status"],"BLOCKED")
    def test_missing_ci_is_amber(self):
        x = good(); x["exactHeadCi"] = False
        self.assertEqual(evaluate_auto_promotion("testing","proposed",x,source_ref=SHA)["status"],"AMBER")
    def test_cockpit_requires_connection_and_consent(self):
        self.assertFalse(cockpit_default(False, True)["effectiveEnabled"])
        self.assertFalse(cockpit_default(True, False)["effectiveEnabled"])
        self.assertTrue(cockpit_default(True, True)["effectiveEnabled"])

if __name__ == "__main__":
    unittest.main()

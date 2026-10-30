import unittest
from tools.cast_escalation_snapshot import assess

class CastEscalationTests(unittest.TestCase):
    def test_not_automatically_promoted(self):
        state=assess()
        self.assertFalse(state["automaticMerge"])
        self.assertFalse(state["automaticDeploy"])
        self.assertFalse(state["automaticPublish"])
        self.assertFalse(state["currentSourcePromotion"])
    def test_beta_and_public_require_evidence(self):
        phases=assess()["phases"]
        self.assertFalse(phases["privateBeta"]["eligible"])
        self.assertFalse(phases["publicStable"]["eligible"])
        self.assertTrue(phases["privateBeta"]["missingEvidence"])
        self.assertTrue(phases["publicStable"]["missingEvidence"])
if __name__=="__main__":
    unittest.main()

import unittest
from tools.family_lane_policy import Request, evaluate

class PolicyTests(unittest.TestCase):
    def test_family_general(self):
        self.assertEqual(evaluate(Request("github","family","general","unknown",True,False)),"ELIGIBLE_FOR_HUMAN_REVIEW")
    def test_family_adult_denied(self):
        self.assertEqual(evaluate(Request("google","family","adult","adult_verified",True,False)),"DENY_ADULT_BOUNDARY")
    def test_teen_adult_denied(self):
        self.assertEqual(evaluate(Request("openai","teen","adult","minor",True,False)),"DENY_ADULT_BOUNDARY")
    def test_adult_unverified_denied(self):
        self.assertEqual(evaluate(Request("openai","adult21","adult","unknown",True,False)),"DENY_ADULT_BOUNDARY")
    def test_adult_verified_review_only(self):
        self.assertEqual(evaluate(Request("openai","adult21","adult","adult_verified",True,False)),"ELIGIBLE_FOR_HUMAN_REVIEW")
    def test_adapter_requires_approval(self):
        self.assertEqual(evaluate(Request("meta","teen","general","unknown",True,False)),"DENY_ADAPTER_AUTHORITY")
    def test_rights(self):
        self.assertEqual(evaluate(Request("github","teen","general","unknown",False,False)),"DENY_RIGHTS_UNREVIEWED")
    def test_unknown_provider(self):
        self.assertEqual(evaluate(Request("other","family","general","unknown",True,False)),"DENY_UNKNOWN")

if __name__ == "__main__":
    unittest.main()

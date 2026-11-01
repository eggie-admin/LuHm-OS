import unittest
from tools.chatFeatureIntake import validate

BASE = {"taskId": "newGameMenu", "sourceRef": "a" * 40,
        "kind": "htmlUi", "request": "Add a touch-friendly game menu"}

class ChatFeatureIntakeTests(unittest.TestCase):
    def test_staged_not_authorized(self):
        result = validate(dict(BASE))
        self.assertEqual(result["lane"], "proposed")
        self.assertFalse(result["mutationAuthorized"])
        self.assertFalse(result["deploymentAuthorized"])
    def test_bad_source_rejected(self):
        x = dict(BASE, sourceRef="main")
        with self.assertRaises(ValueError): validate(x)
    def test_extra_permissions_rejected(self):
        x = dict(BASE, autoDeploy=True)
        with self.assertRaises(ValueError): validate(x)
    def test_empty_request_rejected(self):
        x = dict(BASE, request="")
        with self.assertRaises(ValueError): validate(x)

if __name__ == "__main__":
    unittest.main()

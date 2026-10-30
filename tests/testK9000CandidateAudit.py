import copy
import unittest
from tools.k9000CandidateAudit import audit_files, read_files

class K9000CandidateAuditTests(unittest.TestCase):
    def setUp(self):
        self.files = read_files()

    def test_expected_candidate(self):
        self.assertEqual([], audit_files(self.files))

    def test_negative_controls(self):
        samples = [
            ("html", lambda s: s.replace("default-src 'none'", "default-src *")),
            ("js", lambda s: s + "\nnavigator.mediaDevices.getUserMedia()"),
            ("kotlin", lambda s: s.replace('"camera_probe_requested" -> setOf("type")', '"camera_probe_requested" -> setOf("type", "shell")')),
            ("presets", lambda s: s.replace('name="macOS K9000 Candidate"', 'name="macOS Broken"')),
            ("canon", lambda c: dict(c, status="DEPLOYED")),
            ("canon", lambda c: dict(c, profiles=dict(c["profiles"], jacobCreator=dict(c["profiles"]["jacobCreator"], adultAssets=True)))),
        ]
        for key, mutation in samples:
            with self.subTest(target=key, mutation=str(mutation)):
                fixture = copy.deepcopy(self.files)
                fixture[key] = mutation(fixture[key])
                self.assertTrue(audit_files(fixture))

if __name__ == "__main__":
    unittest.main()

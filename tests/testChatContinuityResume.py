"""Source-backed Project Hydra continuity contract, offline without credentials."""
import json
import unittest
from pathlib import Path
from tools.contextTourniquet import clamp

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "doctrine" / "chatContinuityResumeV1.json"

def valid_packet():
    return {
        "sourceRef": "e86d13fbb20ce308ecacdc1ba676a1503a29ee6c",
        "objective": "Recover current project state",
        "confirmedFacts": [{"class":"OBSERVED","statement":"Source inspected","evidenceRefs":["git:commit"]}],
        "evidenceRefs": ["git:commit"],
        "pendingDecisions": [], "conflicts": [],
        "proposedMutations": [],
        "executionAuthorized": False
    }

class ChatContinuityResumeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = json.loads(CONTRACT.read_text(encoding="utf-8"))

    def test_source_references_exist(self):
        self.assertEqual(self.c["source"]["repository"], "eggie-admin/LuHm-OS")
        for path in self.c["source"]["readOrder"]:
            self.assertTrue((ROOT / path).is_file(), path)

    def test_bounded_checkpoint(self):
        packet = clamp(valid_packet())
        self.assertEqual(packet["schema"], "luhmOs.contextCheckpoint.v1")
        self.assertEqual(packet["sourceRef"], valid_packet()["sourceRef"])
        self.assertIs(packet["executionAuthorized"], False)
        self.assertEqual(packet["crownStatus"], "stop")

    def test_missing_required_field_rejected(self):
        packet = valid_packet()
        packet.pop("sourceRef")
        with self.assertRaises(SystemExit):
            clamp(packet)

    def test_self_authorization_rejected(self):
        packet = valid_packet()
        packet["executionAuthorized"] = True
        with self.assertRaises(SystemExit):
            clamp(packet)

    def test_unproven_observation_rejected(self):
        packet = valid_packet()
        packet["confirmedFacts"][0]["evidenceRefs"] = []
        with self.assertRaises(SystemExit):
            clamp(packet)

    def test_invalid_claim_class_rejected(self):
        packet = valid_packet()
        packet["confirmedFacts"][0]["class"] = "FULL_GREEN_ALWAYS"
        with self.assertRaises(SystemExit):
            clamp(packet)

    def test_no_fake_runtime_or_public_private_storage(self):
        self.assertFalse(self.c["roles"]["independentWorkersProven"])
        self.assertFalse(self.c["statusClaims"]["fullCrossChatHostRecoveryProven"])
        self.assertFalse(self.c["storage"]["privateArtifactsOnPublicRepo"])
        self.assertFalse(self.c["storage"]["publicChatTranscriptStorage"])
        self.assertTrue(self.c["roles"]["quarantineGovernsRuntime"])
        self.assertIn("DEVICE_TESTED", self.c["resumeStatus"])

if __name__ == "__main__":
    unittest.main()

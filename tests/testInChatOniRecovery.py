import unittest
from tools.inChatOniRecoveryGate import adjudicate, GATES

def packet():
    sourceRef = "a" * 40
    return {"schema": "luhmOs.inChatOniReceipt.v1",
        "taskId": "cathedralFix", "sourceRef": sourceRef,
        "scopeId": "chatHost", "authority": "readOnlyEvidence",
        "gates": {g: {"state": "GREEN", "sourceRef": sourceRef,
                       "evidenceRef": "receipt:" + g, "observedAt": "2026-10-12T01:00:00Z",
                       "proofKind": g} for g in GATES}}

def check(p):
    return adjudicate(p, taskId="cathedralFix", sourceRef="a" * 40, scopeId="chatHost")

class RecoveryGateTests(unittest.TestCase):
    def test_all_receipts(self):
        self.assertEqual(check(packet()).state, "GREEN")

    def test_unproven_host_blocks_green(self):
        p=packet(); p["gates"]["chatGptHostMount"]={"state":"UNKNOWN"}
        self.assertEqual(check(p).gate, "chatGptHostMount")
        self.assertEqual(check(p).state, "AMBER")

    def test_wrong_source_ref(self):
        p=packet(); p["sourceRef"]="b"*40
        self.assertEqual(check(p).state, "RED")

    def test_render_receipt_is_not_host_receipt(self):
        p=packet()
        p["gates"]["chatGptHostMount"]["proofKind"]="renderExactDeploy"
        self.assertEqual(check(p).state, "RED")

    def test_fake_demo_green(self):
        p=packet()
        p["gates"]["godotWebInput"]["evidenceRef"]="DEMO:click"
        self.assertEqual(check(p).state, "RED")

    def test_missing_gate(self):
        p=packet(); del p["gates"]["samsungTouch"]
        self.assertEqual(check(p).state, "RED")

    def test_untrusted_authority(self):
        p=packet(); p["authority"]="autoCrown"
        self.assertEqual(check(p).state, "RED")

    def test_missing_green_receipt(self):
        p=packet(); del p["gates"]["mcpResourceContract"]["observedAt"]
        self.assertEqual(check(p).state, "RED")

if __name__ == "__main__":
    unittest.main()

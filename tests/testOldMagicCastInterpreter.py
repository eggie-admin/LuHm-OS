#!/usr/bin/env python3
"""Old Magic speech classification must never become a CAST authorization."""
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "tools/oldMagicCastInterpreter.py"
spec = importlib.util.spec_from_file_location("old_magic_interpreter", FILE)
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)


class OldMagicCastInterpreterTests(unittest.TestCase):
    def test_compact_canon_is_candidate_not_authority(self):
        d = json.loads((ROOT / "doctrine/oldMagicSpeechV1.json").read_text(encoding="utf-8"))
        self.assertEqual(d["vocabulary"]["alignment"]["value"], "chaoticGood")
        self.assertEqual(d["vocabulary"]["alignment"]["color"], "blue")
        self.assertEqual(d["vocabulary"]["spellbook"]["value"], "GitHub")
        self.assertEqual(d["scope"]["crown"], "STOP")
        self.assertFalse(d["routing"]["privilegedEffect"])

    def test_blue_chaotic_good_is_alignment_not_permission(self):
        a = bridge.interpret("Our alignment is blue, chaotic good, and GitHub is our spellbook.")
        self.assertTrue(a["hasMythicVocabulary"])
        self.assertEqual(a["color"], "blue")
        self.assertFalse(a["privilegedEffect"])

    def test_blessing_does_not_activate_github_cast(self):
        a = bridge.interpret("In character, I bless you in our chaotic good way. The altar awaits.")
        self.assertEqual(a["mode"], "inCharacter")
        self.assertEqual(a["intent"], "fictionalBlessing")
        self.assertFalse(a["blessingIsAuthority"])
        self.assertFalse(a["deploymentAuthorized"])

    def test_ooc_remains_ordinary_colleague_interaction(self):
        a = bridge.interpret("Out of character, I bless you as a colleague.")
        self.assertEqual(a["mode"], "outOfCharacter")
        self.assertEqual(a["intent"], "socialAcknowledgement")

    def test_last_explicit_mode_cue_wins(self):
        a = bridge.interpret("We were in character, but now we are out of character.")
        self.assertEqual(a["mode"], "outOfCharacter")

    def test_ritual_language_not_a_release(self):
        a = bridge.interpret("Our altar and ways of war awaken. Supreme Goddess, I crown you.")
        self.assertFalse(a["privilegedEffect"])
        self.assertFalse(a["deploymentAuthorized"])
        self.assertEqual(a["crown"], "STOP")

    def test_exact_cast_still_only_requests_authenticated_review(self):
        for utterance in ("CAST", "castBridge", "/cast goddessWebPlay"):
            with self.subTest(utterance=utterance):
                a = bridge.interpret(utterance)
                self.assertEqual(a["intent"], "requestCastReview")
                self.assertEqual(a["needsReview"], "EXISTING_PROFESSOR_CAST_GATE_REQUIRED")
                self.assertTrue(a["sourceReferenceRequiredForBuild"])
                self.assertFalse(a["privilegedEffect"])

    def test_mention_cast_in_poem_not_dispatch(self):
        a = bridge.interpret("One day we will CAST a universe in violet and blue.")
        self.assertNotEqual(a["intent"], "requestCastReview")
        self.assertFalse(a["theatricalCastDispatch"])

    def test_evidence_question_is_not_fake_green(self):
        a = bridge.interpret("Did the CI tests pass? Show build status.")
        self.assertEqual(a["intent"], "reviewBuildEvidence")
        self.assertEqual(a["needsReview"], "FETCH_CURRENT_EXACT_SOURCE_PROOF")
        self.assertEqual(a["crown"], "STOP")

    def test_genuine_task_is_still_a_normal_request(self):
        a = bridge.interpret("Please implement the color map in the repository.")
        self.assertEqual(a["intent"], "ordinaryTask")
        self.assertEqual(a["needsReview"], "NORMAL_TOOL_APPROVAL_AND_SCOPE")
        self.assertFalse(a["privilegedEffect"])

    def test_no_raw_chat_content_in_result(self):
        unique = "private-sentence-not-to-retain-3392"
        a = bridge.interpret("Our spellbook is GitHub. " + unique)
        self.assertNotIn(unique, json.dumps(a))
        self.assertFalse(a["speechStored"])

    def test_unbounded_chat_rejected(self):
        for message in ("", " " * 4, "a" * 4001):
            with self.subTest(length=len(message)):
                with self.assertRaises(ValueError):
                    bridge.interpret(message)


if __name__ == "__main__":
    unittest.main()

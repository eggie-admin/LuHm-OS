#!/usr/bin/env python3
"""Negative and positive tests for the voice-to-CAST intent compiler."""
from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("fnCast", ROOT / "tools/fnCast.py")
assert SPEC and SPEC.loader
fnCast = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fnCast)
CONTRACT = fnCast.load_contract()
GATE = json.loads((ROOT / "doctrine/finalFormPublicReleaseGateV1.json").read_text())
HEAD = "a" * 40


class FnCastVoiceTests(unittest.TestCase):
    def test_yaml_subset_schema_and_existing_global_alias(self):
        self.assertEqual(CONTRACT["entryPoint"], "LuHmOS.fn.cast")
        self.assertEqual(CONTRACT["sqlCast"]["result"], "boolean")
        self.assertFalse(CONTRACT["sqlCast"]["executesSql"])
        self.assertEqual(CONTRACT["voiceTrigger"]["existingGlobalAliases"]["cst"], "currentSourceTruth")
        self.assertEqual(CONTRACT["voiceTrigger"]["existingGlobalAliases"]["c"], "continue")

    def test_scoped_cast_words_and_punctuation(self):
        for phrase in ("CAST", "cast!", "'cast';", '/?"cast".*', "cst"):
            with self.subTest(phrase=phrase):
                result = fnCast.voice_intent(phrase, CONTRACT, armed=True, context="fnCast")
                self.assertTrue(result["castBoolean"])
                self.assertFalse(result["dispatchAuthorized"])

    def test_only_whole_exact_command_matches(self):
        for phrase in ("broadcast", "forecast", "booleancast", "casting", "cast a spell",
                       "cast; DROP TABLE", "exec cast", "", "create /cast", "cast\nrelease"):
            with self.subTest(phrase=phrase):
                result = fnCast.voice_intent(phrase, CONTRACT, armed=True, context="fnCast")
                self.assertFalse(result["castBoolean"])

    def test_context_and_arm_required_even_for_cast(self):
        for kwargs in ({"armed": False, "context": "fnCast"},
                       {"armed": True, "context": "global"}):
            result = fnCast.voice_intent("cast", CONTRACT, **kwargs)
            self.assertFalse(result["castBoolean"])

    def test_cst_never_hijacks_global_source_truth(self):
        result = fnCast.voice_intent("cst", CONTRACT, armed=True, context="global")
        self.assertFalse(result["castBoolean"])
        self.assertEqual(result["state"], "NOT_IN_FN_CAST_CONTEXT")

    def test_c_single_letter_always_requires_extra_confirmation(self):
        unconfirmed = fnCast.voice_intent("c", CONTRACT, armed=True, context="fnCast")
        confirmed = fnCast.voice_intent(
            "c", CONTRACT, armed=True, context="fnCast", confirm_single_letter=True
        )
        self.assertFalse(unconfirmed["castBoolean"])
        self.assertEqual(unconfirmed["state"], "SINGLE_LETTER_REQUIRES_CONFIRMATION")
        self.assertTrue(confirmed["castBoolean"])
        self.assertFalse(confirmed["dispatchAuthorized"])

    def test_real_release_gate_stays_hold(self):
        result = fnCast.build_receipt(
            "CAST!", armed=True, context="fnCast",
            requested_source_ref=HEAD, checked_out_source_ref=HEAD,
            contract=CONTRACT, release_gate=GATE,
        )
        self.assertEqual(result["tier"]["display"], "FFS!")
        self.assertEqual(result["milestone"]["display"], "FINAL_FORM")
        self.assertEqual(result["finalCast"]["state"], "HOLD_FINAL_FORM_EVIDENCE")
        self.assertFalse(result["crownCondition"]["evidenceReadyForIndependentReview"])
        self.assertIn("androidPhysicalFirstLaunch", result["crownCondition"]["pendingProofs"])
        self.assertFalse(result["finalCast"]["buildDispatched"])
        self.assertFalse(result["finalCast"]["releasePublished"])
        self.assertFalse(result["finalCast"]["crownGranted"])

    def test_logical_or_cannot_bypass_failed_proof(self):
        fake = json.loads(json.dumps(GATE))
        fake["requiredProofs"] = {"proofOne": "PROVEN", "proofTwo": False}
        fake["fullPublicReleaseGreen"] = True
        report = fnCast.inspect_final_form(
            fake, requested_source_ref=HEAD, checked_out_source_ref=HEAD
        )
        self.assertIn("proofTwo", report["pendingProofs"])
        self.assertFalse(report["evidenceReadyForIndependentReview"])
        self.assertFalse(report["crownGranted"])

    def test_null_and_source_mismatch_always_hold(self):
        fake = json.loads(json.dumps(GATE))
        fake["requiredProofs"] = {"proofOne": "PROVEN", "proofTwo": None}
        report = fnCast.inspect_final_form(
            fake, requested_source_ref=HEAD, checked_out_source_ref="b" * 40
        )
        self.assertIn("proofTwo", report["pendingProofs"])
        self.assertFalse(report["checks"]["exactCheckout"])
        self.assertFalse(report["evidenceReadyForIndependentReview"])

    def test_every_proof_cannot_grant_authority_from_voice(self):
        fake = json.loads(json.dumps(GATE))
        fake["requiredProofs"] = {"proofOne": "PROVEN"}
        fake["releaseArtifact"].update({
            "sourceRef": HEAD,
            "sha256": "a" * 64,
            "signingCertificateSha256": "b" * 64,
            "independentVerification": "PROVEN",
            "signingKeyContinuityProven": True,
            "stableBuildRequired": True,
            "signingKeyStoredInGit": False,
        })
        fake["professorAuthority"]["exactStableSignedArtifactReviewed"] = True
        fake["fullPublicReleaseGreen"] = True
        result = fnCast.build_receipt(
            "cast", armed=True, context="fnCast",
            requested_source_ref=HEAD, checked_out_source_ref=HEAD,
            contract=CONTRACT, release_gate=fake,
        )
        self.assertTrue(result["crownCondition"]["evidenceReadyForIndependentReview"])
        self.assertFalse(result["finalCast"]["releasePublished"])
        self.assertFalse(result["finalCast"]["crownGranted"])
        self.assertEqual(
            result["finalCast"]["state"],
            "REQUIRES_INDEPENDENT_AUDIT_AND_SEPARATE_PROFESSOR_CROWN",
        )


if __name__ == "__main__":
    unittest.main()

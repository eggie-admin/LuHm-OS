#!/usr/bin/env python3
"""Negative and positive tests for the voice-to-CAST intent compiler."""
from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("fnCast", root / "tools/fnCast.py")
assert spec and spec.loader
fnCast = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fnCast)
contract = fnCast.loadContract()
gate = json.loads((root / "doctrine/finalFormPublicReleaseGateV1.json").read_text())
head = "a" * 40


class FnCastVoiceTests(unittest.TestCase):
    def testYamlSubsetSchemaAndExistingGlobalAlias(self):
        self.assertEqual(contract["entryPoint"], "LuHmOS.fn.cast")
        self.assertEqual(contract["sqlCast"]["result"], "boolean")
        self.assertFalse(contract["sqlCast"]["executesSql"])
        self.assertEqual(contract["voiceTrigger"]["existingGlobalAliases"]["cst"], "currentSourceTruth")
        self.assertEqual(contract["voiceTrigger"]["existingGlobalAliases"]["c"], "continue")

    def testScopedCastWordsAndPunctuation(self):
        for phrase in ("CAST", "cast!", "'cast';", '/?"cast".*', "cst"):
            with self.subTest(phrase=phrase):
                result = fnCast.voiceIntent(phrase, contract, armed=True, context="fnCast")
                self.assertTrue(result["castBoolean"])
                self.assertFalse(result["dispatchAuthorized"])

    def testOnlyWholeExactCommandMatches(self):
        for phrase in ("broadcast", "forecast", "booleancast", "casting", "cast a spell",
                       "cast; DROP TABLE", "exec cast", "", "create /cast", "cast\nrelease"):
            with self.subTest(phrase=phrase):
                result = fnCast.voiceIntent(phrase, contract, armed=True, context="fnCast")
                self.assertFalse(result["castBoolean"])

    def testContextAndArmRequiredEvenForCast(self):
        for kwargs in ({"armed": False, "context": "fnCast"},
                       {"armed": True, "context": "global"}):
            result = fnCast.voiceIntent("cast", contract, **kwargs)
            self.assertFalse(result["castBoolean"])

    def testCstNeverHijacksGlobalSourceTruth(self):
        result = fnCast.voiceIntent("cst", contract, armed=True, context="global")
        self.assertFalse(result["castBoolean"])
        self.assertEqual(result["state"], "NOT_IN_FN_CAST_CONTEXT")

    def testCSingleLetterAlwaysRequiresExtraConfirmation(self):
        unconfirmed = fnCast.voiceIntent("c", contract, armed=True, context="fnCast")
        confirmed = fnCast.voiceIntent(
            "c", contract, armed=True, context="fnCast", confirmSingleLetter=True
        )
        self.assertFalse(unconfirmed["castBoolean"])
        self.assertEqual(unconfirmed["state"], "SINGLE_LETTER_REQUIRES_CONFIRMATION")
        self.assertTrue(confirmed["castBoolean"])
        self.assertFalse(confirmed["dispatchAuthorized"])

    def testRealReleaseGateStaysHold(self):
        result = fnCast.buildReceipt(
            "CAST!", armed=True, context="fnCast",
            requestedSourceRef=head, checkedOutSourceRef=head,
            contract=contract, releaseGate=gate,
        )
        self.assertEqual(result["tier"]["display"], "FFS!")
        self.assertEqual(result["milestone"]["display"], "FINAL_FORM")
        self.assertEqual(result["finalCast"]["state"], "HOLD_FINAL_FORM_EVIDENCE")
        self.assertFalse(result["crownCondition"]["evidenceReadyForIndependentReview"])
        self.assertIn("androidPhysicalFirstLaunch", result["crownCondition"]["pendingProofs"])
        self.assertFalse(result["finalCast"]["buildDispatched"])
        self.assertFalse(result["finalCast"]["releasePublished"])
        self.assertFalse(result["finalCast"]["crownGranted"])

    def testLogicalOrCannotBypassFailedProof(self):
        fake = json.loads(json.dumps(gate))
        fake["requiredProofs"] = {"proofOne": "PROVEN", "proofTwo": False}
        fake["fullPublicReleaseGreen"] = True
        report = fnCast.inspectFinalForm(
            fake, requestedSourceRef=head, checkedOutSourceRef=head
        )
        self.assertIn("proofTwo", report["pendingProofs"])
        self.assertFalse(report["evidenceReadyForIndependentReview"])
        self.assertFalse(report["crownGranted"])

    def testNullAndSourceMismatchAlwaysHold(self):
        fake = json.loads(json.dumps(gate))
        fake["requiredProofs"] = {"proofOne": "PROVEN", "proofTwo": None}
        report = fnCast.inspectFinalForm(
            fake, requestedSourceRef=head, checkedOutSourceRef="b" * 40
        )
        self.assertIn("proofTwo", report["pendingProofs"])
        self.assertFalse(report["checks"]["exactCheckout"])
        self.assertFalse(report["evidenceReadyForIndependentReview"])

    def testEveryProofCannotGrantAuthorityFromVoice(self):
        fake = json.loads(json.dumps(gate))
        fake["requiredProofs"] = {"proofOne": "PROVEN"}
        fake["releaseArtifact"].update({
            "sourceRef": head,
            "sha256": "a" * 64,
            "signingCertificateSha256": "b" * 64,
            "independentVerification": "PROVEN",
            "signingKeyContinuityProven": True,
            "stableBuildRequired": True,
            "signingKeyStoredInGit": False,
        })
        fake["professorAuthority"]["exactStableSignedArtifactReviewed"] = True
        fake["fullPublicReleaseGreen"] = True
        result = fnCast.buildReceipt(
            "cast", armed=True, context="fnCast",
            requestedSourceRef=head, checkedOutSourceRef=head,
            contract=contract, releaseGate=fake,
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

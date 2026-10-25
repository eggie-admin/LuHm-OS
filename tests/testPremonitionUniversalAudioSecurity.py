#!/usr/bin/env python3
"""Source-only contract audit for Witching Hour portable audio and PKI boundaries.

Passing does not establish live GitHub Codespaces, phone audio capture,
external native assistant execution, package signing, or TLS origin health.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "doctrine/premonitionUniversalAudioV1.json"

def assess(document):
    failures = []
    def require(test, code):
        if not test:
            failures.append(code)
    require(document.get("schema") == "luhmOs.premonitionUniversalAudio.v1", "schema")
    require(document.get("status") == "SOURCE_CANDIDATE_RUNTIME_UNVERIFIED", "sourceBoundary")
    audio = document.get("audioBuses", {})
    require(set(audio.get(k) for k in ("lead","guest","music","effects")) == {
        "PremonitionVoiceLead","PremonitionVoiceGuest","PremonitionMusic","PremonitionEffects"
    }, "audioBusNames")
    voice = document.get("voice", {})
    require(voice.get("lead") == "lum", "lumDefault")
    require(voice.get("defaultSimultaneousVoices") == 1, "oneLeadAtATime")
    require(voice.get("maximumAudibleVoices") <= 2, "boundedOverlap")
    require(voice.get("autoVoiceGeneration") is False, "voiceProvenance")
    trust = document.get("distributionAndTransport", {}).get("trustSeparation", {})
    require(trust.get("packageSignature") != trust.get("tlsCertificate"), "independentSigningIdentity")
    require(trust.get("authorization") not in (trust.get("packageSignature"), trust.get("tlsCertificate")), "independentAccessIdentity")
    banned = trust.get("secretBytesNeverIn", [])
    for place in ("GitHub source","public site","JSON wire events","screen recordings"):
        require(place in banned, "privateKeyBoundary:"+place)
    channels = document.get("distributionAndTransport", {}).get("platformPackageChannels", {})
    require(channels.get("linux",{}).get("manager") == "apt" and channels.get("linux",{}).get("autoInstall") is False, "linuxPackageLaw")
    require(channels.get("android",{}).get("sameSignerUpgradeRequired") is True, "androidSigner")
    require(channels.get("ios",{}).get("aptNotUsed") is True, "iosNotApt")
    private = document.get("distributionAndTransport", {}).get("publicVsPrivateRoutes", {})
    require(private.get("privateLan",{}).get("dnsSuffix") == "eggiebagelface.lan", "privateDns")
    require(private.get("privateLan",{}).get("neverExposeInPublicDns") is True, "privateLanVisibility")
    require(private.get("privatePortal",{}).get("access", "").startswith("default deny"), "privateZeroTrust")
    require(private.get("mediaForge",{}).get("publicEndpointAllowed") is False, "forgeNeverPublic")
    laws = document.get("distributionAndTransport", {}).get("networkLaws", {})
    for key in ("noRouterPortForwarding","noRawLanAddressInPublicRecords",
                "noPublicMicrophoneOrCamera","tlsVerificationNeverDisabled",
                "noSecretsInUrls","noCloudflareDnsChangesFromCast"):
        require(laws.get(key) is True, key)
    evidence = document.get("distributionAndTransport", {}).get("releaseEvidence", {})
    require(evidence.get("ownerCrown") == "STOP", "crown")
    require(all(evidence.get(k) != "PROVEN" for k in (
        "artifactSigning","packageUpgrade","tlsAndHost",
        "accessAndTunnel","samsungPhysicalProof","iosRuntime")), "noRuntimeGreen")
    require(document.get("release",{}).get("noMergeWithoutReview") is True, "noAutoMerge")
    require(document.get("executionBoundary",{}).get("noRecordingWithoutConsent") is True, "recordingConsent")
    return failures

class PremonitionUniversalAudioSecurityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(DOC.read_text(encoding="utf-8"))

    def test_contract_has_no_unproven_green(self):
        self.assertEqual(assess(self.doc), [])

    def test_reject_insecure_public_media_forge(self):
        mutated = json.loads(json.dumps(self.doc))
        mutated["distributionAndTransport"]["publicVsPrivateRoutes"]["mediaForge"]["publicEndpointAllowed"] = True
        self.assertIn("forgeNeverPublic", assess(mutated))

    def test_reject_private_lan_dns_exposure(self):
        mutated = json.loads(json.dumps(self.doc))
        mutated["distributionAndTransport"]["publicVsPrivateRoutes"]["privateLan"]["neverExposeInPublicDns"] = False
        self.assertIn("privateLanVisibility", assess(mutated))

    def test_reject_false_tls_safety(self):
        mutated = json.loads(json.dumps(self.doc))
        mutated["distributionAndTransport"]["networkLaws"]["tlsVerificationNeverDisabled"] = False
        self.assertIn("tlsVerificationNeverDisabled", assess(mutated))

    def test_reject_runtime_green_without_receipt(self):
        mutated = json.loads(json.dumps(self.doc))
        mutated["distributionAndTransport"]["releaseEvidence"]["samsungPhysicalProof"] = "PROVEN"
        self.assertIn("noRuntimeGreen", assess(mutated))

if __name__ == "__main__":
    unittest.main()

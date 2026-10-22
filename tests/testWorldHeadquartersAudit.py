"""Fail-closed regression tests for World Headquarters candidate."""
import copy
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tools"))
import worldHeadquartersAudit as audit

class WorldHeadquartersTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy = audit.load(audit.CONTRACT)
        cls.contracts = {name:audit.load(name) for name in [
            "doctrine/currentSourceTruthV3.json",
            "doctrine/studioCompatibilityFastMeshV1.json",
            "doctrine/lumGoddessCabinetV1.json",
            "doctrine/companyWideOperationalQuarantineV1.json",
            "doctrine/luhmAiControlPlaneV1.json",
            "doctrine/agentSystemDeploymentV1.json",
            "doctrine/cloudflareAirTrafficControllerV1.json",
            "doctrine/storageTopologyV1.json",
            "doctrine/forgeTwinsV3.json",
            "doctrine/githubRenderSidecarV1.json",
            "doctrine/fourTierOperatingModelV1.json",
        ]}

    def test_canonical_invariants(self):
        self.assertEqual([], audit.assess(self.policy, self.contracts))

    def test_negative_controls(self):
        self.assertEqual(8, audit.negative_controls(self.policy, self.contracts))

    def test_second_layer_is_github_source_not_second_source_of_truth(self):
        self.assertEqual(["chatGptOpenAi","github"], [row["id"] for row in self.policy["compatibilityLayers"]])
        self.assertFalse(self.policy["researchAndDevelopment"]["secondSourceOfTruthInterpretation"]["sourceAuthority"])

    def test_cast_phrase_does_not_auto_install(self):
        forge = self.policy["researchAndDevelopment"]["forge"]
        self.assertTrue(forge["genericPhraseIsNotAValidCastEnvelope"])
        self.assertTrue(self.policy["pipeline"]["noAutomaticDeployment"])
        self.assertFalse(self.policy["promotion"])

if __name__ == "__main__":
    unittest.main()

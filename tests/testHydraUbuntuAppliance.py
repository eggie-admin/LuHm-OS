import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = json.loads((ROOT / "doctrine/hydraUbuntuApplianceV1.json").read_text(encoding="utf-8"))

class HydraUbuntuApplianceContractTest(unittest.TestCase):
    def test_source_never_implies_os_or_agent_runtime(self):
        self.assertEqual(SPEC["status"], "PROPOSED_SOURCE_ONLY")
        self.assertEqual(SPEC["crownStatus"], "STOP")
        self.assertFalse(SPEC["promotion"])
        self.assertFalse(SPEC["productionMergeAuthority"])
        self.assertFalse(SPEC["kernelMutationAuthority"])
        self.assertFalse(SPEC["agentReleaseAuthority"])
        self.assertFalse(SPEC["publicReleaseAuthority"])
        for value in SPEC["proof"].values():
            self.assertNotEqual(value, "VERIFIED")
    def test_ubuntu_kernel_is_distribution_owned(self):
        d = SPEC["distribution"]
        self.assertEqual(d["strategy"], "ubuntuSupportedBasePlusLuHmAppOverlay")
        self.assertFalse(d["customKernelBuild"])
        self.assertFalse(d["firmwareModification"])
        self.assertFalse(d["bootloaderModification"])
        self.assertTrue(d["rootlessAppRuntime"])
        self.assertEqual(d["kernelProof"], "REQUIRES_ACTUAL_TARGET_HOST")
    def test_four_planes_have_explicit_proof_and_authority(self):
        planes = SPEC["planes"]
        self.assertEqual([x["id"] for x in planes], [
            "hardwareAndKernel","headlessServices","webGui","gameMediaAi"
        ])
        self.assertTrue(all(x["requiredProof"] and x["authority"] for x in planes))
        self.assertEqual(SPEC["desktop"]["headless"], "NoX11OrDisplayServerForBackendWorkers")
    def test_hydra_failover_is_bounded_not_exponential_worker_spawning(self):
        h = SPEC["hydraRecovery"]
        self.assertEqual(h["maxConcurrentActive"], 1)
        self.assertEqual(h["maxReplacementCandidates"], 2)
        self.assertEqual(h["maxRestartAttemptsPerWindow"], 2)
        self.assertEqual(len(h["backoffSeconds"]), h["maxRestartAttemptsPerWindow"])
        self.assertTrue(all(x > 0 for x in h["backoffSeconds"]))
        self.assertEqual(h["failedFallback"], "STOP_AND_NOTIFY_OPERATOR")
        self.assertFalse(h["agentSpawnAuthority"])
        self.assertFalse(h["autoElevatePrivileges"])
        self.assertFalse(h["autoPublish"])
        self.assertTrue(h["sourcePinRequired"])
        self.assertTrue(h["rollbackProofRequired"])
    def test_game_media_and_network_stay_conservative(self):
        self.assertTrue(SPEC["ai"]["quarantine"])
        self.assertTrue(SPEC["ai"]["noPaidApiByDefault"])
        self.assertEqual(SPEC["media"]["vlc"], "OptionalLocalDesktopOrReviewedNativeLibVlcNoVlcWebPort")
        self.assertEqual(SPEC["web"]["dom"], "ExistingHTMLAndCSS")
        self.assertFalse(SPEC["web"]["remoteScriptsDefault"])
        self.assertTrue(SPEC["desktop"]["escapeAccessible"])
        for target in SPEC["canonicalRefs"]:
            self.assertTrue((ROOT / target).is_file(), target)
if __name__ == "__main__":
    unittest.main()

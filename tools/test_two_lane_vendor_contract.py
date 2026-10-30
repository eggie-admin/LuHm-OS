#!/usr/bin/env python3
"""Source-only two-lane agent and JS supply-chain contract tests."""
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class TwoLaneCanon(unittest.TestCase):
    def test_developer_bridge_has_zero_packages(self):
        pkg = json.loads((ROOT / "packages/unified-ops/package.json").read_text())
        self.assertEqual(pkg["dependencies"], {})
        self.assertEqual(pkg["devDependencies"], {})
        self.assertTrue(pkg["private"])

    def test_frontend_jquery_is_pinned(self):
        pkg = json.loads((ROOT / "frontEnd/package.json").read_text())
        self.assertEqual(pkg["dependencies"], {"jquery": "3.7.1"})
        self.assertTrue(pkg["private"])

    def test_only_one_mutation_lane_and_no_activation(self):
        data = json.loads((ROOT / "doctrine/unifiedGoddessOrchestraV1.json").read_text())
        self.assertTrue(data["tasks"]["noAutomaticWorkerSpawning"])
        self.assertTrue(data["tasks"]["noRemoteExecution"])
        self.assertTrue(data["agentSong"]["all15WorkersQuarantined"])
        self.assertFalse(data["toolchain"]["python"]["productionExecution"])

    def test_canonical_source_and_production_stop(self):
        data = json.loads((ROOT / "doctrine/currentSourceTruthV3.json").read_text())
        self.assertEqual(data["canonicalRepository"], "eggie-admin/LuHm-OS")
        self.assertFalse(data["promotion"])

    def test_two_lane_plan_never_grants_authority(self):
        lanes = {"lum": ("hear", "resolve"), "mini": ("build", "verify")}
        self.assertEqual(len(lanes), 2)
        for lane in lanes:
            self.assertNotIn("deploy", lane)


if __name__ == "__main__":
    unittest.main()

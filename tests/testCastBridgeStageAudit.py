"""Reject false CAST deployment and runtime claims."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from castBridgeStageAudit import audit


class CastBridgeStageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = json.loads((ROOT / "doctrine/castBridgeStageGateV1.json").read_text(encoding="utf-8"))

    def assert_rejected(self, mutate):
        stage = copy.deepcopy(self.original)
        mutate(stage)
        self.assertTrue(audit(stage=stage)["errors"])

    def test_default_source_stage(self):
        self.assertEqual(audit()["errors"], [])

    def test_forged_cast(self):
        self.assert_rejected(lambda x: x["ownerCast"].update(dispatchTriggered=True))

    def test_fake_visual_acceptance(self):
        self.assert_rejected(lambda x: x["hostEvidence"].update(visualMcpAppMount="GREEN"))

    def test_fake_ci(self):
        self.assert_rejected(lambda x: x["sourceEvidence"].update(stageHeadExactCI="GREEN"))

    def test_main_merge(self):
        self.assert_rejected(lambda x: x["deployment"].update(productionMerge=True))

    def test_render_deploy(self):
        self.assert_rejected(lambda x: x["deployment"].update(renderDeployTriggered=True))

    def test_agent_release(self):
        self.assert_rejected(lambda x: x["deployment"].update(agentQuarantineLifted=True))

    def test_unknown_sha(self):
        self.assert_rejected(lambda x: x.update(upstreamHeadSha="not-a-sha"))

    def test_forged_cast_green(self):
        self.assert_rejected(lambda x: x["hostEvidence"].update(chatGptPluginCastGreen=True))


if __name__ == "__main__":
    unittest.main()

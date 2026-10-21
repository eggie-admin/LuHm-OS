#!/usr/bin/env python3
"""Negative controls against accidental four-lane plugin beta promotion."""
from __future__ import annotations
import copy
import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("pluginBetaFourLaneAudit", ROOT / "tools/pluginBetaFourLaneAudit.py")
audit = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(audit)

class FourLaneBetaSafetyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy = audit.read(audit.POLICY)
        cls.invite = audit.read(audit.INVITE)
        cls.quarantine = audit.read(audit.QUARANTINE)
        cls.plugin = audit.read(audit.REPO_PLUGIN)

    def check(self, policy=None, invite=None, quarantine=None, plugin=None):
        return audit.validate(self.policy if policy is None else policy,
                              self.invite if invite is None else invite,
                              self.quarantine if quarantine is None else quarantine,
                              self.plugin if plugin is None else plugin)

    def test_current_policy_is_reviewable_but_not_external_release(self):
        self.assertEqual(self.check(), [])
        self.assertEqual([x["id"] for x in self.policy["lanes"]], ["testing","proposed","beta","betaLts"])

    def test_each_lane_denies_auto_promotion_and_public_release(self):
        for index in range(4):
            for prop in ("autoPromote", "externalAccess", "publicRelease", "realUserData"):
                with self.subTest(lane=index,property=prop):
                    change=copy.deepcopy(self.policy)
                    change["lanes"][index][prop]=True
                    self.assertTrue(self.check(policy=change))

    def test_lts_freeze_or_proven_source_cannot_be_forged(self):
        for action in ("pinnedCockpitRollbackCommit","pinnedGodotRollbackCommit","publicVersionAssigned","immutableReleaseArtifactObserved"):
            changed=copy.deepcopy(self.policy)
            changed["lanes"][3]["freeze"][action] = True if action.endswith(("Assigned","Observed")) else "badsha"
            self.assertTrue(self.check(policy=changed))

    def test_private_plugin_and_exact_identity_remain_separate(self):
        changed=copy.deepcopy(self.policy)
        changed["currentOwnerPlugin"]["shareableExternally"]=True
        self.assertTrue(self.check(policy=changed))
        changed=copy.deepcopy(self.policy)
        changed["currentOwnerPlugin"]["version"]="0.5.2"
        self.assertTrue(self.check(policy=changed))
        changed=copy.deepcopy(self.policy)
        changed["target"]="Alex@example.com"
        self.assertTrue(self.check(policy=changed))

    def test_no_invites_workers_or_unaudited_upgrade(self):
        changed=copy.deepcopy(self.policy)
        changed["release"]["betaInviteSent"]=True
        self.assertTrue(self.check(policy=changed))
        changed=copy.deepcopy(self.policy)
        changed["gateStates"]["supportedDistribution"]="PROVED"
        self.assertTrue(self.check(policy=changed))
        changed=copy.deepcopy(self.quarantine)
        changed["activeTaskWorkersAllowed"]=True
        self.assertTrue(self.check(quarantine=changed))

    def test_cannot_self_certify_beta_readiness(self):
        proc=subprocess.run([sys.executable,str(audit.ROOT/"tools/pluginBetaFourLaneAudit.py"),"--require-beta-ready"],cwd=audit.ROOT,capture_output=True,text=True)
        self.assertEqual(proc.returncode,3,proc.stdout+proc.stderr)
        self.assertIn("BETA_READY_DENIED",proc.stdout)

if __name__=="__main__":
    unittest.main()

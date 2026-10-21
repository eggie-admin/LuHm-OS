#!/usr/bin/env python3
"""Adversarial controls for read-only LuHm OS beta candidate guard."""
from __future__ import annotations
import copy
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("pluginBetaInviteAudit", ROOT/"tools/pluginBetaInviteAudit.py")
gate = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(gate)

class PublicBetaGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = gate.read(gate.CONTRACT)
        cls.manifest = gate.read(gate.MANIFEST)
        cls.mcp = gate.read(gate.MCP)
        cls.recon = gate.read(gate.RECON)
        cls.truth = gate.read(gate.TRUTH)

    def check(self, contract=None, manifest=None, mcp=None, recon=None, truth=None):
        return gate.validate(contract if contract is not None else self.contract,
                             manifest if manifest is not None else self.manifest,
                             mcp if mcp is not None else self.mcp,
                             recon if recon is not None else self.recon,
                             truth if truth is not None else self.truth)

    def test_current_candidate_is_safe_to_review_not_release(self):
        self.assertEqual(self.check(), [])
        self.assertEqual(self.contract["status"], "CANDIDATE_SOURCE_ONLY_NOT_INVITE_READY")

    def test_forged_invites_and_publication_fail(self):
        for path, value in [
            (("release","pluginInviteSent"), True),
            (("release","githubInviteSent"), True),
            (("release","publicBetaReleased"), True),
            (("release","directoryPublished"), True),
            (("access","chatgpt","externalTesterAccess"), "GRANTED"),
            (("access","github","writeInvitationState"), "SENT"),
            (("release","crownStatus"), "GREEN"),
            (("gates","externalTesterToolInvocation"), "PROVED"),
        ]:
            with self.subTest(path=path):
                item = copy.deepcopy(self.contract)
                node = item
                for part in path[:-1]:
                    node=node[part]
                node[path[-1]]=value
                self.assertTrue(self.check(contract=item))

    def test_permissions_and_version_collisions_fail(self):
        m=copy.deepcopy(self.manifest)
        m["extensions"]["com.openai"]["interface"]["capabilities"]=["Read","Write"]
        self.assertTrue(self.check(manifest=m))
        c=copy.deepcopy(self.contract)
        c["identity"]["personalPlugin"]["version"]="0.5.2"
        self.assertTrue(self.check(contract=c))
        c=copy.deepcopy(self.contract)
        c["access"]["inviteTarget"]="tester@example.com"
        self.assertTrue(self.check(contract=c))

    def test_mcp_endpoint_and_quarantine_drift_fail(self):
        m=copy.deepcopy(self.mcp)
        m["mcpServers"]["luhm"]["url"]="http://127.0.0.1:8788/mcp"
        self.assertTrue(self.check(mcp=m))
        c=copy.deepcopy(self.contract)
        c["intendedExperience"]["independentWorkers"]="ACTIVE"
        self.assertTrue(self.check(contract=c))

    def test_external_beta_must_never_go_green_from_source_only(self):
        run=subprocess.run([sys.executable,str(ROOT/"tools/pluginBetaInviteAudit.py"),
                             "--require-beta-ready"],cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(run.returncode,3)
        self.assertIn("BETA_READY_DENIED",run.stdout)

if __name__ == "__main__":
    unittest.main()

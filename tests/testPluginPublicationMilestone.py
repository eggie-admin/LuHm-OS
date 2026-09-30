#!/usr/bin/env python3
from __future__ import annotations
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("pluginPublicationAudit", ROOT / "tools/pluginPublicationAudit.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class PluginPublicationMilestoneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.milestone = MODULE.load(MODULE.MILESTONE)
        cls.source = MODULE.load(MODULE.SOURCE)
        cls.boundary = MODULE.load(MODULE.BOUNDARY)
        cls.enterprise = MODULE.load(MODULE.ENTERPRISE)
        cls.plugin = MODULE.load(MODULE.PLUGIN)
        cls.mcp_config = MODULE.load(MODULE.MCP_CONFIG)
        cls.tests = MODULE.load(MODULE.TESTS)
        cls.server = MODULE.SERVER.read_text(encoding="utf-8")
        cls.harness_server = MODULE.HARNESS_SERVER.read_text(encoding="utf-8")
        cls.harness_module = MODULE.HARNESS_MODULE.read_text(encoding="utf-8")

    def errors(
        self,
        milestone=None,
        source=None,
        boundary=None,
        enterprise=None,
        server=None,
        harness_server=None,
        harness_module=None,
        plugin=None,
        mcp_config=None,
        tests=None,
    ):
        return MODULE.validate(
            copy.deepcopy(milestone or self.milestone),
            copy.deepcopy(source or self.source),
            copy.deepcopy(boundary or self.boundary),
            copy.deepcopy(enterprise or self.enterprise),
            server if server is not None else self.server,
            harness_server if harness_server is not None else self.harness_server,
            harness_module if harness_module is not None else self.harness_module,
            copy.deepcopy(plugin or self.plugin),
            copy.deepcopy(mcp_config or self.mcp_config),
            copy.deepcopy(tests or self.tests),
        )

    def test_current_source_package_is_valid(self):
        self.assertEqual(self.errors(), [])

    def test_publication_authority_overclaim_fails(self):
        milestone = copy.deepcopy(self.milestone)
        milestone["publicationAuthority"] = True
        self.assertTrue(self.errors(milestone=milestone))

    def test_fake_directory_publication_fails(self):
        milestone = copy.deepcopy(self.milestone)
        milestone["directoryPublicationProven"] = True
        self.assertTrue(self.errors(milestone=milestone))

    def test_crown_promotion_fails(self):
        milestone = copy.deepcopy(self.milestone)
        milestone["crownStatus"] = "GREEN"
        self.assertTrue(self.errors(milestone=milestone))

    def test_removing_publish_boundary_fails(self):
        boundary = copy.deepcopy(self.boundary)
        boundary["deny"] = [v for v in boundary["deny"] if v != "publishing"]
        self.assertTrue(self.errors(boundary=boundary))

    def test_write_capability_fails(self):
        plugin = copy.deepcopy(self.plugin)
        plugin["extensions"]["com.openai"]["interface"]["capabilities"] = ["Read", "Write"]
        self.assertTrue(self.errors(plugin=plugin))

    def test_review_test_count_drift_fails(self):
        tests = copy.deepcopy(self.tests)
        tests["negative"] = tests["negative"][:2]
        self.assertTrue(self.errors(tests=tests))

    def test_missing_challenge_endpoint_fails(self):
        server = self.server.replace('/.well-known/openai-apps-challenge', '/removed-challenge')
        self.assertTrue(self.errors(server=server))

    def test_non_harness_mcp_endpoint_fails(self):
        mcp_config = copy.deepcopy(self.mcp_config)
        mcp_config["mcpServers"]["luhm"]["url"] = "https://luhm-os-publication-green.onrender.com/mcp"
        self.assertTrue(self.errors(mcp_config=mcp_config))

    def test_missing_chat_ui_resource_fails(self):
        harness_module = self.harness_module.replace(
            'UI_RESOURCE_URI = "ui://luhm-os/cockpit-v1.html"',
            'UI_RESOURCE_URI = "ui://removed/cockpit.html"',
        )
        self.assertTrue(self.errors(harness_module=harness_module))


if __name__ == "__main__":
    unittest.main()

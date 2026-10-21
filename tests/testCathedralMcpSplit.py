"""Compatibility: same exact-commit MCP serves verified public Godot Web export."""
import ast
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOST = (ROOT / "host/mcp/luhmHarness.py").read_text()
PLUGIN = json.loads((ROOT / "plugins/luhm-os/plugin.json").read_text())
CONFIG = json.loads((ROOT / "plugins/luhm-os/mcp.json").read_text())
INSTALL = json.loads((ROOT / "doctrine/manualPluginVirginInstallV1.json").read_text())

class CathedralSplitContract(unittest.TestCase):
    def testPythonParses(self):
        ast.parse(HOST)
    def testPluginTargetsHardenedReadOnlyMcp(self):
        self.assertEqual(CONFIG["mcpServers"]["luhm"]["url"],
            "https://luhm-os-harness-green.onrender.com/mcp")
    def testVersionAndPackageMatch(self):
        self.assertEqual(PLUGIN["version"], "0.5.2")
        self.assertEqual(INSTALL["package"]["packageVersion"], PLUGIN["version"])
        self.assertEqual(INSTALL["network"]["canonicalEndpoint"],
                         CONFIG["mcpServers"]["luhm"]["url"])
    def testSameOriginPlayerAndSourceIdentity(self):
        self.assertIn('godot_frame_origin = public_origin', HOST)
        self.assertIn('"frameDomains": [godot_frame_origin] if godot_frame_origin else []', HOST)
        self.assertIn('_inspect_godot_bundle(godot_root)', HOST)
        self.assertNotIn('godot_frame_origin = EXISTING_GODOT_PUBLIC_ORIGIN if', HOST)
    def testMcpDoesNotClaimBuild(self):
        self.assertIn('"bundleIntegrity": "SHA256_PASS" if staged else "UNVERIFIED"', HOST)
        self.assertIn('"PENDING_EXPORT_OR_HTTPS_ORIGIN"', HOST)
        self.assertIn('"runtimeVerifiedInChat": False', HOST)
        self.assertIn('"buildAuthority": False', HOST)
        self.assertIn('"crownStatus": "STOP"', HOST)
    def testFrameSandboxAndFailClosedFallback(self):
        self.assertIn('sandbox="allow-scripts allow-same-origin allow-pointer-lock"', HOST)
        self.assertIn('if not public_origin or not staged:', HOST)
        self.assertIn('not _inspect_godot_bundle(godot_root)["ready"]', HOST)
        self.assertIn('SHA256SUMS.txt', HOST)
        self.assertIn('https://luhm-os-publication-site.onrender.com', HOST)
    def testNoSecondMcpClientOrNewService(self):
        self.assertEqual(list(CONFIG["mcpServers"]), ["luhm"])
    def testReadOnlyPlugin(self):
        self.assertEqual(PLUGIN["extensions"]["com.openai"]["interface"]["capabilities"], ["Read"])

if __name__ == "__main__":
    unittest.main()

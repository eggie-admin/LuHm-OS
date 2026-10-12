"""Static contract: current MCP service owns HTML, existing Godot service owns Web export."""
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
    def testExistingPlayerOriginIsExplicit(self):
        self.assertIn('EXISTING_GODOT_PUBLIC_ORIGIN = "https://luhm-os-godot-harness-green.onrender.com"', HOST)
        self.assertIn('remote_godot_candidate = public_origin == MCP_COCKPIT_PUBLIC_ORIGIN', HOST)
        self.assertIn('"frameDomains": [godot_frame_origin] if godot_frame_origin else []', HOST)
    def testMcpDoesNotClaimBuild(self):
        self.assertIn('"EXTERNAL_GODOT_FRAME_CANDIDATE"', HOST)
        self.assertIn('"runtimeVerifiedInChat": False', HOST)
        self.assertIn('"buildAuthority": False', HOST)
        self.assertIn('"crownStatus": "STOP"', HOST)
    def testFrameSandboxAndFallback(self):
        self.assertIn('sandbox="allow-scripts allow-same-origin allow-pointer-lock"', HOST)
        self.assertIn('rel="noopener noreferrer"', HOST)
        self.assertIn('frame += (', HOST)
    def testNoSecondMcpClientOrNewService(self):
        self.assertEqual(list(CONFIG["mcpServers"]), ["luhm"])
    def testReadOnlyPlugin(self):
        self.assertEqual(PLUGIN["extensions"]["com.openai"]["interface"]["capabilities"], ["Read"])

if __name__ == "__main__":
    unittest.main()

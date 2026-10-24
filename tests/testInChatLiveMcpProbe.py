import json
import unittest
from tools.inChatLiveMcpProbe import parse_rpc, parse_script, read_public, ORIGINS, TOOLS, MOBILE_TOOLS, expected_tools

class PublicMcpProbeContract(unittest.TestCase):
    def test_primaryMcpRequiresMobileTool(self):
        required = expected_tools(ORIGINS["mcp"])
        self.assertEqual(required["luhm_open_mobile_cockpit"], "ui://luhm-os/mobile-cockpit-v1.html")
        self.assertIn("luhm_open_cockpit", required)

    def test_godotPreviewNotFalselyEquatedWithPrimary(self):
        required = expected_tools(ORIGINS["godot"])
        self.assertEqual(required, TOOLS)
        self.assertNotIn("luhm_open_mobile_cockpit", required)
        self.assertEqual(len(MOBILE_TOOLS), 1)

    def test_plainJson(self):
        response = {"jsonrpc": "2.0", "id": 3, "result": {"tools": []}}
        self.assertEqual(parse_rpc(json.dumps(response).encode(), "application/json"), response)

    def test_sseEnvelope(self):
        response = {"jsonrpc": "2.0", "id": 3, "result": {"tools": []}}
        body = ("event: message\n" + "data: " + json.dumps(response) + "\n\n").encode()
        self.assertEqual(parse_rpc(body, "text/event-stream"), response)

    def test_rejectMissingSse(self):
        with self.assertRaisesRegex(ValueError, "NO_SSE_DATA"):
            parse_rpc(b"event: ping\n\n", "text/event-stream")

    def test_rejectWrongOrigin(self):
        with self.assertRaisesRegex(ValueError, "OUTSIDE_FIXED_ORIGIN"):
            read_public("https://example.com", "/mcp")

    def test_rejectRelativeWithoutSlash(self):
        with self.assertRaisesRegex(ValueError, "OUTSIDE_FIXED_ORIGIN"):
            read_public(ORIGINS["mcp"], "mcp")

    def test_rejectMissingScript(self):
        with self.assertRaisesRegex(ValueError, "COCKPIT_SCRIPT_COUNT"):
            parse_script("<html></html>")

    def test_parseSmallJs(self):
        self.assertEqual(parse_script("<script>const x = 1;</script>"), "PARSE_PASS")

    def test_parseAssembledCockpitTwoInlineScripts(self):
        page = "<html><script>const root = 1;</script><script>const deck = 2;</script></html>"
        self.assertEqual(parse_script(page), "PARSE_PASS")

    def test_rejectExternalScriptEvenWithInline(self):
        page = '<script src="https://bad.example/evil.js"></script><script>const ok = 1;</script>'
        with self.assertRaisesRegex(ValueError, "WIDGET_EXTERNAL_SCRIPT_FORBIDDEN"):
            parse_script(page)

    def test_rejectSecondScriptSyntax(self):
        with self.assertRaisesRegex(ValueError, "COCKPIT_JAVASCRIPT_PARSE_FAIL:2"):
            parse_script("<script>const valid=1;</script><script>function {bad}</script>")

    def test_rejectSyntax(self):
        with self.assertRaisesRegex(ValueError, "COCKPIT_JAVASCRIPT_PARSE_FAIL"):
            parse_script("<script>function {bad}</script>")

if __name__ == "__main__":
    unittest.main()

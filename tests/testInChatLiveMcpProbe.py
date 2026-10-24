import json
import unittest
from tools.inChatLiveMcpProbe import parse_rpc, parse_script, read_public, verify_ui_resource, ORIGINS

class PublicMcpProbeContract(unittest.TestCase):
    def test_mobileUiResource_valid(self):
        uri = "ui://luhm-os/mobile-cockpit-v1.html"
        contents = [{"uri": uri, "mimeType": "text/html;profile=mcp-app",
                     "text": "<!doctype html><script>\"ui/initialize\"</script>"}]
        self.assertEqual(verify_ui_resource(contents, uri)["mimeType"],
                         "text/html;profile=mcp-app")

    def test_mobileUiResource_wrongMime(self):
        uri = "ui://luhm-os/mobile-cockpit-v1.html"
        with self.assertRaisesRegex(ValueError, "UI_RESOURCE_WRONG_MIME"):
            verify_ui_resource([{"uri": uri, "mimeType": "text/html", "text": "<!doctype html>"}], uri)

    def test_mobileUiResource_missingBridge(self):
        uri = "ui://luhm-os/mobile-cockpit-v1.html"
        with self.assertRaisesRegex(ValueError, "UI_RESOURCE_MISSING_HOST_BRIDGE"):
            verify_ui_resource([{"uri": uri, "mimeType": "text/html;profile=mcp-app",
                                 "text": "<!doctype html><p>Content</p>"}], uri)

    def test_mobileUiResource_missingResource(self):
        with self.assertRaisesRegex(ValueError, "UI_RESOURCE_NOT_EXACTLY_ONCE"):
            verify_ui_resource([], "ui://luhm-os/mobile-cockpit-v1.html")

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

    def test_rejectSyntax(self):
        with self.assertRaisesRegex(ValueError, "COCKPIT_JAVASCRIPT_PARSE_FAIL"):
            parse_script("<script>function {bad}</script>")

if __name__ == "__main__":
    unittest.main()

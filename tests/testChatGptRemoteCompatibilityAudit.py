"""Negative-control source tests for OpenAI plugin packaging and MCP Apps metadata."""
import copy
import json
import unittest
from pathlib import Path
from tools.chatGptRemoteCompatibilityAudit import (
    ROOT, DOC, PLUGIN, MCP, HARNESS, MOBILE, PRIVACY, TERMS,
    audit, audit_data,
)

def source():
    d = json.loads((ROOT / DOC).read_text(encoding="utf-8"))
    p = json.loads((ROOT / PLUGIN).read_text(encoding="utf-8"))
    m = json.loads((ROOT / MCP).read_text(encoding="utf-8"))
    raw = [(ROOT / x).read_text(encoding="utf-8")
           for x in (HARNESS, MOBILE, PRIVACY, TERMS)]
    return d, p, m, raw

class RemoteCompatibilityTests(unittest.TestCase):
    def test_exact_source_candidate(self):
        self.assertEqual(audit(), [])

    def test_more_than_three_starter_prompts_is_rejected(self):
        d, p, m, raw = source()
        p["extensions"]["com.openai"]["interface"]["defaultPrompt"].append("Unexpected fourth starter prompt")
        self.assertIn("starterPromptLimit", audit_data(d, p, m, *raw))

    def test_http_mcp_endpoint_rejected(self):
        d, p, m, raw = source()
        m["mcpServers"]["luhm"]["url"] = "http://example.com/mcp"
        self.assertIn("stableHttpsMcp", audit_data(d, p, m, *raw))

    def test_wrong_ui_resource_uri_rejected(self):
        d, p, m, raw = source()
        raw[0] = raw[0].replace('UI_RESOURCE_URI = "ui://luhm-os/cockpit-v2.html"',
                                'UI_RESOURCE_URI = "ui://luhm-os/old-cockpit.html"')
        self.assertIn("fullUiResource", audit_data(d, p, m, *raw))

    def test_tool_without_ui_binding_rejected(self):
        d, p, m, raw = source()
        raw[0] = raw[0].replace('"ui": {"resourceUri": MOBILE_COCKPIT_RESOURCE_URI',
                                '"ui": {"resourceUri": "wrong-resource"')
        self.assertIn("descriptorUiBinding", audit_data(d, p, m, *raw))

    def test_missing_mobile_bridge_rejected(self):
        d, p, m, raw = source()
        raw[1] = raw[1].replace('"ui/notifications/tool-result"', '"ui/result-unknown"')
        self.assertIn("mobileMcpAppsBridge", audit_data(d, p, m, *raw))

    def test_falsified_android_green_rejected(self):
        d, p, m, raw = source()
        d["hostMount"]["userObserved"] = "GREEN"
        self.assertIn("androidRed", audit_data(d, p, m, *raw))

    def test_private_site_scope_preserved(self):
        d, p, m, raw = source()
        d["target"]["independentOwnedSitePlugin"]["sharing"] = "PUBLIC"
        self.assertIn("privateSite", audit_data(d, p, m, *raw))

if __name__ == "__main__":
    unittest.main()

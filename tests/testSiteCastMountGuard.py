"""Site App compatibility checks: metadata, resources and negative controls.

These fixtures do not prove the ChatGPT Android renderer loaded the app.
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from siteCastMountGuard import MOBILE_TOOL, MOBILE_URI, APP_MIME, validate


def fixture():
    return (
        {"tools": [{
            "name": MOBILE_TOOL,
            "_meta": {"ui": {"resourceUri": MOBILE_URI},
                      "openai/outputTemplate": MOBILE_URI}
        }]},
        {"contents": [{
            "uri": MOBILE_URI, "mimeType": APP_MIME,
            "_meta": {"ui": {"csp": {"connectDomains": [],
                                    "resourceDomains": [],
                                    "frameDomains": []}}},
            "text": "<!doctype html><html><script>\"ui/initialize\"</script></html>"
        }]}
    )


class SiteCastMountGuardTests(unittest.TestCase):
    def test_expected_site_tool_and_resource_shape(self):
        tools, resource = fixture()
        result = validate(tools, resource)
        self.assertEqual(result["sourceAndServerContract"], "PASS")
        self.assertEqual(result["chatGptInlineMounted"], "UNVERIFIED")
        self.assertFalse(result["siteBackendChanged"])

    def test_server_payload_is_not_ui_metadata(self):
        tools, resource = fixture()
        tools["tools"][0].pop("_meta")
        problems = validate(tools, resource)["problems"]
        self.assertIn("SITE_TOOL_UI_RESOURCE_URI_MISSING", problems)
        self.assertIn("SITE_TOOL_OUTPUT_TEMPLATE_MISSING", problems)

    def test_wrong_resource_mime_is_red(self):
        tools, resource = fixture()
        resource["contents"][0]["mimeType"] = "text/html"
        self.assertIn("SITE_MOBILE_UI_WRONG_MIME", validate(tools, resource)["problems"])

    def test_missing_host_handshake_is_red(self):
        tools, resource = fixture()
        resource["contents"][0]["text"] = "<!doctype html><p>Status JSON only</p>"
        self.assertIn("SITE_MOBILE_UI_HOST_BRIDGE_MISSING", validate(tools, resource)["problems"])

    def test_missing_resource_registration_is_red(self):
        tools, resource = fixture()
        resource["contents"] = []
        self.assertIn("SITE_MOBILE_UI_RESOURCE_NOT_UNIQUE", validate(tools, resource)["problems"])

    def test_empty_json_is_not_a_mount_receipt(self):
        result = validate({}, {})
        self.assertEqual(result["sourceAndServerContract"], "FAIL")
        self.assertEqual(result["chatGptInlineMounted"], "UNVERIFIED")


if __name__ == "__main__":
    unittest.main()

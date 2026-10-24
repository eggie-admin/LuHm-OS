"""Read-only fail-closed source/JavaScript checks for the LuHm phone cockpit.

These tests DO NOT claim that a ChatGPT Android/iPhone app mounted the UI.
"""
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "host/harness/mobileCockpitWidget.html").read_text(encoding="utf-8")
SERVER = (ROOT / "host/mcp/luhmHarness.py").read_text(encoding="utf-8")
MOBILE_URI = "ui://luhm-os/mobile-cockpit-v1.html"


def audit_mobile(html: str, server: str) -> list[str]:
    checks = {
        "resourceUri": MOBILE_URI in html or MOBILE_URI in server,
        "boundTool": 'name="luhm_open_mobile_cockpit"' in server
                     and '"resourceUri": MOBILE_COCKPIT_RESOURCE_URI' in server,
        "registeredResource": 'def luhm_mobile_cockpit_resource() -> str:' in server,
        "existingStudioPreserved": 'name="luhm_open_cockpit"' in server
                                   and 'UI_RESOURCE_URI = "ui://luhm-os/cockpit-v2.html"' in server,
        "sourceQuarantineGate": 'RED_MOBILE_AGENT_QUARANTINE_CONTRACT' in server
                                and 'company.get("registeredCount") != 15' in server,
        "noPrivilege": all(s in server for s in (
            '"readOnly": True', '"mutationAuthority": False',
            '"promotionAuthority": False', '"publicationAuthority": False',
            '"crownAuthority": False', '"testerDeviceMount": "NOT_VERIFIED"',
        )),
        "payloadValidation": 'd.schema!=="luhmOs.mobileCockpitPayload.v1"' in html
                            and 'd?.authority?.mutationAuthority!==false' in html,
        "safeDOM": ".innerHTML=" not in html and "document.write(" not in html
                   and "eval(" not in html,
        "mobileViewport": 'name="viewport"' in html and "viewport-fit=cover" in html,
        "touchTargets": "min-height:44px" in html,
        "noExternalResources": not re.search(r'<(?:script|link|img|iframe)[^>]+(?:src|href)\s*=\s*["\']https?://', html),
        "noExternalNetwork": "fetch(" not in html and "XMLHttpRequest" not in html,
        "eventBridge": '"ui/initialize"' in html
                       and '"ui/notifications/tool-result"' in html
                       and '"ui/notifications/initialized"' in html,
        "presentationTruth": 'mobile display acceptance pending' in html
                             and 'Agents: quarantined' in html,
        "releaseSeparation": all(s in html for s in (
            'data-lane="testing"', 'data-lane="proposed"',
            'data-lane="beta"', 'data-lane="betaLts"',
        )),
        "compact": len(html.encode("utf-8")) <= 12000,
    }
    return [name for name, passed in checks.items() if not passed]


class MobileCockpitEvidenceContract(unittest.TestCase):
    def test_current_source(self):
        self.assertEqual(audit_mobile(HTML, SERVER), [])

    def test_reject_fake_privilege(self):
        self.assertIn("noPrivilege", audit_mobile(HTML, SERVER.replace('"mutationAuthority": False', '"mutationAuthority": True')))

    def test_reject_missing_mobile_tool(self):
        self.assertIn("boundTool", audit_mobile(HTML, SERVER.replace('name="luhm_open_mobile_cockpit"', 'name="disabled_mobile_tool"')))

    def test_reject_html_injection(self):
        self.assertIn("safeDOM", audit_mobile(HTML + "\\ncard.innerHTML=unsafe;", SERVER))

    def test_reject_external_script(self):
        self.assertIn("noExternalResources", audit_mobile(HTML + '<script src="https://bad.example/script.js"></script>', SERVER))

    def test_reject_wrong_payload_schema(self):
        self.assertIn("payloadValidation", audit_mobile(HTML.replace(
            'd.schema!=="luhmOs.mobileCockpitPayload.v1"', 'd.schema!=="wrong.schema"'), SERVER))

    def test_embedded_javascript_parses(self):
        if not shutil.which("node"):
            self.skipTest("Node unavailable for syntax-only check")
        scripts = re.findall(r"<script(?:\\s[^>]*)?>(.*?)</script>", HTML, re.I | re.S)
        self.assertEqual(len(scripts), 1)
        with tempfile.TemporaryDirectory() as directory:
            script = Path(directory) / "mobileCockpit.js"
            script.write_text(scripts[0], encoding="utf-8")
            subprocess.run(["node", "--check", str(script)], check=True, capture_output=True, text=True)


if __name__ == "__main__":
    unittest.main()

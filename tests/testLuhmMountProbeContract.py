"""Source-only, negative-control checks for a tiny MCP Apps host-mount diagnostic."""
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
URI = "ui://luhm-os/mount-probe-v1.html"
PROBE = (ROOT / "host/harness/mountProbeWidget.html").read_text(encoding="utf-8")
SERVER = (ROOT / "host/mcp/luhmHarness.py").read_text(encoding="utf-8")

def audit(probe: str, server: str) -> list[str]:
    checks = {
        "selfContained": len(probe.encode("utf-8")) < 3500 and
                         not re.search(r'<(?:script|link|iframe|img)[^>]+(?:src|href)\s*=\s*["\']https?://',probe,re.I),
        "properUri": f'MOUNT_PROBE_RESOURCE_URI = "{URI}"' in server,
        "registeredResource": 'name="luhm-os-mount-probe"' in server and
                              'mime_type=APP_MIME_TYPE' in server and
                              'def luhm_mount_probe_resource()' in server,
        "registeredTool": 'name="luhm_open_mount_probe"' in server and
                          '"ui": {"resourceUri": MOUNT_PROBE_RESOURCE_URI' in server and
                          '"openai/outputTemplate": MOUNT_PROBE_RESOURCE_URI' in server,
        "csp": '"csp": {"connectDomains": [], "resourceDomains": [], "frameDomains": []}' in server,
        "readOnlyFallback": '"deviceMount": "NOT_VERIFIED"' in server and
                             '"readOnly": True' in server,
        "userTap": 'id="tap"' in probe and 'Touch: PASS on this screen.' in probe,
        "bridge": '"ui/initialize"' in probe and '"ui/notifications/initialized"' in probe,
        "notFakeMount": 'Only a visible and user-touched in-chat card proves host acceptance.' in server,
    }
    return [key for key, ok in checks.items() if not ok]

class MountProbeSourceTests(unittest.TestCase):
    def test_candidate(self):
        self.assertEqual(audit(PROBE,SERVER),[])

    def test_tampered_resource(self):
        self.assertIn("properUri",audit(PROBE,SERVER.replace(URI,"ui://other")))

    def test_missing_tool_binding(self):
        self.assertIn("registeredTool",audit(PROBE,SERVER.replace(
            '"ui": {"resourceUri": MOUNT_PROBE_RESOURCE_URI','"ui": {"resourceUri": "unlinked"')))

    def test_fake_device_mount(self):
        self.assertIn("readOnlyFallback",audit(PROBE,SERVER.replace(
            '"deviceMount": "NOT_VERIFIED"','"deviceMount": "GREEN"')))

    def test_no_unreviewed_remote_scripts(self):
        mutated=PROBE.replace("</head>","<script src='https://evil.example/code.js'></script></head>")
        self.assertIn("selfContained",audit(mutated,SERVER))

    def test_actual_inline_javascript_parses(self):
        matches=re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>",PROBE,re.S|re.I)
        self.assertEqual(len(matches),1)
        with tempfile.TemporaryDirectory() as root:
            f=Path(root)/"mountProbe.js"
            f.write_text(matches[0],encoding="utf-8")
            check=subprocess.run(["node","--check",str(f)],capture_output=True,text=True)
            self.assertEqual(check.returncode,0,check.stderr)

if __name__=="__main__":
    unittest.main()

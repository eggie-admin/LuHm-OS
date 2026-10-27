"""Read-only fail-closed source/JavaScript checks for the LuHm phone cockpit.

These tests DO NOT claim that a ChatGPT Android/iPhone app mounted the UI.
"""
from pathlib import Path
import ast
import copy
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from typing import Any

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
        "compact": len(html.encode("utf-8")) <= 16000,
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

    def test_mobile_resource_has_declared_widget_origin_when_hosted(self):
        # A resource URI in a JSON tool result is not renderable UI metadata.
        # On a hosted MCP app, include the exact configured origin in resource _meta.ui.
        start = SERVER.index('    @server.resource(\n        MOBILE_COCKPIT_RESOURCE_URI,')
        end = SERVER.index('    @server.tool(', start)
        resource_registration = SERVER[start:end]
        self.assertIn('"domain": public_origin', resource_registration)
        self.assertIn('"csp": {"connectDomains": [], "resourceDomains": [], "frameDomains": []}', resource_registration)

    def test_embedded_javascript_parses(self):
        if not shutil.which("node"):
            self.skipTest("Node unavailable for syntax-only check")
        scripts = re.findall(r"<script(?:\\s[^>]*)?>(.*?)</script>", HTML, re.I | re.S)
        self.assertEqual(len(scripts), 1)
        with tempfile.TemporaryDirectory() as directory:
            script = Path(directory) / "mobileCockpit.js"
            script.write_text(scripts[0], encoding="utf-8")
            subprocess.run(["node", "--check", str(script)], check=True, capture_output=True, text=True)


    def test_mobile_tool_real_function_returns_readonly_roster(self):
        tool = self._tool_function({"state": "QUARANTINED", "registeredCount": 15,
                                   "activeTaskWorkersAllowed": False})
        out = tool()
        self.assertEqual(out["schema"], "luhmOs.mobileCockpitPayload.v1")
        self.assertEqual(out["resourceUri"], MOBILE_URI)
        self.assertEqual(out["roster"]["roles"][0]["agentId"], "lum")
        self.assertEqual(out["companyQuarantine"]["state"], "QUARANTINED")
        self.assertFalse(out["companyQuarantine"]["activeTaskWorkersAllowed"])
        self.assertTrue(out["authority"]["readOnly"])
        self.assertFalse(out["authority"]["mutationAuthority"])
        self.assertFalse(out["authority"]["publicationAuthority"])
        self.assertFalse(out["authority"]["crownAuthority"])
        self.assertEqual(out["testerDeviceMount"], "NOT_VERIFIED")
        self.assertEqual(out["sourceRef"], "SOURCE_NOT_DEPLOYED")
        self.assertEqual(out["glassDock"]["schema"], "luhmOs.glassPluginDock.v1")
        self.assertEqual([x["id"] for x in out["glassDock"]["modules"]],
                         ["music", "avatars", "yume", "social", "admin"])

    def test_mobile_tool_rejects_count_and_state_drift(self):
        for policy in (
            {"state": "QUARANTINED", "registeredCount": 16},
            {"state": "UNKNOWN", "registeredCount": 15},
            {"state": "PUBLISHED", "registeredCount": 15},
        ):
            with self.subTest(policy=policy):
                tool = self._tool_function(policy)
                with self.assertRaisesRegex(RuntimeError, "RED_MOBILE_AGENT_QUARANTINE_CONTRACT"):
                    tool()

    def test_mobile_resource_body_matches_host_file(self):
        tree = ast.parse(SERVER)
        registration = next(
            node for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "register_harness"
        )
        resource = next(
            node for node in registration.body
            if isinstance(node, ast.FunctionDef) and node.name == "luhm_mobile_cockpit_resource"
        )
        isolated = copy.deepcopy(resource)
        isolated.decorator_list = []
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "mobileCockpitWidget.html"
            path.write_text(HTML, encoding="utf-8")
            scope = {"mobile_widget_path": path}
            exec(compile(ast.fix_missing_locations(ast.Module(body=[isolated], type_ignores=[])),
                         "host/mcp/luhmHarness.py", "exec"), scope)
            self.assertEqual(scope["luhm_mobile_cockpit_resource"](), HTML)

    @staticmethod
    def _tool_function(policy):
        """Execute the actual undecorated GitHub tool body, not a source-text mock."""
        tree = ast.parse(SERVER)
        registration = next(
            node for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "register_harness"
        )
        fn = next(
            node for node in registration.body
            if isinstance(node, ast.FunctionDef) and node.name == "luhm_open_mobile_cockpit"
        )
        body = copy.deepcopy(fn)
        body.decorator_list = []
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            doctrine = root / "doctrine"
            doctrine.mkdir()
            (doctrine / "companyWideOperationalQuarantineV1.json").write_text(
                json.dumps(policy), encoding="utf-8")
            # The function consumes policy before returning. Bind a callable
            # which retains a concrete rooted fixture after this context exits.
            original_read = Path.read_text
            policy_bytes = json.dumps(policy)
            class FixturePath:
                def __truediv__(self, part):
                    return self
                def read_text(self, encoding="utf-8"):
                    return policy_bytes
            scope = {
                "root": FixturePath(), "json": json, "os": os, "Any": Any,
                "MOBILE_COCKPIT_RESOURCE_URI": MOBILE_URI,
                "glass_dock": json.loads((ROOT / "doctrine/glassPluginDockV1.json").read_text(encoding="utf-8")),
                "status_provider": lambda: {"sourceRef": "SOURCE_NOT_DEPLOYED",
                                            "sourceTruthStatus": "SOURCE_ONLY"},
                "roster_provider": lambda: {"roles": [{"agentId": "lum", "displayName": "Lum"}]},
            }
            exec(compile(ast.fix_missing_locations(ast.Module(body=[body], type_ignores=[])),
                         "host/mcp/luhmHarness.py", "exec"), scope)
            return scope["luhm_open_mobile_cockpit"]


if __name__ == "__main__":
    unittest.main()

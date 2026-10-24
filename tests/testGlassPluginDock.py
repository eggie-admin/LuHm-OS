"""Fail-closed glass dock Canon, interface, and browser portability tests."""
from __future__ import annotations
import copy
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = json.loads((ROOT / "doctrine/glassPluginDockV1.json").read_text(encoding="utf-8"))
MOBILE = (ROOT / "host/harness/mobileCockpitWidget.html").read_text(encoding="utf-8")
FULL = (ROOT / "host/harness/widget.html").read_text(encoding="utf-8")
SERVER = (ROOT / "host/mcp/luhmHarness.py").read_text(encoding="utf-8")
ROSTER = ["music", "avatars", "yume", "social", "admin"]


def audit(policy: dict, mobile: str, full: str, server: str) -> list[str]:
    checks = {
        "schema": policy.get("schema") == "luhmOs.glassPluginDock.v1",
        "crown": policy.get("crownStatus") == "STOP" and policy.get("promotion") is False,
        "oneIcon": policy.get("launcher", {}).get("icon") == "settings" and
                   mobile.count('id="glassToggle"') == 1 and
                   full.count('id="studioGlassToggle"') == 1,
        "fiveModules": [i.get("id") for i in policy.get("modules", [])] == ROSTER,
        "sourceOnly": all(i.get("status") == "SOURCE_BOUNDARY_ONLY" and
                          isinstance(i.get("chatIntent"), str) and
                          20 < len(i["chatIntent"]) <= 1000 for i in policy.get("modules", [])),
        "noHostHijack": policy.get("presentation", {}).get("hostPageOverlay") is False and
                        "window.parent.document" not in mobile and
                        "window.parent.document" not in full,
        "noImplicitExecution": policy.get("orchestration", {}).get("companyQuarantineEnforced") is True
                               and policy.get("hostCapabilities", {}).get("serverToolWrites") is False
                               and policy.get("hostCapabilities", {}).get("providerPlayback") is False,
        "iosReality": ("Canary" not in policy.get("kiosk", {}).get("iosPreferredTest", "") or
                      "not Canary" in policy.get("kiosk", {}).get("iosPreferredTest", "")) and
                      policy.get("kiosk", {}).get("browserIsHeadlessOnMobile") is False and
                      policy.get("kiosk", {}).get("escapeMustRemainAvailable") is True,
        "bothPayloads": server.count('"glassDock": glass_dock') == 2,
        "glassModelBridge": "sendFollowUp(item.chatIntent)" in full and
                            'window.openai.sendFollowUpMessage({prompt})' in mobile and
                            '"ui/message"' in mobile,
        "userGesture": 'action.addEventListener("click",()=>sendDockIntent(item))' in mobile and
                       'btn.addEventListener("click",async()=>{' in full,
        "focusEscape": 'e.key==="Escape"' in mobile and
                       'event.key==="Escape"' in full and
                       'aria-expanded="false"' in mobile and
                       'aria-expanded="false"' in full,
        "safeDom": ".innerHTML=" not in mobile and ".innerHTML=" not in full and
                   "document.write(" not in mobile and "document.write(" not in full,
        "noAutoExternalMedia": "<iframe" not in mobile and
                               "youtube.com/embed" not in mobile and "spotify.com/embed" not in mobile,
        "hostExpansionOptional": "window.openai?.requestDisplayMode" in mobile and
                                 "window.openai?.requestDisplayMode" in full,
    }
    return [name for name, passed in checks.items() if not passed]


class GlassPluginDockTests(unittest.TestCase):
    def test_current_dock(self):
        self.assertEqual(audit(POLICY, MOBILE, FULL, SERVER), [])

    def test_reject_auto_publish(self):
        fake = copy.deepcopy(POLICY)
        fake["promotion"] = True
        self.assertIn("crown", audit(fake, MOBILE, FULL, SERVER))

    def test_reject_unsupported_ios_canary(self):
        fake = copy.deepcopy(POLICY)
        fake["kiosk"]["iosPreferredTest"] = "Chrome Canary iOS"
        self.assertIn("iosReality", audit(fake, MOBILE, FULL, SERVER))

    def test_reject_script_host_hijack(self):
        self.assertIn("noHostHijack", audit(POLICY, MOBILE + "\nwindow.parent.document", FULL, SERVER))

    def test_reject_ghost_module(self):
        fake = copy.deepcopy(POLICY)
        fake["modules"].append({"id": "ghost"})
        self.assertIn("fiveModules", audit(fake, MOBILE, FULL, SERVER))

    def test_reject_unbounded_model_action(self):
        fake = copy.deepcopy(POLICY)
        fake["modules"][0]["status"] = "RUNNING"
        self.assertIn("sourceOnly", audit(fake, MOBILE, FULL, SERVER))


if __name__ == "__main__":
    unittest.main()

"""Fail-closed static contract for the existing LuHm MCP Apps HTML widget."""
from pathlib import Path
import unittest

SOURCE = Path("host/harness/widget.html").read_text(encoding="utf-8")

def auditWidget(source: str) -> list[str]:
    errors = []
    checks = {
        "htmlSink": ".innerHTML=" not in source,
        "safeCommandDOM": 'strong.textContent=item.icon+" "+item.debugVerb' in source and 'detail.textContent=item.kebab' in source,
        "schema": 'candidate.schema!=="luhmOs.inChatExperiencePayload.v1"' in source,
        "surface": 'candidate.surface!=="mcp-app"' in source,
        "resourceUri": 'candidate?.experience?.runtime?.resourceUri!=="ui://luhm-os/cockpit-v2.html"' in source,
        "authority": all(part in source for part in (
            "candidate?.authority?.readOnly!==true",
            "candidate?.authority?.mutationAuthority!==false",
            "candidate?.authority?.publicationAuthority!==false",
            "candidate?.authority?.greenAuthority!==false",
        )),
        "visibleFailure": 'MCP CONTRACT VERIFY' in source and '$("truth").textContent="VERIFY"' in source,
        "noConfiguredGreen": all(part not in source for part in (
            'csp:"PRESENT"',
            'https:origin.startsWith?.("https://")?"PRESENT"',
            'renderOrigin:origin.includes?.("onrender.com")?"PRESENT"',
            'x.className=v==="PRESENT"?"ok":"verify"',
        )),
        "hostBridge": all(part in source for part in (
            'window.openai?.toolOutput',
            'ui/initialize',
            'ui/notifications/tool-result',
            'ui/notifications/initialized',
        )),
    }
    return [key for key, passed in checks.items() if not passed]

class InChatWidgetEvidenceContract(unittest.TestCase):
    def test_currentWidget(self):
        self.assertEqual(auditWidget(SOURCE), [])

    def test_rejectUnsafeSink(self):
        self.assertIn("htmlSink", auditWidget(SOURCE + "\nb.innerHTML=untrusted;"))

    def test_rejectForgedGreen(self):
        self.assertIn("noConfiguredGreen", auditWidget(SOURCE + '\ncsp:"PRESENT"'))

    def test_rejectMissingSchemaGuard(self):
        self.assertIn("schema", auditWidget(SOURCE.replace('candidate.schema!=="luhmOs.inChatExperiencePayload.v1"', "true")))

    def test_rejectMissingAuthorityGuard(self):
        self.assertIn("authority", auditWidget(SOURCE.replace("candidate?.authority?.mutationAuthority!==false", "true")))

    def test_rejectMissingResourceBinding(self):
        self.assertIn("resourceUri", auditWidget(SOURCE.replace('candidate?.experience?.runtime?.resourceUri!=="ui://luhm-os/cockpit-v2.html"', "true")))

if __name__ == "__main__":
    unittest.main()

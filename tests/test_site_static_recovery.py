"""No-network contract tests for the Site static CAST recovery source candidate."""
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "host" / "mcp" / "site-static-recovery.py"
SPEC = importlib.util.spec_from_file_location("siteStaticRecovery", MODULE)
site = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = site
SPEC.loader.exec_module(site)


class FakeMcpServer:
    def __init__(self):
        self.resources = {}
        self.tools = {}

    def resource(self, uri, **metadata):
        def decorator(handler):
            if uri in self.resources:
                raise AssertionError("duplicate resource")
            self.resources[uri] = (metadata, handler)
            return handler
        return decorator

    def tool(self, *, name, **metadata):
        def decorator(handler):
            if name in self.tools:
                raise AssertionError("duplicate tool")
            self.tools[name] = (metadata, handler)
            return handler
        return decorator


class SiteStaticRecoveryTests(unittest.TestCase):
    def test_html_is_self_contained_and_touchable(self):
        html = site.static_html()
        self.assertIn("LuHm", html)
        self.assertIn('id="touch"', html)
        self.assertIn('method:"ui/initialize"', html)
        self.assertIn('method:"ui/notifications/initialized"', html)
        self.assertIn("textContent=", html)
        self.assertLess(len(html.encode("utf-8")), 12_000)
        self.assertNotIn("<script src=", html)
        self.assertNotIn("fetch(", html)
        self.assertNotIn("https://", html)

    def test_both_existing_tools_bind_to_registered_versioned_html(self):
        server = FakeMcpServer()
        site.register_site_static_recovery(
            server, status_provider=lambda: {
                "sourceRef": "a"*40, "sourceTruthStatus": "AMBER_PROPOSED_SEAL_OF_TRUTH"})
        self.assertEqual(set(server.tools), set(site.RESOURCES))
        self.assertEqual(set(server.resources), set(site.RESOURCES.values()))
        for name, uri in site.RESOURCES.items():
            with self.subTest(name=name):
                metadata, tool = server.tools[name]
                rmeta, resource = server.resources[uri]
                self.assertEqual(metadata["meta"]["ui"]["resourceUri"], uri)
                self.assertEqual(metadata["meta"]["openai/outputTemplate"], uri)
                self.assertEqual(rmeta["mime_type"], site.APP_MIME)
                self.assertEqual(rmeta["meta"]["ui"]["csp"], site.CSP)
                self.assertIn("<!doctype html>", resource())
                value = tool()
                self.assertEqual(value["sourceRef"], "a"*40)
                self.assertTrue(value["readOnly"])
                self.assertFalse(value["agentExecution"])
                self.assertFalse(value["publication"])
                self.assertEqual(value["crown"], "STOP")
                self.assertIn("UNVERIFIED", value["status"])

    def test_reject_external_assets_and_oversized_html(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as td:
            file = Path(td) / "index.html"
            original = site.static_html()
            for tampered in (original.replace("</body>", "<script src='https://evil.example/x.js'></script></body>"),
                             original + ("x"*12_001),
                             "<html>No doctype</html>"):
                file.write_text(tampered, encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "RED_STATIC_CAST_RESOURCE"):
                    site.static_html(file)

    def test_failure_to_read_status_does_not_enable_authority(self):
        fake = FakeMcpServer()
        site.register_site_static_recovery(fake, status_provider=lambda: "bad provider")
        for _, (_, call) in fake.tools.items():
            payload = call()
            self.assertEqual(payload["sourceRef"], "UNVERIFIED")
            self.assertFalse(payload["agentExecution"])


if __name__ == "__main__":
    unittest.main()

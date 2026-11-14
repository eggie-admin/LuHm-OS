"""Read-only source and localhost integration tests for Firefox Antenna."""
import http.client
import json
from pathlib import Path
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.parse import urlsplit

from host.antenna import luhmLocalAntenna as antenna

ROOT = Path(__file__).resolve().parents[1]


class AntennaTests(unittest.TestCase):
    def test_source_contract_and_shell_budget(self):
        s = antenna.make_status(ROOT, source="a" * 40)
        self.assertEqual(s["mode"], "READ_ONLY")
        self.assertEqual(s["updateState"], "CHECK_ONLY_NO_INSTALL")
        self.assertEqual(s["crownStatus"], "STOP")
        self.assertLessEqual(s["shellBytes"], 100_000_000)
        self.assertFalse(s["remoteManifestChecked"])
        self.assertFalse(s["agentExecution"])
        self.assertFalse(s["signedXpiInstalled"])
        self.assertFalse(s["physicalFirefoxX11Proven"])

    def test_ref_invariant_rejects_fake_source(self):
        with self.assertRaises(ValueError):
            antenna.make_status(ROOT, source="../untrusted")

    def test_extension_permissions_are_narrow(self):
        manifest = json.loads(
            (ROOT / "plugins/luhm-firefox-antenna/manifest.json").read_text()
        )
        self.assertEqual(manifest["manifest_version"], 3)
        self.assertEqual(manifest["host_permissions"], ["http://127.0.0.1:8765/*"])
        self.assertEqual(manifest["permissions"], [])
        self.assertNotIn("content_scripts", manifest)
        self.assertNotIn("background", manifest)
        self.assertNotIn("update_url", manifest.get("browser_specific_settings", {}).get("gecko", {}))
        for name in antenna.SHELL_PATHS:
            self.assertFalse((ROOT / antenna.EXTENSION_DIR / name).is_symlink())

    def test_public_shell_contains_no_remote_script_injection(self):
        html = (ROOT / "plugins/luhm-firefox-antenna/popup.html").read_text()
        script = (ROOT / "plugins/luhm-firefox-antenna/popup.js").read_text()
        self.assertNotIn("innerHTML", script)
        self.assertNotIn("eval(", script)
        self.assertNotIn("document.write", script)
        self.assertNotIn("<script src=\"https:", html)
        self.assertIn("textContent", script)
        self.assertNotIn("install", html.lower().split("<footer>")[0].split("<div class=\"controls\">")[1].split("</div>")[0])

    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), antenna.make_handler(ROOT))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)

    def request(self, method, path, *, host=None, origin=None):
        port = self.server.server_port
        conn = http.client.HTTPConnection("127.0.0.1", port, timeout=4)
        headers = {"Host": host or f"127.0.0.1:{port}"}
        if origin is not None:
            headers["Origin"] = origin
        conn.request(method, path, headers=headers)
        response = conn.getresponse()
        body = response.read()
        result = (response.status, dict(response.getheaders()), body)
        conn.close()
        return result

    def test_localhost_get_and_head(self):
        status, headers, body = self.request("GET", "/antenna/v1/status")
        self.assertEqual(status, 200)
        self.assertEqual(headers["Cache-Control"], "no-store")
        self.assertNotIn("Access-Control-Allow-Origin", headers)
        data = json.loads(body)
        self.assertEqual(data["schema"], "luhmOs.firefoxAntennaStatus.v1")
        self.assertEqual(data["mode"], "READ_ONLY")
        self.assertEqual(self.request("HEAD", "/antenna/v1/status")[0], 200)
        self.assertEqual(self.request("HEAD", "/antenna/v1/status")[2], b"")

    def test_kiosk_static_popup(self):
        for route in ("/", "/popup.css", "/popup.js"):
            code, _, body = self.request("GET", route)
            self.assertEqual(code, 200)
            self.assertGreater(len(body), 10)
        self.assertEqual(self.request("GET", "/manifest.json")[0], 404)
        self.assertEqual(self.request("GET", "/../doctrine/currentSourceTruthV3.json")[0], 404)
        self.assertEqual(self.request("GET", "/antenna/v1/status?exec=shell")[0], 404)

    def test_host_origin_and_mutation_refused(self):
        port = self.server.server_port
        self.assertEqual(self.request("GET", "/", host="attacker.example")[0], 403)
        self.assertEqual(self.request("GET", "/", origin="https://evil.example")[0], 403)
        self.assertEqual(self.request("GET", "/", origin="moz-extension://addon-test")[0], 200)
        for method in ("POST", "PUT", "DELETE"):
            self.assertEqual(self.request(method, "/antenna/v1/status")[0], 405)


if __name__ == "__main__":
    unittest.main()

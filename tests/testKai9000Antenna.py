import http.client
import importlib.util
import json
from pathlib import Path
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("antenna", Path(__file__).resolve().parents[1] / "tools/kai9000Antenna.py")
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)


class AntennaTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "antenna.html").write_text("antenna")
        (self.root / "assets").mkdir()
        (self.root / "assets/app-123.js").write_text("asset")
        (self.root / ".env").write_text("secret")
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), app.handler_for(self.root))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.temp.cleanup()

    def request(self, path="/", method="GET", headers=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.server.server_address[1], timeout=3)
        try:
            conn.request(method, path, headers=headers or {})
            response = conn.getresponse()
            return response.status, response.read(), dict(response.getheaders())
        finally:
            conn.close()

    def test_capabilities_do_not_claim_execution(self):
        with patch.object(app.shutil, "which", return_value=None):
            code, body, _ = self.request("/api/capabilities")
        data = json.loads(body)
        self.assertEqual(code, 200)
        self.assertFalse(data["executionEnabled"])
        self.assertFalse(data["runtimeExecutionProven"])
        self.assertFalse(any(data["commandDiscovery"].values()))

    def test_rebinding_and_cross_site_requests_rejected(self):
        for headers in ({"Host": "evil.example"}, {"Origin": "https://evil.example"}, {"Sec-Fetch-Site": "cross-site"}):
            self.assertEqual(self.request("/api/capabilities", headers=headers)[0], 403)

    def test_no_paths_or_writes(self):
        for path in ("/.env", "/../.env", "/assets/../.env", "/assets/%2e%2e/.env", "/?token=secret"):
            self.assertEqual(self.request(path)[0], 404)
        for method in ("POST", "PUT", "DELETE"):
            self.assertEqual(self.request("/api/capabilities", method)[0], 405)

    def test_assets_and_head(self):
        self.assertEqual(self.request()[:2], (200, b"antenna"))
        code, body, headers = self.request("/assets/app-123.js", "HEAD")
        self.assertEqual((code, body), (200, b""))
        self.assertIn("connect-src 'self'", headers["Content-Security-Policy"])

    def test_symlink_escape(self):
        with tempfile.TemporaryDirectory() as outside:
            private = Path(outside) / "secret.js"
            private.write_text("secret")
            (self.root / "assets/private.js").symlink_to(private)
            self.assertEqual(self.request("/assets/private.js")[0], 404)


if __name__ == "__main__":
    unittest.main()

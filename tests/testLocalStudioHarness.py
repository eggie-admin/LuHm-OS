import http.client
import importlib.util
from pathlib import Path
import tempfile
import threading
import unittest

spec = importlib.util.spec_from_file_location("localStudioHarness", Path(__file__).resolve().parents[1] / "tools/localStudioHarness.py")
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)


class localStudioTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name) / "dist"
        root.mkdir()
        (root / "index.html").write_text("LuHm-OS")
        (root / "_headers").write_text("/*\n  Content-Security-Policy: default-src 'none'; script-src 'self'\n")
        (root / "folder").mkdir()
        (root / ".secret").write_text("never serve")
        outside = Path(self.temp.name) / "private.txt"
        outside.write_text("never serve")
        (root / "escape.txt").symlink_to(outside)
        (root / "escapeDir").mkdir()
        (root / "escapeDir/index.html").symlink_to(outside)
        self.server = harness.createServer(root, 0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.temp.cleanup()

    def request(self, path="/", host=None, method="GET"):
        client = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        client.request(method, path, headers={} if host is None else {"Host": host})
        response = client.getresponse()
        result = response.status, dict(response.getheaders()), response.read()
        client.close()
        return result

    def testBundleAndPolicy(self):
        status, headers, body = self.request()
        self.assertEqual(status, 200)
        self.assertEqual(body, b"LuHm-OS")
        self.assertEqual(headers["X-Content-Type-Options"], "nosniff")
        self.assertIn("script-src 'self'", headers["Content-Security-Policy"])
        self.assertEqual(self.server.server_address[0], "127.0.0.1")

    def testBoundaryAttacks(self):
        for path in ["/.secret", "/%2e%2e/private.txt", "/escape.txt", "/escapeDir/", "/%00", "/a%5cb"]:
            with self.subTest(path=path):
                self.assertEqual(self.request(path)[0], 403)
        self.assertEqual(self.request(host="attacker.example")[0], 403)
        self.assertEqual(self.request("/folder/")[0], 404)
        self.assertEqual(self.request(method="POST")[0], 501)


if __name__ == "__main__":
    unittest.main()

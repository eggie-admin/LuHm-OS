"""Unprivileged offline safety and HTTP behavior tests for KAI9000."""
import http.client
import importlib.util
from pathlib import Path
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / 'tools/kai9000LocalCockpit.py'
SPEC = importlib.util.spec_from_file_location('kai9000_local', MOD)
app = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(app)


class TestServer(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.root = Path(self.dir.name)
        for relative, _ in app.ASSETS.values():
            target = self.root / relative
            target.parent.mkdir(exist_ok=True, parents=True)
            target.write_text('asset-' + relative)
        (self.root / 'private-key.txt').write_text('secret')
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), app.handler_for(self.root))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)
        self.dir.cleanup()

    def request(self, method, url):
        client = http.client.HTTPConnection('127.0.0.1', self.server.server_address[1], timeout=3)
        try:
            client.request(method, url)
            res = client.getresponse()
            return res.status, res.read(), dict(res.getheaders())
        finally:
            client.close()

    def test_allowlisted_asset_and_headers(self):
        status, body, headers = self.request('GET', '/')
        self.assertEqual(status, 200)
        self.assertEqual(body, b'asset-index.html')
        self.assertIn("connect-src 'none'", headers['Content-Security-Policy'])
        self.assertEqual(headers['X-Content-Type-Options'], 'nosniff')

    def test_all_assets_must_exist(self):
        self.assertEqual(app.missing_assets(self.root), [])
        (self.root / 'app.js').unlink()
        self.assertEqual(app.missing_assets(self.root), ['app.js'])

    def test_no_secret_or_traversal(self):
        for url in ('/private-key.txt', '/.env', '/tools/secret', '/%2e%2e/private-key.txt', '/app.js?q=1'):
            self.assertEqual(self.request('GET', url)[0], 404, url)

    def test_no_mutations_or_cross_domain(self):
        for method in ('POST', 'PUT', 'DELETE'):
            self.assertEqual(self.request(method, '/index.html')[0], 405)

    def test_health_and_head(self):
        self.assertEqual(self.request('GET', '/health')[:2], (200, b'LOCAL_COCKPIT_READY\n'))
        self.assertEqual(self.request('HEAD', '/index.html')[:2], (200, b''))

    def test_no_symlink_escape(self):
        outside = self.root.parent / ('kai9000-secret-' + self.root.name)
        outside.write_text('private')
        try:
            (self.root / 'app.js').unlink()
            (self.root / 'app.js').symlink_to(outside)
            self.assertEqual(self.request('GET', '/app.js')[0], 404)
        finally:
            outside.unlink()

    def test_loopback_explicit(self):
        self.assertIn("('127.0.0.1', args.port)", MOD.read_text())
        self.assertNotIn('0.0.0.0', MOD.read_text())

    def test_termux_shell_does_not_use_root_or_public_x(self):
        bash = (ROOT / 'tools/kai9000TermuxX11.sh').read_text()
        for unsafe in ('sudo ', 'su -c', 'setenforce 0', 'xhost +', 'pkill -f', 'rm -rf', '0.0.0.0'):
            self.assertNotIn(unsafe, bash)
        self.assertIn('termux-x11 "$DISPLAY_ID" -tag "$TAG"', bash)
        self.assertIn('npm ci --ignore-scripts', bash)


if __name__ == '__main__':
    unittest.main()

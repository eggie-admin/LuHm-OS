"""Actual local HTTP, SQLite, CSRF and story-run tests, without root or third-party deps."""
import http.client
import json
import tempfile
import threading
import unittest
from pathlib import Path

from tools.rootlessCastCockpit import init_db, read_state, response_state, serve, advance, reset, STORY


class TestRootlessCastCockpit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.db = Path(cls.temp.name) / 'story.sqlite3'
        cls.http = serve(cls.db, port=0)
        cls.port = cls.http.server_port
        cls.background = threading.Thread(target=cls.http.serve_forever, daemon=True)
        cls.background.start()
        cls.origin = f'http://127.0.0.1:{cls.port}'

    @classmethod
    def tearDownClass(cls):
        cls.http.shutdown()
        cls.http.server_close()
        cls.background.join(timeout=3)
        cls.temp.cleanup()

    def call(self, method, path, data=None, headers=None):
        connection = http.client.HTTPConnection('127.0.0.1', self.port, timeout=3)
        if data is not None:
            data = json.dumps(data)
        connection.request(method, path, data, {'Host': f'127.0.0.1:{self.port}', **(headers or {})})
        response = connection.getresponse()
        body = response.read()
        code = response.status
        security = dict(response.getheaders())
        connection.close()
        return code, json.loads(body) if security.get('Content-Type','').startswith('application/json') else body, security

    def test_01_python_only_no_root_health(self):
        code, value, headers = self.call('GET', '/api/health')
        self.assertEqual(code, 200)
        self.assertEqual(value['databaseLayer'], 'USERSPACE_SQLITE_NOT_FIRMWARE')
        self.assertFalse(value['androidApkBuilt'])
        self.assertEqual(value['crown'], 'STOP')
        self.assertIn("default-src 'self'", headers['Content-Security-Policy'])

    def test_02_html_css_js_no_cdn(self):
        for url, kind in [('/', 'text/html'), ('/app.css', 'text/css'), ('/app.js', 'text/javascript'),
                          ('/manifest.webmanifest', 'application/manifest+json'), ('/icon.svg', 'image/svg+xml')]:
            code, content, headers = self.call('GET', url)
            self.assertEqual(code, 200)
            self.assertIn(kind, headers['Content-Type'])
            self.assertGreater(len(content), 20)
        self.assertNotIn(b'https://', self.call('GET','/')[1])

    def test_webgl2_original_mesh_static_route(self):
        status, code, headers = self.call('GET', '/avatar3d.mjs')
        self.assertEqual(status,200)
        self.assertIn('text/javascript',headers['Content-Type'])
        self.assertIn(b'getContext("webgl2"',code)
        html = self.call('GET','/')[1]
        self.assertIn(b'id="avatar-3d"',html)
        self.assertIn(b'id="avatar-2d"',html)
        self.assertIn(b'type="module"',html)

    def test_03_origin_denied(self):
        code, val, _ = self.call('POST', '/api/reset', {'revision':0}, {'Origin':'https://attacker.example','Content-Type':'application/json'})
        self.assertEqual(code, 403)
        self.assertEqual(val['error'], 'CROSS_ORIGIN_DENIED')

    def test_04_no_missing_origin(self):
        code, _, _ = self.call('POST', '/api/reset', {'revision':0}, {'Content-Type':'application/json'})
        self.assertEqual(code, 403)

    def test_05_host_rebinding_denied(self):
        code, val, _ = self.call('GET', '/api/state', headers={'Host':'attack.example'})
        self.assertEqual(code, 403)
        self.assertEqual(val['error'], 'INVALID_HOST')

    def test_06_choice_and_revision(self):
        before = self.call('GET','/api/state')[1]
        self.assertIn(before['nodeId'], {'arrival','studio','practice','rehearsalEnd'})
        code, after, _ = self.call('POST','/api/reset', {'revision': before['revision']}, {'Origin':self.origin,'Content-Type':'application/json'})
        self.assertEqual(code, 200)
        self.assertEqual(after['nodeId'], 'arrival')
        code, nxt, _ = self.call('POST', '/api/choice',{'revision':after['revision'],'choice':1},{'Origin':self.origin,'Content-Type':'application/json'})
        self.assertEqual(code,200)
        self.assertEqual(nxt['nodeId'],'studio')
        self.assertEqual(nxt['affinity'], 0)
        self.assertEqual(nxt['revision'], after['revision']+1)
        code, val, _ = self.call('POST','/api/choice', {'revision':after['revision'],'choice':1},{'Origin':self.origin,'Content-Type':'application/json'})
        self.assertEqual(code,409)
        self.assertEqual(val['error'],'INVALID_OR_STALE_COMMAND')

    def test_07_typed_sqlite_sandbox(self):
        self.assertEqual(self.db.stat().st_mode & 0o777,0o600)
        self.assertEqual(self.db.parent.stat().st_mode & 0o777,0o700)
        import sqlite3
        with sqlite3.connect(self.db) as conn:
            mode = conn.execute('PRAGMA journal_mode').fetchone()[0]
            self.assertEqual(mode.lower(),'wal')
            version = conn.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='story_state'").fetchone()[0]
            self.assertEqual(version,1)

    def test_08_no_path_traversal(self):
        code, _, _ = self.call('GET','/../../../../etc/passwd')
        self.assertEqual(code,404)

    def test_09_reject_bad_content_type(self):
        code, _, _ = self.call('POST','/api/reset', {'revision':1},{'Origin':self.origin,'Content-Type':'text/plain'})
        self.assertEqual(code,415)

    def test_10_reject_json_command_injection(self):
        before = self.call('GET','/api/state')[1]
        code, _, _ = self.call('POST','/api/choice', {'revision':before['revision'],'choice':'__import__("os")'},
                               {'Origin':self.origin,'Content-Type':'application/json'})
        self.assertEqual(code,409)

    def test_11_static_only_no_network_tracking(self):
        html = self.call('GET','/')[1]
        self.assertNotIn(b'openai.com',html)
        self.assertNotIn(b'googleapis.com',html)
        self.assertNotIn(b'<iframe',html)
        js = self.call('GET','/app.js')[1]
        self.assertNotIn(b'eval(',js)
        self.assertNotIn(b'innerHTML',js)

    def test_12_no_bad_sql_state(self):
        import sqlite3
        with sqlite3.connect(self.db) as conn:
            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute("UPDATE story_state SET affinity=100 WHERE id=1")


if __name__ == '__main__':
    unittest.main()

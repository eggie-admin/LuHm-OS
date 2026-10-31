"""Actual local HTTP, SQLite, CSRF and story-run tests, without root or third-party deps."""
import http.client
import json
import tempfile
import threading
import unittest
from pathlib import Path

from tools.rootlessCastCockpit import init_db, db_connect, read_state, response_state, serve, advance, reset, STORY


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

    def raw_call(self, method, path, headers, body=b''):
        """Send deliberate duplicate HTTP headers without normalizing them."""
        connection = http.client.HTTPConnection('127.0.0.1', self.port, timeout=3)
        connection.putrequest(method, path, skip_host=True)
        for name, value in headers:
            connection.putheader(name, value)
        connection.endheaders(body)
        response = connection.getresponse()
        status = response.status
        raw = response.read()
        connection.close()
        return status, json.loads(raw)

    def test_duplicate_host_fails_closed(self):
        status, body = self.raw_call('GET', '/api/state', [
            ('Host', f'127.0.0.1:{self.port}'), ('Host', 'attacker.example')])
        self.assertEqual((status, body['error']), (403, 'INVALID_HOST'))

    def test_duplicate_origin_fails_closed(self):
        payload = b'{"revision":0}'
        status, body = self.raw_call('POST', '/api/reset', [
            ('Host', f'127.0.0.1:{self.port}'),
            ('Origin', self.origin), ('Origin', 'http://attacker.example'),
            ('Content-Type', 'application/json'), ('Content-Length', str(len(payload)))], payload)
        self.assertEqual((status, body['error']), (403, 'CROSS_ORIGIN_DENIED'))

    def test_duplicate_content_length_fails_closed(self):
        payload = b'{"revision":0}'
        status, body = self.raw_call('POST', '/api/reset', [
            ('Host', f'127.0.0.1:{self.port}'), ('Origin', self.origin),
            ('Content-Type', 'application/json'),
            ('Content-Length', str(len(payload))), ('Content-Length', str(len(payload) + 1))], payload)
        self.assertEqual((status, body['error']), (413, 'BODY_LIMIT'))

    def test_transfer_encoding_is_rejected(self):
        payload = b'{"revision":0}'
        status, body = self.raw_call('POST', '/api/reset', [
            ('Host', f'127.0.0.1:{self.port}'), ('Origin', self.origin),
            ('Content-Type', 'application/json'),
            ('Transfer-Encoding', 'chunked'), ('Content-Length', str(len(payload)))], payload)
        self.assertEqual((status, body['error']), (400, 'TRANSFER_ENCODING_DENIED'))

    def test_duplicate_content_type_fails_closed(self):
        payload = b'{"revision":0}'
        status, body = self.raw_call('POST', '/api/reset', [
            ('Host', f'127.0.0.1:{self.port}'), ('Origin', self.origin),
            ('Content-Type', 'application/json'), ('Content-Type', 'text/plain'),
            ('Content-Length', str(len(payload)))], payload)
        self.assertEqual((status, body['error']), (415, 'JSON_REQUIRED'))

    def test_oversized_length_token_is_rejected_before_integer_parse(self):
        status, body = self.raw_call('POST', '/api/reset', [
            ('Host', f'127.0.0.1:{self.port}'), ('Origin', self.origin),
            ('Content-Type', 'application/json'), ('Content-Length', '0' * 6000)])
        self.assertEqual((status, body['error']), (413, 'BODY_LIMIT'))

    def test_malformed_utf8_json_is_a_recoverable_client_error(self):
        payload = b'{"revision":"\\xff"}'.replace(b'\\xff', bytes([255]))
        status, body = self.raw_call('POST', '/api/reset', [
            ('Host', f'127.0.0.1:{self.port}'), ('Origin', self.origin),
            ('Content-Type', 'application/json'), ('Content-Length', str(len(payload)))], payload)
        self.assertEqual((status, body['error']), (409, 'INVALID_OR_STALE_COMMAND'))

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

    def test_sqlite_rejects_symlinked_db_without_touching_target(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            store = base / "private"
            store.mkdir(mode=0o700)
            target = base / "untouched"
            target.write_bytes(b"do not replace")
            db = store / "story.sqlite3"
            db.symlink_to(target)
            with self.assertRaisesRegex(ValueError, "UNSAFE_SQLITE_SYMLINK"):
                init_db(db, json.loads(STORY.read_text(encoding="utf-8")))
            self.assertEqual(target.read_bytes(), b"do not replace")

    def test_sqlite_rejects_symlinked_directory_without_chmod(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            outside = base / "outside"
            outside.mkdir(mode=0o755)
            alias = base / "alias"
            alias.symlink_to(outside, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "UNSAFE_SQLITE_SYMLINK"):
                init_db(alias / "story.sqlite3", json.loads(STORY.read_text(encoding="utf-8")))
            self.assertFalse((outside / "story.sqlite3").exists())
            self.assertEqual(outside.stat().st_mode & 0o777, 0o755)

    def test_sqlite_rejects_existing_shared_dir_without_chmod(self):
        with tempfile.TemporaryDirectory() as temp:
            store = Path(temp) / "shared"
            store.mkdir(mode=0o755)
            with self.assertRaisesRegex(ValueError, "INSECURE_SQLITE_DIRECTORY"):
                init_db(store / "story.sqlite3", json.loads(STORY.read_text(encoding="utf-8")))
            self.assertEqual(store.stat().st_mode & 0o777, 0o755)
            self.assertFalse((store / "story.sqlite3").exists())

    def test_sqlite_rejects_linked_wal_sidecar_without_mutation(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            store = base / "private"
            store.mkdir(mode=0o700)
            target = base / "sentinel"
            target.write_bytes(b"no WAL writes")
            db = store / "story.sqlite3"
            (store / "story.sqlite3-wal").symlink_to(target)
            with self.assertRaisesRegex(ValueError, "UNSAFE_SQLITE_SYMLINK"):
                init_db(db, json.loads(STORY.read_text(encoding="utf-8")))
            self.assertEqual(target.read_bytes(), b"no WAL writes")
            self.assertFalse(db.exists())

    def test_sqlite_wal_reinit_preserves_story_revision(self):
        with tempfile.TemporaryDirectory() as temp:
            db = Path(temp) / "private" / "story.sqlite3"
            story = json.loads(STORY.read_text(encoding="utf-8"))
            init_db(db, story)
            result = advance(db, story, 1, 0)
            self.assertEqual(result["revision"], 1)
            init_db(db, story)
            with db_connect(db) as conn:
                state = read_state(conn)
                mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
            self.assertEqual(state["revision"], 1)
            self.assertEqual(state["nodeId"], result["nodeId"])
            self.assertEqual(mode.lower(), "wal")
            with self.assertRaisesRegex(ValueError, "STALE_STORY_REVISION"):
                reset(db, story, 0)
            with db_connect(db) as conn:
                self.assertEqual(read_state(conn)["revision"], 1)

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

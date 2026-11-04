"""Direct local HTTP, consent, SQLite and 2048-case TestBridge checks."""
import http.client
import json
from pathlib import Path
import threading
import unittest
from http.server import ThreadingHTTPServer
from tempfile import TemporaryDirectory

from host.testBridge import luhmTestBridge as bridge
from tools import firefoxTestBridge2048Audit as audit


class TestBridgeChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.store = bridge.BridgeStore()
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), bridge.make_handler(cls.store))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)
        cls.store.close()

    def request(self, method, path, obj=None, *, origin="good", token=None, ctype="application/json"):
        port = self.server.server_port
        conn = http.client.HTTPConnection("127.0.0.1", port, timeout=4)
        headers = {"Host": f"127.0.0.1:{port}"}
        if origin == "good":
            headers["Origin"] = f"http://127.0.0.1:{port}"
        elif origin == "bad":
            headers["Origin"] = "https://attacker.example"
        if token is not None:
            headers["X-TestBridge-Token"] = token
        body = None
        if obj is not None:
            body = json.dumps(obj)
            headers["Content-Type"] = ctype
        conn.request(method, path, body=body, headers=headers)
        response = conn.getresponse()
        data = response.read()
        headers_out = dict(response.getheaders())
        status = response.status
        conn.close()
        return status, headers_out, data

    def test_status_reports_local_only_and_no_auth(self):
        status, headers, body = self.request("GET", "/api/testbridge/v1/status")
        self.assertEqual(status, 200)
        payload = json.loads(body)
        self.assertEqual(payload["mode"], "LOCAL_VOLATILE_DEMO")
        self.assertFalse(payload["publicApiEnabled"])
        self.assertEqual(payload["userAuthentication"], "NOT_IMPLEMENTED")
        self.assertEqual(payload["crownStatus"], "STOP")
        self.assertNotIn("Access-Control-Allow-Origin", headers)

    def test_only_static_allowlist(self):
        for path in ("/", "/testBridge.css", "/testBridge.js"):
            self.assertEqual(self.request("GET", path)[0], 200)
        for path in ("/../doctrine/currentSourceTruthV3.json",
                     "/api/testbridge/v1/notes?dump=1", "/.env"):
            self.assertEqual(self.request("GET", path)[0], 404)

    def test_consent_and_sqlite_parameter_binding(self):
        note = "a' OR 1=1 -- <img src=x onerror=alert(1)>"
        created = self.request("POST", "/api/testbridge/v1/notes", {
            "displayName": "Professor", "note": note, "consent": True
        }, token=self.store.csrf)
        self.assertEqual(created[0], 201)
        row_id = json.loads(created[2])["id"]
        items = json.loads(self.request("GET", "/api/testbridge/v1/notes")[2])["items"]
        self.assertTrue(any(x["id"] == row_id and x["note"] == note for x in items))
        deletion = self.request("POST", "/api/testbridge/v1/delete", {"id": row_id}, token=self.store.csrf)
        self.assertEqual(deletion[0], 200)
        self.assertFalse(any(x["id"] == row_id for x in self.store.list()))

    def test_negative_consent_and_unknown_fields(self):
        base = {"displayName": "Demo", "note": "Only local", "consent": False}
        self.assertEqual(self.request("POST", "/api/testbridge/v1/notes", base, token=self.store.csrf)[0], 400)
        self.assertEqual(self.request("POST", "/api/testbridge/v1/notes",
                         {**base, "consent": True, "email": "bad@example"}, token=self.store.csrf)[0], 400)
        self.assertEqual(self.request("POST", "/api/testbridge/v1/notes",
                         {"displayName": "Demo", "note": "demo@example.com", "consent": True},
                         token=self.store.csrf)[0], 400)

    def test_csrf_and_origin_rejected(self):
        payload = {"displayName": "Demo", "note": "No remote input", "consent": True}
        self.assertEqual(self.request("POST", "/api/testbridge/v1/notes", payload, token="wrong")[0], 403)
        self.assertEqual(self.request("POST", "/api/testbridge/v1/notes", payload,
                                      token=self.store.csrf, origin="bad")[0], 403)
        self.assertEqual(self.request("POST", "/api/testbridge/v1/notes", payload,
                                      token=self.store.csrf, origin="none")[0], 403)
        self.assertEqual(self.request("POST", "/api/testbridge/v1/notes", payload,
                                      token=self.store.csrf, ctype="text/plain")[0], 415)
        for method in ("PUT", "DELETE"):
            self.assertEqual(self.request(method, "/api/testbridge/v1/notes")[0], 405)

    def test_session_is_volatile(self):
        session = json.loads(self.request("GET", "/api/testbridge/v1/session")[2])
        self.assertEqual(session["csrfToken"], self.store.csrf)
        self.assertTrue(session["consentRequired"])
        self.assertFalse(session["publicAuthProven"])
        self.assertEqual(session["retentionSeconds"], 3600)

    def test_expiry_and_delete(self):
        now = [100000]
        store = bridge.BridgeStore(clock=lambda: now[0])
        try:
            rid = store.insert("Demo", "one hour only", True)
            self.assertEqual(len(store.list()), 1)
            now[0] += bridge.MAX_AGE_SECONDS + 1
            self.assertEqual(store.list(), [])
            store.delete(rid)
        finally:
            store.close()

    def test_no_persistent_database(self):
        store = bridge.BridgeStore()
        try:
            db_files = store.db.execute("PRAGMA database_list").fetchall()
            self.assertEqual(db_files[0][2], "")
        finally:
            store.close()

    def test_static_js_renders_text_not_html(self):
        js = (bridge.ASSET_DIR / "testBridge.js").read_text(encoding="utf-8")
        self.assertIn("textContent=item.note", js)
        self.assertNotIn("innerHTML", js)
        self.assertNotIn("eval(", js)
        self.assertNotIn("https://", js)

    def test_2048_matrix_receipt_and_source_anchors(self):
        with TemporaryDirectory() as tmp:
            report, ok = audit.run("b" * 40, Path(tmp))
            self.assertTrue(ok, report["sourceAnchors"])
            self.assertEqual(report["scenarioAssertions"], 2048)
            self.assertEqual(report["passedScenarioAssertions"], 2048)
            self.assertEqual((Path(tmp) / "testBridge2048.bin").stat().st_size, 131072)
            self.assertEqual(report["verdict"], "SOURCE_MODEL_PASS")
            self.assertEqual(report["crownStatus"], "STOP")
            self.assertFalse(report["privateRecordsIncluded"])
            self.assertFalse(report["firefoxHostSigningProven"])
            self.assertFalse(report["livePublicDeployment"])

    def test_fail_closed_for_every_hostile_scenario(self):
        for family in range(16):
            for evidence in range(8):
                for scope in range(4):
                    for authority in range(4):
                        decision = audit.policy_actual(family, evidence, scope, authority)
                        if (evidence or scope or authority != 1 or family in (11, 12, 15)):
                            self.assertEqual(decision, "HOLD")

    def test_source_rules_before_runtime(self):
        self.assertTrue(bridge.load_source_policy())


if __name__ == "__main__":
    unittest.main()

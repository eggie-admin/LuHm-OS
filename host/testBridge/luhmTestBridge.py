#!/usr/bin/env python3
"""Local-only consent-based TestBridge for the LuHm Firefox antenna.

Source demonstration: SQLite :memory:, no external network, no auth bypass.
NOT a production forum, phpMyAdmin, or public personal-data database.
"""
from __future__ import annotations
import argparse
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import secrets
import sqlite3
import threading
import time
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
HOST = "127.0.0.1"
PORT = 8766
ASSET_DIR = ROOT / "host" / "testBridge"
MAX_RECORDS = 32
MAX_AGE_SECONDS = 3600
MAX_JSON_BYTES = 4096
ASSETS = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/testBridge.js": ("testBridge.js", "text/javascript; charset=utf-8"),
    "/testBridge.css": ("testBridge.css", "text/css; charset=utf-8"),
}

class BridgeStore:
    """Explicitly volatile. One process and no disk writes."""
    def __init__(self, *, clock=time.time):
        self.clock = clock
        self.lock = threading.Lock()
        self.db = sqlite3.connect(":memory:", check_same_thread=False)
        self.db.execute("CREATE TABLE notes (id INTEGER PRIMARY KEY, displayName TEXT NOT NULL, note TEXT NOT NULL, createdAt INTEGER NOT NULL)")
        self.csrf = secrets.token_urlsafe(32)

    def purge(self):
        self.db.execute("DELETE FROM notes WHERE createdAt <= ?", (int(self.clock()) - MAX_AGE_SECONDS,))

    def insert(self, display_name: str, note: str, consent: bool):
        if consent is not True:
            raise ValueError("EXPLICIT_CONSENT_REQUIRED")
        if not isinstance(display_name, str) or not isinstance(note, str):
            raise ValueError("INVALID_RECORD_TYPES")
        if not (1 <= len(display_name.strip()) <= 40 and 1 <= len(note.strip()) <= 300):
            raise ValueError("INVALID_LENGTH")
        if any(ord(c) < 32 or ord(c) == 127 for c in display_name + note):
            raise ValueError("CONTROL_CHARACTER_FORBIDDEN")
        # This bounded demo does not accept credentials, direct contacts, or email fields.
        if "@" in display_name or "@" in note:
            raise ValueError("CONTACT_INFORMATION_OUT_OF_SCOPE")
        with self.lock:
            self.purge()
            count = self.db.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
            if count >= MAX_RECORDS:
                raise ValueError("RECORD_LIMIT_REACHED")
            cur = self.db.execute(
                "INSERT INTO notes(displayName, note, createdAt) VALUES(?, ?, ?)",
                (display_name.strip(), note.strip(), int(self.clock())),
            )
            self.db.commit()
            return cur.lastrowid

    def list(self):
        with self.lock:
            self.purge()
            rows = self.db.execute(
                "SELECT id, displayName, note, createdAt FROM notes ORDER BY id DESC LIMIT ?",
                (MAX_RECORDS,)
            ).fetchall()
            return [{"id": r[0], "displayName": r[1], "note": r[2], "createdAt": r[3]} for r in rows]

    def delete(self, record_id):
        if type(record_id) is not int or not (0 < record_id < 2**63):
            raise ValueError("INVALID_ID")
        with self.lock:
            self.db.execute("DELETE FROM notes WHERE id = ?", (record_id,))
            self.db.commit()

    def close(self):
        self.db.close()


def load_source_policy(root=ROOT):
    a = json.loads((root / "doctrine/firefoxAntennaV1.json").read_text(encoding="utf-8"))
    q = json.loads((root / "doctrine/companyWideOperationalQuarantineV1.json").read_text(encoding="utf-8"))
    if (a.get("crownStatus") != "STOP" or a.get("backend", {}).get("httpBind") != HOST
            or q.get("state") != "QUARANTINED" or q.get("activeTaskWorkersAllowed") is not False):
        raise ValueError("POLICY_DRIFT")
    return True


def make_handler(store: BridgeStore, *, root=ROOT):
    class Handler(BaseHTTPRequestHandler):
        server_version = "LuHmTestBridge/0.1"
        sys_version = ""
        protocol_version = "HTTP/1.1"

        def log_message(self, fmt, *args):
            # Avoid storing user entries or request metadata in logs.
            pass

        def respond(self, code, value, *, ctype="application/json; charset=utf-8", head=False):
            body = (json.dumps(value, sort_keys=True).encode("utf-8")
                    if isinstance(value, (dict, list)) else value)
            self.send_response(code)
            for key, val in {
                "Content-Type": ctype,
                "Content-Length": str(len(body)),
                "Cache-Control": "no-store",
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "Referrer-Policy": "no-referrer",
                "Cross-Origin-Resource-Policy": "same-origin",
                "Content-Security-Policy": ("default-src 'self'; "
                  "script-src 'self'; style-src 'self'; img-src 'self'; "
                  "connect-src 'self'; form-action 'self'; base-uri 'none'; "
                  "frame-ancestors 'none'; object-src 'none'"),
            }.items():
                self.send_header(key, val)
            self.end_headers()
            if not head:
                self.wfile.write(body)

        def trusted(self, *, require_origin=False):
            if self.headers.get("Host", "") != f"{HOST}:{self.server.server_port}":
                return False
            origin = self.headers.get("Origin")
            if require_origin and origin != f"http://{HOST}:{self.server.server_port}":
                return False
            return origin in (None, f"http://{HOST}:{self.server.server_port}")

        def path(self):
            parsed = urlsplit(self.path)
            if parsed.query or parsed.fragment:
                return None
            return parsed.path

        def do_GET(self):
            if not self.trusted():
                return self.respond(403, {"error": "BAD_ORIGIN"})
            path = self.path()
            if path == "/api/testbridge/v1/session":
                return self.respond(200, {
                    "schema": "luhmOs.testBridgeSession.v1", "csrfToken": store.csrf,
                    "mode": "LOCAL_VOLATILE_DEMO", "retentionSeconds": MAX_AGE_SECONDS,
                    "consentRequired": True, "publicAuthProven": False,
                })
            if path == "/api/testbridge/v1/notes":
                return self.respond(200, {"items": store.list(), "mode": "LOCAL_VOLATILE_DEMO"})
            if path == "/api/testbridge/v1/status":
                return self.respond(200, {
                    "schema": "luhmOs.testBridgeStatus.v1", "mode": "LOCAL_VOLATILE_DEMO",
                    "store": "SQLITE_IN_MEMORY", "personalDataInGithub": False,
                    "publicApiEnabled": False, "remoteNetworkEnabled": False,
                    "userAuthentication": "NOT_IMPLEMENTED",
                    "tls": "NOT_REQUIRED_FOR_LOOPBACK_ONLY",
                    "crownStatus": "STOP",
                })
            if path not in ASSETS:
                return self.respond(404, {"error": "NOT_FOUND"})
            name, mime = ASSETS[path]
            p = root / "host" / "testBridge" / name
            if p.is_symlink() or not p.is_file():
                return self.respond(503, {"error": "ASSET_MISSING"})
            data = p.read_bytes()
            if len(data) > 100_000:
                return self.respond(503, {"error": "ASSET_TOO_LARGE"})
            return self.respond(200, data, ctype=mime)

        def do_HEAD(self):
            if not self.trusted():
                return self.respond(403, {"error": "BAD_ORIGIN"}, head=True)
            if self.path() == "/api/testbridge/v1/status":
                return self.respond(200, b"", head=True)
            return self.respond(405, {"error": "METHOD_NOT_ALLOWED"}, head=True)

        def do_POST(self):
            if not self.trusted(require_origin=True):
                return self.respond(403, {"error": "BAD_ORIGIN"})
            if self.path() not in ("/api/testbridge/v1/notes", "/api/testbridge/v1/delete"):
                return self.respond(404, {"error": "NOT_FOUND"})
            if self.headers.get("X-TestBridge-Token") != store.csrf:
                return self.respond(403, {"error": "BAD_TOKEN"})
            if self.headers.get("Content-Type", "").split(";")[0].strip() != "application/json":
                return self.respond(415, {"error": "JSON_REQUIRED"})
            try:
                length = int(self.headers.get("Content-Length", "-1"))
                if not 0 <= length <= MAX_JSON_BYTES:
                    return self.respond(413, {"error": "BAD_SIZE"})
                payload = json.loads(self.rfile.read(length))
                if not isinstance(payload, dict):
                    raise ValueError("OBJECT_REQUIRED")
                if self.path() == "/api/testbridge/v1/notes":
                    if set(payload) != {"displayName", "note", "consent"}:
                        raise ValueError("UNKNOWN_FIELDS")
                    rid = store.insert(payload["displayName"], payload["note"], payload["consent"])
                    return self.respond(201, {"id": rid, "stored": "IN_MEMORY_ONLY"})
                if set(payload) != {"id"}:
                    raise ValueError("UNKNOWN_FIELDS")
                store.delete(payload["id"])
                return self.respond(200, {"deleted": True})
            except (ValueError, TypeError, KeyError, UnicodeDecodeError, json.JSONDecodeError):
                return self.respond(400, {"error": "INVALID_OR_UNCONSENTED_INPUT"})

        def do_PUT(self):
            return self.respond(405, {"error": "METHOD_NOT_ALLOWED"})

        def do_DELETE(self):
            return self.respond(405, {"error": "METHOD_NOT_ALLOWED"})

    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=PORT)
    args = parser.parse_args()
    if args.port != PORT:
        parser.error("TestBridge is fixed at loopback port 8766")
    load_source_policy()
    store = BridgeStore()
    server = ThreadingHTTPServer((HOST, PORT), make_handler(store))
    print(f"TESTBRIDGE_LOCAL_ONLY http://{HOST}:{PORT}/", flush=True)
    try:
        server.serve_forever(poll_interval=0.25)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        store.close()


if __name__ == "__main__":
    main()

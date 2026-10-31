#!/usr/bin/env python3
"""A rootless, loopback-only LuHm-OS cockpit: stdlib Python, HTML/CSS, SQLite.

A private candidate browser app, NOT a signed APK, game-engine runtime,
ChatGPT plugin install, firmware component, or public network service.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from contextlib import closing
from pathlib import Path
from urllib.parse import urlsplit

from tools.datingSimPilot import current, new_game, select
from tools.hydraCastMediaBridge import verify_story

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "frontEnd" / "rootlessCockpit"
STORY = ROOT / "game" / "datingSimPilotV1.json"
STATIC = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/app.css": ("app.css", "text/css; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
    "/avatar3d.mjs": ("avatar3d.mjs", "text/javascript; charset=utf-8"),
    "/manifest.webmanifest": ("manifest.webmanifest", "application/manifest+json"),
    "/icon.svg": ("icon.svg", "image/svg+xml"),
}


def db_connect(path: Path):
    conn = sqlite3.connect(str(path), timeout=5, isolation_level=None)
    conn.execute("PRAGMA busy_timeout=5000")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db(path: Path, story: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.parent.chmod(0o700)
    with closing(db_connect(path)) as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("""CREATE TABLE IF NOT EXISTS story_state(
            id INTEGER PRIMARY KEY CHECK(id=1),
            node TEXT NOT NULL, affinity INTEGER NOT NULL CHECK(affinity BETWEEN 0 AND 10),
            revision INTEGER NOT NULL CHECK(revision >= 0),
            history TEXT NOT NULL)""")
        start = new_game(story)
        conn.execute("INSERT OR IGNORE INTO story_state(id,node,affinity,revision,history) VALUES(1,?,?,0,?)",
                     (start["nodeId"], start["affinity"], "[]"))
    path.chmod(0o600)


def read_state(conn) -> dict:
    row = conn.execute("SELECT node,affinity,revision,history FROM story_state WHERE id=1").fetchone()
    if row is None:
        raise ValueError("MISSING_STORY_STATE")
    return {"nodeId": row[0], "affinity": row[1], "revision": row[2], "history": json.loads(row[3])}


def response_state(story: dict, state: dict) -> dict:
    node = current(story, state)
    return {
        "schema": "luhmOs.rootlessStory.v1", "nodeId": node["id"],
        "speaker": node["speaker"], "line": node["line"],
        "choices": [option["label"] for option in node["choices"]],
        "affinity": state["affinity"], "revision": state["revision"],
        "ending": node["kind"] == "ending", "cloudCalled": False,
        "engineRunning": False, "crown": "STOP",
    }


def advance(path: Path, story: dict, choice: int, expected_revision: int) -> dict:
    if type(choice) is not int or type(expected_revision) is not int:
        raise ValueError("INVALID_CHOICE_PAYLOAD")
    with closing(db_connect(path)) as conn:
        try:
            conn.execute("BEGIN IMMEDIATE")
            old = read_state(conn)
            if old["revision"] != expected_revision:
                raise ValueError("STALE_STORY_REVISION")
            nxt = select(story, old, choice)
            conn.execute("""UPDATE story_state SET node=?, affinity=?, revision=?, history=?
                         WHERE id=1 AND revision=?""",
                         (nxt["nodeId"], nxt["affinity"], old["revision"] + 1,
                          json.dumps(nxt["history"], separators=(",", ":")), old["revision"]))
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise
    return response_state(story, {**nxt, "revision": old["revision"] + 1})


def reset(path: Path, story: dict, expected_revision: int) -> dict:
    if type(expected_revision) is not int:
        raise ValueError("INVALID_RESET_REVISION")
    start = new_game(story)
    with closing(db_connect(path)) as conn:
        try:
            conn.execute("BEGIN IMMEDIATE")
            old = read_state(conn)
            if old["revision"] != expected_revision:
                raise ValueError("STALE_STORY_REVISION")
            conn.execute("UPDATE story_state SET node=?, affinity=?, revision=?, history='[]' WHERE id=1",
                         (start["nodeId"], start["affinity"], old["revision"] + 1))
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise
    return response_state(story, {**start, "revision": old["revision"] + 1})


def serve(db_path: Path, port: int = 8787, story_path: Path = STORY) -> ThreadingHTTPServer:
    if type(port) is not int or not 0 <= port <= 65535:
        raise ValueError("INVALID_LOOPBACK_PORT")
    story = json.loads(story_path.read_text(encoding="utf-8"))
    if verify_story(story):
        raise ValueError("INVALID_STORY_CONTRACT")
    init_db(db_path, story)

    class Handler(BaseHTTPRequestHandler):
        server_version = "LuHmRootless/0.1"
        sys_version = ""

        def _single_header(self, name):
            # Email-style headers.get() silently accepts the first of duplicates.
            # HTTP framing, Host and Origin must never be ambiguous.
            values = self.headers.get_all(name, [])
            return values[0] if len(values) == 1 else None

        def _host_ok(self):
            host = self._single_header("Host")
            return host in (f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}")

        def _headers(self, status, mime, length):
            self.send_response(status)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(length))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Cross-Origin-Resource-Policy", "same-origin")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
            self.end_headers()

        def _send(self, status, payload):
            body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
            self._headers(status, "application/json; charset=utf-8", len(body))
            self.wfile.write(body)

        def do_GET(self):
            if not self._host_ok():
                self._send(403, {"error": "INVALID_HOST"})
                return
            path = urlsplit(self.path).path
            if path in STATIC:
                name, mime = STATIC[path]
                body = (ASSETS / name).read_bytes()
                self._headers(200, mime, len(body))
                self.wfile.write(body)
                return
            if path == "/api/health":
                self._send(200, {"status": "ROOTLESS_LOCAL_CANDIDATE", "crown": "STOP",
                                  "databaseLayer": "USERSPACE_SQLITE_NOT_FIRMWARE", "mode": "OFFLINE_NO_CLOUD",
                                  "androidApkBuilt": False, "godotRunning": False, "aiProviderVerified": False})
                return
            if path == "/api/state":
                with closing(db_connect(db_path)) as conn:
                    state = read_state(conn)
                self._send(200, response_state(story, state))
                return
            self._send(404, {"error": "NOT_FOUND"})

        def do_POST(self):
            if not self._host_ok():
                self._send(403, {"error": "INVALID_HOST"})
                return
            valid_origins = (f"http://127.0.0.1:{self.server.server_port}",
                             f"http://localhost:{self.server.server_port}")
            if self._single_header("Origin") not in valid_origins:
                self._send(403, {"error": "CROSS_ORIGIN_DENIED"})
                return
            # This stdlib endpoint accepts only one explicit Content-Length,
            # never chunked/CL+TE framing or ambiguous duplicate headers.
            if self.headers.get_all("Transfer-Encoding", []):
                self._send(400, {"error": "TRANSFER_ENCODING_DENIED"})
                return
            content_type = self._single_header("Content-Type")
            if content_type is None or content_type.split(";", 1)[0].strip() != "application/json":
                self._send(415, {"error": "JSON_REQUIRED"})
                return
            length = self._single_header("Content-Length")
            if (length is None or len(length) > 4 or not length.isascii()
                    or not length.isdecimal() or not 2 <= int(length) <= 2048):
                self._send(413, {"error": "BODY_LIMIT"})
                return
            try:
                data = json.loads(self.rfile.read(int(length)))
                if not isinstance(data, dict):
                    raise ValueError("INVALID_JSON_OBJECT")
                path = urlsplit(self.path).path
                if path == "/api/choice" and set(data) == {"choice", "revision"}:
                    value = advance(db_path, story, data["choice"], data["revision"])
                elif path == "/api/reset" and set(data) == {"revision"}:
                    value = reset(db_path, story, data["revision"])
                else:
                    raise ValueError("UNKNOWN_COMMAND")
                self._send(200, value)
            except (ValueError, TypeError, UnicodeDecodeError, json.JSONDecodeError, KeyError):
                self._send(409, {"error": "INVALID_OR_STALE_COMMAND"})

        def log_message(self, format_string, *args):
            # Avoid recording potentially sensitive local paths or browser request metadata.
            pass

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--data-dir", type=Path, default=Path.home() / ".local" / "share" / "luhm-os" / "rootless")
    parser.add_argument("--check", action="store_true", help="Run source-only checks, do not start server or create SQLite")
    args = parser.parse_args()
    story = json.loads(STORY.read_text(encoding="utf-8"))
    errors = verify_story(story)
    for name, _ in STATIC.values():
        if not (ASSETS / name).is_file():
            errors.append("MISSING_STATIC_RESOURCE:" + name)
    if errors:
        raise SystemExit("RED_ROOTLESS_COCKPIT:" + ",".join(errors))
    if args.check:
        print(json.dumps({"status": "PASS_SOURCE_ONLY", "rootRequired": False, "apkBuilt": False,
                          "firmwareModified": False, "providerCalled": False, "crown": "STOP"}))
        return
    if args.data_dir.is_symlink():
        raise SystemExit("RED_SYMLINKED_DATA_DIRECTORY")
    app = serve(args.data_dir / "story.sqlite3", args.port)
    print(f"LuHm Rootless Cockpit: http://127.0.0.1:{app.server_port}/ (private browser preview)", flush=True)
    print("No root, APK signing, remote AI or firmware changes. Ctrl+C to stop.", flush=True)
    try:
        app.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:
        pass
    finally:
        app.server_close()


if __name__ == "__main__":
    main()

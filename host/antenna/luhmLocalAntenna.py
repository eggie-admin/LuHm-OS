#!/usr/bin/env python3
"""LuHm-OS Antenna: loopback-only, read-only Firefox/X11 kiosk status.

No network client, credentials, SQL, update installer, agent runtime, or shell exec.
This is a source candidate. Running it is a separate local user action.
"""
from __future__ import annotations

import argparse
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
HOST = "127.0.0.1"
PORT = 8765
EXTENSION_DIR = "plugins/luhm-firefox-antenna"
FILES = {
    "/": ("popup.html", "text/html; charset=utf-8"),
    "/popup.css": ("popup.css", "text/css; charset=utf-8"),
    "/popup.js": ("popup.js", "text/javascript; charset=utf-8"),
    "/manifest.json": (None, None),  # Deliberately inaccessible over HTTP.
}
SHELL_PATHS = ("manifest.json", "popup.html", "popup.css", "popup.js")
SHELL_BUDGET = 100_000_000
SHA = re.compile(r"^[a-f0-9]{40}$")


def load_json(root: Path, name: str) -> dict:
    return json.loads((root / name).read_text(encoding="utf-8"))


def read_public_asset(root: Path, filename: str) -> bytes:
    """Strict allowlist and no symlinks, including at parent boundary."""
    if filename not in SHELL_PATHS:
        raise ValueError("UNAPPROVED_ASSET")
    base = root / EXTENSION_DIR
    if base.is_symlink() or (root / "plugins").is_symlink():
        raise ValueError("SYMLINK_NOT_ALLOWED")
    item = base / filename
    if item.is_symlink() or not item.is_file():
        raise ValueError("MISSING_OR_SYMLINK_ASSET")
    data = item.read_bytes()
    if not data or len(data) > 1_000_000:
        raise ValueError("ASSET_SIZE_OUT_OF_RANGE")
    return data


def source_ref(root: Path) -> str:
    try:
        head = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"], text=True,
            capture_output=True, timeout=2, check=True,
        ).stdout.strip().lower()
        changed = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain", "--untracked-files=no"],
            text=True, capture_output=True, timeout=2, check=True,
        ).stdout
        return head if SHA.fullmatch(head) and not changed else "UNVERIFIED"
    except (subprocess.SubprocessError, OSError):
        return "UNVERIFIED"


def make_status(root: Path, *, source: str | None = None) -> dict:
    canon = load_json(root, "doctrine/projectChatCanonV1.json")
    updates = load_json(root, "doctrine/selfHostedRemoteUpdatesV1.json")
    quarantine = load_json(root, "doctrine/companyWideOperationalQuarantineV1.json")
    if canon["developmentIdentity"]["productName"] != "LuHm-OS":
        raise ValueError("CANONICAL_NAME_DRIFT")
    if (updates["crownStatus"] != "STOP"
            or updates["remoteScriptExecution"] is not False
            or updates["automaticApkInstall"] is not False):
        raise ValueError("UPDATE_DOCTRINE_DRIFT")
    if (quarantine["state"] != "QUARANTINED"
            or quarantine["activeTaskWorkersAllowed"] is not False):
        raise ValueError("QUARANTINE_DRIFT")
    files = {name: read_public_asset(root, name) for name in SHELL_PATHS}
    count = sum(map(len, files.values()))
    if count > SHELL_BUDGET:
        raise ValueError("SHELL_BUDGET_EXCEEDED")
    manifest = json.loads(files["manifest.json"])
    if manifest["manifest_version"] != 3:
        raise ValueError("EXTENSION_VERSION_DRIFT")
    ref = source if source is not None else source_ref(root)
    if ref != "UNVERIFIED" and not SHA.fullmatch(ref):
        raise ValueError("INVALID_SOURCE_REF")
    return {
        "schema": "luhmOs.firefoxAntennaStatus.v1",
        "identity": "LuHm-OS: Project Premonition",
        "mode": "READ_ONLY",
        "transport": "LOOPBACK_HTTP_ONLY",
        "sourceRef": ref,
        "shellBytes": count,
        "shellBudgetBytes": SHELL_BUDGET,
        "shellDigest": hashlib.sha256(
            b"".join(files[name] for name in SHELL_PATHS)
        ).hexdigest(),
        "shellScope": "fourExtensionSourceFilesOnlyNotDebianX11FirefoxOrPython",
        "firefoxExtensionVersion": manifest["version"],
        "updateState": "CHECK_ONLY_NO_INSTALL",
        "remoteManifestChecked": False,
        "agentExecution": False,
        "signedXpiInstalled": False,
        "physicalFirefoxX11Proven": False,
        "crownStatus": "STOP",
    }


def make_handler(root: Path):
    """Factory enables isolated localhost integration tests."""
    class Handler(BaseHTTPRequestHandler):
        server_version = "LuHmAntenna/0.1"
        sys_version = ""
        protocol_version = "HTTP/1.1"

        def log_message(self, format, *args):
            # No URLs, headers, or request body recorded.
            pass

        def send_payload(self, body: bytes, status: int, content_type: str, *, head=False):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header(
                "Content-Security-Policy",
                "default-src 'self'; connect-src 'self' http://127.0.0.1:8765; "
                "script-src 'self'; style-src 'self'; img-src 'self'; "
                "object-src 'none'; frame-ancestors 'none'; base-uri 'none'",
            )
            self.end_headers()
            if not head:
                self.wfile.write(body)

        def serve(self, *, head=False):
            host = self.headers.get("Host", "")
            if host != f"{HOST}:{self.server.server_port}":
                return self.send_payload(b"Bad host\n", 403, "text/plain", head=head)
            origin = self.headers.get("Origin")
            if origin and not origin.startswith("moz-extension://"):
                return self.send_payload(b"Origin rejected\n", 403, "text/plain", head=head)
            parsed = urlsplit(self.path)
            if parsed.query or parsed.fragment:
                return self.send_payload(b"Not found\n", 404, "text/plain", head=head)
            path = parsed.path
            if path == "/antenna/v1/status":
                try:
                    data = json.dumps(make_status(root), sort_keys=True).encode("utf-8")
                except (ValueError, KeyError, OSError, json.JSONDecodeError):
                    return self.send_payload(b"Local source check failed\n", 503, "text/plain", head=head)
                return self.send_payload(data, 200, "application/json; charset=utf-8", head=head)
            if path not in FILES or FILES[path][0] is None:
                return self.send_payload(b"Not found\n", 404, "text/plain", head=head)
            filename, mime = FILES[path]
            try:
                body = read_public_asset(root, filename)
            except (ValueError, OSError):
                return self.send_payload(b"Asset unavailable\n", 503, "text/plain", head=head)
            return self.send_payload(body, 200, mime, head=head)

        def do_GET(self):
            self.serve()

        def do_HEAD(self):
            self.serve(head=True)

        def do_POST(self):
            self.send_payload(b"Read-only\n", 405, "text/plain")

        def do_PUT(self):
            self.send_payload(b"Read-only\n", 405, "text/plain")

        def do_DELETE(self):
            self.send_payload(b"Read-only\n", 405, "text/plain")

    return Handler


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=PORT)
    args = parser.parse_args()
    if args.port != PORT:
        parser.error("Firefox extension is pinned to 127.0.0.1:8765; alternate ports are not supported")
    make_status(ROOT)  # Fail closed before binding.
    with ThreadingHTTPServer((HOST, PORT), make_handler(ROOT)) as httpd:
        print(f"LOCAL_ANTENNA_READ_ONLY http://{HOST}:{PORT}/", flush=True)
        try:
            httpd.serve_forever(poll_interval=0.25)
        except KeyboardInterrupt:
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

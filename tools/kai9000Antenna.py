#!/usr/bin/env python3
"""Loopback-only antenna assets and read-only capability discovery. No execution API."""
import argparse
import json
import mimetypes
import platform
import re
import shutil
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit


def capabilities():
    return {"schema": "luhmOs.antennaCapabilities.v1", "scope": "localProcess",
            "architecture": platform.machine(), "python": platform.python_version(),
            "profiles": ["antenna", "light"], "commandDiscovery": {
                name: bool(shutil.which(name)) for name in
                ("blender", "gimp", "ffmpeg", "godot", "ollama")},
            "runtimeExecutionProven": False, "remoteConnectionProven": False,
            "chatPluginInvocationProven": False, "executionEnabled": False}


def handler_for(root):
    root = Path(root).resolve(strict=True)

    class Handler(BaseHTTPRequestHandler):
        server_version = "LuHmAntenna/0.1"
        sys_version = ""

        def respond(self, code, body, content_type="text/plain; charset=utf-8", head=False):
            self.send_response(code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Content-Security-Policy", "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data: blob:; media-src blob:; connect-src 'self'; worker-src 'self' blob:; base-uri 'none'; frame-ancestors 'none'; form-action 'none'")
            self.end_headers()
            if not head:
                self.wfile.write(body)

        def serve(self, head=False):
            port = self.server.server_address[1]
            hosts = {f"127.0.0.1:{port}", f"localhost:{port}"}
            host = self.headers.get("Host", "")
            origin = self.headers.get("Origin")
            if host not in hosts or (origin and origin != "http://" + host):
                return self.respond(403, b"Forbidden", head=head)
            if self.headers.get("Sec-Fetch-Site") == "cross-site":
                return self.respond(403, b"Forbidden", head=head)
            url = urlsplit(self.path)
            if url.query or url.fragment:
                return self.respond(404, b"Not found", head=head)
            if url.path == "/api/capabilities":
                return self.respond(200, json.dumps(capabilities()).encode(), "application/json", head)
            path = "/antenna.html" if url.path == "/" else url.path
            if path not in ("/antenna.html", "/index.html") and not re.fullmatch(r"/assets/[A-Za-z0-9_.-]+\.(?:js|css|png|svg|woff2)", path):
                return self.respond(404, b"Not found", head=head)
            target = root / path.lstrip("/")
            if not target.is_file() or not target.resolve().is_relative_to(root):
                return self.respond(404, b"Not found", head=head)
            kind = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
            return self.respond(200, target.read_bytes(), kind, head)

        def do_GET(self):
            self.serve()

        def do_HEAD(self):
            self.serve(True)

        def do_POST(self):
            self.respond(405, b"Read only")

        do_PUT = do_POST
        do_DELETE = do_POST

        def log_message(self, *_args):
            pass

    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1] / "frontEnd/prototypes/glassWorld/dist")
    parser.add_argument("--port", type=int, default=8766)
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error("port must be 1024..65535")
    if not (args.root / "antenna.html").is_file():
        parser.error("built antenna.html missing; build the Glass World candidate first")
    with ThreadingHTTPServer(("127.0.0.1", args.port), handler_for(args.root)) as server:
        print(f"ANTENNA=http://127.0.0.1:{args.port}/", flush=True)
        server.serve_forever()


if __name__ == "__main__":
    main()

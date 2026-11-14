#!/usr/bin/env python3
"""Serve only the compiled LuHm-OS edge bundle on loopback; no command API."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit
import argparse

projectRoot = Path(__file__).resolve().parents[1]
bundleRoot = projectRoot / "frontEnd/prototypes/lumEdge/dist"


class localStudioHandler(SimpleHTTPRequestHandler):
    def send_head(self):
        allowedHosts = {f"127.0.0.1:{self.server.server_port}",
                        f"localhost:{self.server.server_port}"}
        if self.headers.get_all("Host", []) not in [[host] for host in allowedHosts]:
            self.send_error(403, "Local host required")
            return None
        path = unquote(urlsplit(self.path).path)
        parts = path.split("/")
        if any(part.startswith(".") for part in parts if part) or "\\" in path or "\x00" in path:
            self.send_error(403, "Path rejected")
            return None
        root = Path(self.directory).resolve()
        target = (root / path.lstrip("/")).resolve()
        if target.is_dir():
            target = (target / "index.html").resolve()
        if not target.is_relative_to(root):
            self.send_error(403, "Path rejected")
            return None
        return super().send_head()

    def list_directory(self, path):
        self.send_error(404, "Directory listing disabled")
        return None

    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=(), usb=()")
        self.send_header("Content-Security-Policy", self.server.studioCsp)
        super().end_headers()

    def log_message(self, format, *args):
        # Do not persist user-supplied paths or local model names.
        pass


def createServer(root=bundleRoot, port=8789):
    root = Path(root).resolve(strict=True)
    if not (root / "index.html").is_file():
        raise ValueError("Build the edge bundle before starting the harness")
    headerLines = (root / "_headers").read_text().splitlines()
    policies = [line.strip().split(":", 1)[1].strip() for line in headerLines
                if line.strip().startswith("Content-Security-Policy:")]
    if len(policies) != 1:
        raise ValueError("Exactly one compiled CSP required")
    server = ThreadingHTTPServer(("127.0.0.1", port), partial(localStudioHandler, directory=str(root)))
    server.studioCsp = policies[0].replace("; upgrade-insecure-requests", "")
    return server


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8789)
    args = parser.parse_args()
    with createServer(port=args.port) as server:
        print(f"LuHm-OS: http://127.0.0.1:{server.server_port}/", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Read-only, explicit-allowlist LuHm cockpit for a local Termux/Android browser.

No API, command execution, remote binding, uploads, or directory browsing.
"""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ASSETS = {
    '/index.html': ('index.html', 'text/html; charset=utf-8'),
    '/styles.css': ('styles.css', 'text/css; charset=utf-8'),
    '/app.js': ('app.js', 'text/javascript; charset=utf-8'),
    '/jquery/luhm.codingRoleplay.js': ('jquery/luhm.codingRoleplay.js', 'text/javascript; charset=utf-8'),
    '/jquery/luhm.parallax.js': ('jquery/luhm.parallax.js', 'text/javascript; charset=utf-8'),
    '/jquery/luhm.cockpit.js': ('jquery/luhm.cockpit.js', 'text/javascript; charset=utf-8'),
    '/jquery/luhm.cast.js': ('jquery/luhm.cast.js', 'text/javascript; charset=utf-8'),
    '/vendor/jquery-3.7.1.min.js': ('vendor/jquery-3.7.1.min.js', 'text/javascript; charset=utf-8'),
}
CSP = (
    "default-src 'none'; script-src 'self'; style-src 'self'; "
    "img-src 'self' data: blob:; font-src 'self'; connect-src 'none'; "
    "object-src 'none'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'"
)


def missing_assets(root: Path):
    return [relative for relative, _ in ASSETS.values() if not (root / relative).is_file()]


def handler_for(root: Path):
    root = root.resolve(strict=True)

    class Handler(BaseHTTPRequestHandler):
        server_version = 'LuHmLocal/1.0'
        sys_version = ''

        def _respond(self, status, body: bytes, content_type='text/plain; charset=utf-8', send_body=True):
            self.send_response(status)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('X-Frame-Options', 'DENY')
            self.send_header('Referrer-Policy', 'no-referrer')
            self.send_header('Content-Security-Policy', CSP)
            self.end_headers()
            if send_body:
                self.wfile.write(body)

        def _serve(self, send_body=True):
            url = urlsplit(self.path)
            if url.query or url.fragment or not url.path.startswith('/'):
                return self._respond(404, b'Not found', send_body=send_body)
            path = '/index.html' if url.path == '/' else url.path
            if path == '/health':
                return self._respond(200, b'LOCAL_COCKPIT_READY\n', send_body=send_body)
            pair = ASSETS.get(path)
            if pair is None:
                return self._respond(404, b'Not found', send_body=send_body)
            relative, content_type = pair
            target = root / relative
            if not target.is_file() or not target.resolve().is_relative_to(root):
                return self._respond(404, b'Not found', send_body=send_body)
            return self._respond(200, target.read_bytes(), content_type, send_body=send_body)

        def do_GET(self):
            self._serve()

        def do_HEAD(self):
            self._serve(send_body=False)

        def do_POST(self):
            self._respond(405, b'Method not allowed')

        def do_PUT(self):
            self._respond(405, b'Method not allowed')

        def do_DELETE(self):
            self._respond(405, b'Method not allowed')

        def log_message(self, fmt, *args):
            # Do not log user-controlled URL paths or query values.
            pass

    return Handler


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1] / 'frontEnd')
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.port < 1024 or args.port > 65535:
        parser.error('port must be between 1024 and 65535')
    root = args.root.resolve()
    if not root.is_dir():
        parser.error('frontEnd directory is missing')
    missing = missing_assets(root)
    if missing:
        parser.error('local cockpit assets missing: ' + ', '.join(missing) + '. Run: bash tools/kai9000TermuxX11.sh setup')
    if args.check:
        print('GREEN_LOCAL_COCKPIT_ASSET_ALLOWLIST')
        return
    # Explicit literal loopback, never wildcard bind or LAN.
    with ThreadingHTTPServer(('127.0.0.1', args.port), handler_for(root)) as httpd:
        print(f'LOCAL_COCKPIT=http://127.0.0.1:{args.port}/', flush=True)
        httpd.serve_forever(poll_interval=0.5)


if __name__ == '__main__':
    main()

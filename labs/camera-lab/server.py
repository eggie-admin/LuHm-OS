#!/usr/bin/env python3
"""Hydra Camera Lab: minimal local-only camera + Ollama control plane.

The prototype does not retain chat history. Adult-supervised use only.
"""
import glob
import json
import os
import pathlib
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = pathlib.Path(__file__).resolve().parent
HOST = "127.0.0.1"
PORT = int(os.environ.get("HYDRA_CAMERA_PORT", "8765"))
OLLAMA = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
MODEL = os.environ.get("HYDRA_OLLAMA_MODEL", "llama3.2:3b")
MAX_BODY = 16 * 1024


def ollama_status():
    try:
        request = urllib.request.Request(OLLAMA + "/api/tags")
        with urllib.request.urlopen(request, timeout=2) as response:
            data = json.load(response)
        return {"connected": True, "models": [m.get("name", "") for m in data.get("models", [])][:30]}
    except Exception:
        return {"connected": False, "models": []}


class Handler(BaseHTTPRequestHandler):
    def allowed_host(self):
        return self.headers.get("Host", "").lower() in {f"127.0.0.1:{PORT}", f"localhost:{PORT}"}

    def log_message(self, fmt, *args):
        # Do not log a child's chat or browsing activity.
        pass

    def send_json(self, obj, status=200):
        payload = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; img-src 'self' data: blob:; style-src 'self'; script-src 'self'; connect-src 'self'; media-src 'self' blob:")
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if not self.allowed_host():
            return self.send_error(403, "Localhost only")
        if self.path == "/api/status":
            return self.send_json({
                "ollama": ollama_status(),
                "model": MODEL,
                "video_devices": sorted(glob.glob("/dev/video*")),
                "usb_gadget_config_present": (
                    os.path.isdir("/config/usb_gadget")
                    or os.path.isdir("/sys/kernel/config/usb_gadget")
                ),
                "note": "Android Chrome might not expose external UVC sources."
            })
        if self.path in ("/", "/index.html", "/app.js", "/style.css"):
            path = ROOT / "static" / ("index.html" if self.path == "/" else self.path.lstrip("/"))
            if not path.is_file():
                return self.send_error(404)
            data = path.read_bytes()
            kind = (
                "text/html; charset=utf-8" if path.suffix == ".html"
                else "application/javascript; charset=utf-8" if path.suffix == ".js"
                else "text/css; charset=utf-8"
            )
            self.send_response(200)
            self.send_header("Content-Type", kind)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'self'; img-src 'self' data: blob:; style-src 'self'; script-src 'self'; connect-src 'self'; media-src 'self' blob:")
            self.end_headers()
            return self.wfile.write(data)
        return self.send_error(404)

    def do_POST(self):
        if not self.allowed_host():
            return self.send_error(403, "Localhost only")
        if self.headers.get("Content-Type", "").split(";", 1)[0].lower() != "application/json":
            return self.send_json({"error": "JSON required"}, 415)
        origin = self.headers.get("Origin")
        if origin and origin.rstrip("/") not in {
            f"http://127.0.0.1:{PORT}", f"http://localhost:{PORT}"
        }:
            return self.send_error(403, "Cross-origin requests disabled")
        if self.path != "/api/ask":
            return self.send_error(404)
        try:
            n = int(self.headers.get("Content-Length", "0"))
            if not 0 < n <= MAX_BODY:
                return self.send_json({"error": "Message too large or empty"}, 400)
            msg = json.loads(self.rfile.read(n))
            if not isinstance(msg, dict):
                return self.send_json({"error": "JSON object required"}, 400)
            prompt = msg.get("prompt", "")
            if not isinstance(prompt, str) or not 0 < len(prompt.strip()) <= 4000:
                return self.send_json({"error": "Enter a question of up to 4000 characters"}, 400)
            # This is a prompt guide, not a verified child-safety mechanism.
            system = (
                "You are a friendly educational helper for a child working on creative and coding projects. "
                "Use age-appropriate language; avoid mature topics; encourage checking facts and asking "
                "a trusted adult about risky, personal, or sensitive matters. Do not request identifying data."
            )
            payload = json.dumps({
                "model": MODEL, "stream": False, "prompt": prompt, "system": system,
                "options": {"num_predict": 450}
            }).encode("utf-8")
            req = urllib.request.Request(
                OLLAMA + "/api/generate", data=payload,
                headers={"Content-Type": "application/json"}, method="POST"
            )
            with urllib.request.urlopen(req, timeout=100) as response:
                result = json.load(response)
            return self.send_json({"answer": str(result.get("response", ""))[:12000]})
        except (TimeoutError, urllib.error.URLError):
            return self.send_json({"error": "Ollama unavailable. Start it locally or use an SSH tunnel."}, 503)
        except (ValueError, json.JSONDecodeError):
            return self.send_json({"error": "Invalid request or Ollama response."}, 400)
        except Exception:
            return self.send_json({"error": "Request failed; check Termux console."}, 500)


if __name__ == "__main__":
    print(f"Hydra Camera Lab: http://{HOST}:{PORT}")
    print(f"Ollama endpoint: {OLLAMA} | model: {MODEL}")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()

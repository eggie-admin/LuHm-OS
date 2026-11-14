#!/usr/bin/env python3
"""Loopback antenna assets, capability discovery and offline creation plans. No execution API."""
import argparse
import json
import mimetypes
import platform
import re
import shutil
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

RECIPES = {
    "scenePreview": ("blender", "prepareScene", "renderPreview"),
    "imagePrepare": ("gimp", "prepareImage", "exportPreview"),
    "videoPreview": ("ffmpeg", "prepareTimeline", "encodePreview"),
    "characterAnimation": ("blender", "bakeRigMotion", "exportAnimatedGlb"),
}


def creation_plan(data):
    """Validate untrusted UI/AI output as data. Never translate a brief into code."""
    if not isinstance(data, dict) or set(data) != {"schema", "recipe", "target", "brief"}:
        raise ValueError("Expected creation request fields only")
    if data["schema"] != "luhmOs.creationRequest.v1":
        raise ValueError("Unsupported schema")
    if not isinstance(data["recipe"], str) or data["recipe"] not in RECIPES:
        raise ValueError("Unknown recipe")
    if data["target"] not in ("raspberryPi", "remoteStudio"):
        raise ValueError("Creation work requires an explicit remote target")
    brief = data["brief"]
    if not isinstance(brief, str) or not 1 <= len(brief.strip()) <= 2000 or len(brief) > 2000:
        raise ValueError("Brief must contain 1..2000 characters")
    if any(ord(char) < 32 and char not in "\n\t" for char in brief):
        raise ValueError("Unsupported control character")
    tool, prepare, preview = RECIPES[data["recipe"]]
    request = dict(data, brief=brief.strip())
    digest = hashlib.sha256(json.dumps(request, sort_keys=True, ensure_ascii=True).encode()).hexdigest()
    plan = {"schema": "luhmOs.creationPlan.v1", "requestSha256": digest,
            "request": request, "tool": tool, "steps": [prepare, preview, "reviewResult"],
            "planner": "deterministicTemplate", "aiInvoked": False,
            "status": "draftPlan", "encoding": "json", "executionEnabled": False,
            "providerCalls": 0, "publicationEnabled": False,
            "requiredEvidence": ["sourceCommit", "workerCapability", "assetRights", "resultSha256"],
            "assetTransfer": "fileReference", "base64Required": False}
    if data["recipe"] == "characterAnimation":
        plan["animationPipeline"] = {"master": "privateHighFidelityBlenderRig",
            "motionImport": "rightsClearedMmdOrOriginalMotion",
            "interchange": "glbWithBakedAnimationAndMorphTargets",
            "godotRole": "characterAnimationOnly", "gameWork": "onHold",
            "webRole": "vueControlsBabylonPreview", "antennaFallback": "renderedVideoOrStill",
            "runtimeProof": "PENDING", "masterModification": False}
    return plan


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate field")
        result[key] = value
    return result


def reject_constant(_value):
    raise ValueError("Non-finite JSON value")

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

        def trusted_request(self):
            port = self.server.server_address[1]
            hosts = {f"127.0.0.1:{port}", f"localhost:{port}"}
            host = self.headers.get("Host", "")
            origin = self.headers.get("Origin")
            if host not in hosts or (origin and origin != "http://" + host):
                return False
            if self.headers.get("Sec-Fetch-Site") == "cross-site":
                return False
            return True

        def serve(self, head=False):
            if not self.trusted_request():
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
            self.close_connection = True
            self.connection.settimeout(5)
            if not self.trusted_request():
                return self.respond(403, b"Forbidden")
            if self.path != "/api/creation/plan":
                return self.respond(405, b"No execution API")
            if self.headers.get("Content-Type", "").lower() != "application/json":
                return self.respond(415, b"JSON required")
            lengths = self.headers.get_all("Content-Length", [])
            if len(lengths) != 1 or self.headers.get("Transfer-Encoding"):
                return self.respond(400, b"One content length required")
            try:
                length = int(lengths[0])
                if not 1 <= length <= 8192:
                    return self.respond(413, b"Request too large or empty")
                raw = self.rfile.read(length)
                if len(raw) != length:
                    return self.respond(400, b"Incomplete request")
                data = json.loads(raw, object_pairs_hook=unique_object, parse_constant=reject_constant)
                result = creation_plan(data)
            except (ValueError, UnicodeError, RecursionError, TimeoutError, OSError):
                return self.respond(400, b"Invalid creation request")
            return self.respond(200, json.dumps(result).encode(), "application/json")

        def do_PUT(self):
            self.respond(405, b"No write API")

        do_DELETE = do_PUT

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

"""Deterministic adversarial tests for LuHm-OS read-only update metadata."""
from __future__ import annotations
import asyncio
import hashlib
import json
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "host/mcp"))
from luhmUpdateSpine import build_update_manifest, register_update_spine, MANIFEST_ROUTE
from starlette.requests import Request


class FakeServer:
    def __init__(self):
        self.routes = {}

    def custom_route(self, route, methods):
        def register(handler):
            self.routes[route] = (tuple(methods), handler)
            return handler
        return register


class UpdateSpineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = pathlib.Path(self.tmp.name)
        for d in ("doctrine", "plugins/luhm-os", "host/harness"):
            (self.root / d).mkdir(parents=True)
        c = json.loads((ROOT / "doctrine/stablePluginUpdateSpineV1.json").read_text())
        (self.root / "doctrine/stablePluginUpdateSpineV1.json").write_text(json.dumps(c))
        (self.root / "plugins/luhm-os/plugin.json").write_text(json.dumps({"name": "luhm-os", "version": "0.5.2"}))
        (self.root / "plugins/luhm-os/mcp.json").write_text(json.dumps({"mcpServers": {"luhm": {"url": "https://luhm-os-harness-green.onrender.com/mcp"}}}))
        for name in c["updateManifest"]["publicAllowlist"]:
            (self.root / "host/harness" / name).write_bytes(name.encode())

    def test_hash_and_unknown_state(self):
        manifest = build_update_manifest(self.root)
        self.assertEqual(len(manifest["assets"]), 4)
        self.assertEqual(manifest["deployedSourceRef"], "UNVERIFIED")
        self.assertEqual(manifest["crownStatus"], "STOP")
        self.assertFalse(manifest["hostInstallationProven"])
        self.assertFalse(manifest["cloudflareCdnProven"])
        self.assertFalse(manifest["autoInstall"])
        for asset in manifest["assets"]:
            digest = hashlib.sha256(asset["id"].encode()).hexdigest()
            self.assertEqual(asset["sha256"], digest)
            self.assertTrue(asset["path"].startswith("/harness/assets/"))

    def test_revision_input_validation(self):
        self.assertEqual(build_update_manifest(self.root, deployed_sha="a" * 40)["deployedSourceRef"], "a" * 40)
        for bad in ("", "short", "A" * 40, "a" * 39 + "g", "a" * 41):
            self.assertEqual(build_update_manifest(self.root, deployed_sha=bad)["deployedSourceRef"], "UNVERIFIED")

    def test_canonical_endpoint_cannot_drift(self):
        p = self.root / "plugins/luhm-os/mcp.json"
        p.write_text(json.dumps({"mcpServers": {"luhm": {"url": "https://attacker.example/mcp"}}}))
        with self.assertRaisesRegex(ValueError, "RED_STABLE_MCP"):
            build_update_manifest(self.root)

    def test_symlink_fails_closed(self):
        asset = self.root / "host/harness/cockpit.css"
        asset.unlink()
        asset.symlink_to(self.root / "plugins/luhm-os/plugin.json")
        with self.assertRaisesRegex(ValueError, "RED_UNSAFE_UPDATE_ASSET"):
            build_update_manifest(self.root)

    def test_get_head_etag_and_no_cors(self):
        server = FakeServer()
        register_update_spine(server, root=self.root)
        self.assertEqual(server.routes[MANIFEST_ROUTE][0], ("GET", "HEAD"))
        handler = server.routes[MANIFEST_ROUTE][1]
        async def request(method="GET", headers=None):
            encoded = [(k.lower().encode(), v.encode()) for k, v in (headers or {}).items()]
            req = Request({"type": "http", "method": method, "path": MANIFEST_ROUTE, "headers": encoded, "query_string": b""})
            return await handler(req)
        with patch.dict("os.environ", {"RENDER_GIT_COMMIT": "b" * 40}):
            get = asyncio.run(request())
            not_modified = asyncio.run(request(headers={"If-None-Match": get.headers["etag"]}))
        self.assertEqual(get.status_code, 200)
        self.assertIn("no-cache", get.headers["cache-control"])
        self.assertEqual(json.loads(get.body)["deployedSourceRef"], "b" * 40)
        self.assertEqual(not_modified.status_code, 304)
        self.assertEqual(not_modified.body, b"")
        self.assertNotIn("access-control-allow-origin", get.headers)
        head = asyncio.run(request("HEAD"))
        self.assertEqual(head.status_code, 200)
        self.assertEqual(head.body, b"")

    def test_corrupt_manifest_is_503_not_green(self):
        (self.root / "doctrine/stablePluginUpdateSpineV1.json").write_text("{}")
        server = FakeServer()
        register_update_spine(server, root=self.root)
        req = Request({"type": "http", "method": "GET", "path": MANIFEST_ROUTE, "headers": [], "query_string": b""})
        response = asyncio.run(server.routes[MANIFEST_ROUTE][1](req))
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.headers["cache-control"], "no-store")


if __name__ == "__main__":
    unittest.main()

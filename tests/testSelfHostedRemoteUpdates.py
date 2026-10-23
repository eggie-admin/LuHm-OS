"""Adversarial remote update feed and hashed asset contract tests; no remote IO."""
import asyncio
import hashlib
import json
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "host/mcp"))
from luhmUpdateSpine import (
    PUBLIC_ASSETS, V2_PUBLIC_ASSETS, V2_MANIFEST_ROUTE, V2_ASSET_ROUTE,
    build_remote_update_manifest, register_remote_update_routes,
)
from starlette.requests import Request

class FakeServer:
    def __init__(self):
        self.routes = {}
    def custom_route(self, uri, methods):
        def attach(handler):
            self.routes[uri] = (methods, handler)
            return handler
        return attach

class RemoteUpdateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = pathlib.Path(self.tmp.name)
        for name in ("doctrine", "plugins/luhm-os", "host/harness"):
            (self.root / name).mkdir(parents=True)
        for name in ("stablePluginUpdateSpineV1.json", "selfHostedRemoteUpdatesV1.json"):
            from_file = ROOT / "doctrine" / name
            (self.root / "doctrine" / name).write_bytes(from_file.read_bytes())
        (self.root / "plugins/luhm-os/plugin.json").write_text('{"name":"luhm-os","version":"0.5.2"}')
        (self.root / "plugins/luhm-os/mcp.json").write_text(
            '{"mcpServers":{"luhm":{"url":"https://luhm-os-harness-green.onrender.com/mcp"}}}')
        for name in V2_PUBLIC_ASSETS:
            value = name.encode()
            if name.endswith(".svg"):
                value = b'<svg xmlns="http://www.w3.org/2000/svg"><circle cx="10" cy="10" r="8"/></svg>'
            (self.root / "host/harness" / name).write_bytes(value)
        self.server = FakeServer()
        register_remote_update_routes(self.server, root=self.root)

    def request(self, route, method="GET", headers=None, params=None):
        h = [(k.lower().encode(), v.encode()) for k, v in (headers or {}).items()]
        req = Request({"type": "http", "method": method, "path": route,
                       "headers": h, "query_string": b"", "path_params": params or {}})
        return asyncio.run(self.server.routes[route][1](req))

    def test_sha_source_limits_and_android_boundary(self):
        o = build_remote_update_manifest(self.root, deployed_sha="a"*40)
        self.assertEqual(o["schema"], "luhmOs.remoteUpdateManifest.v2")
        self.assertTrue(o["sourceRefVerified"])
        self.assertEqual(len(o["assets"]), len(V2_PUBLIC_ASSETS))
        self.assertEqual([a["id"] for a in o["assets"]], list(V2_PUBLIC_ASSETS))
        self.assertEqual(o["crownStatus"], "STOP")
        self.assertFalse(o["autoInstall"])
        self.assertFalse(o["autoPublish"])
        self.assertFalse(o["remoteScriptExecution"])
        self.assertFalse(o["immutableDurableAssetArchiveProven"])
        self.assertEqual(o["cdnStatus"], "NOT_ACTIVATED_SAME_ORIGIN_ONLY")
        self.assertIsNone(o["android"]["apkUrl"])
        self.assertIsNone(o["android"]["releaseCertFingerprint"])
        self.assertEqual(o["plugin"]["shellVersion"], "0.5.2")
        self.assertEqual(o["plugin"]["resourceUri"], "ui://luhm-os/cockpit-v2.html")
        for item in o["assets"]:
            data = (self.root/"host/harness"/item["id"]).read_bytes()
            self.assertEqual(item["sha256"], hashlib.sha256(data).hexdigest())
            self.assertEqual(item["bytes"], len(data))
            self.assertIn(item["sha256"], item["path"])
            self.assertNotIn("https://", item["path"])

    def test_manifest_etag_head_and_no_cors(self):
        r = self.request(V2_MANIFEST_ROUTE)
        self.assertEqual(r.status_code, 200)
        self.assertIn("must-revalidate", r.headers["cache-control"])
        self.assertNotIn("access-control-allow-origin", r.headers)
        self.assertEqual(self.request(V2_MANIFEST_ROUTE, "HEAD").body, b"")
        self.assertEqual(self.request(V2_MANIFEST_ROUTE, headers={"If-None-Match": r.headers["etag"]}).status_code, 304)

    def test_digest_resource_and_cache(self):
        record = build_remote_update_manifest(self.root)["assets"][0]
        args = {"digest": record["sha256"], "filename": record["id"]}
        r = self.request(V2_ASSET_ROUTE, params=args)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.body, b"cockpit.css")
        self.assertIn("max-age=300", r.headers["cache-control"])
        self.assertNotIn("immutable", r.headers["cache-control"])
        self.assertNotIn("access-control-allow-origin", r.headers)
        self.assertEqual(self.request(V2_ASSET_ROUTE, "HEAD", params=args).body,b"")
        self.assertEqual(self.request(V2_ASSET_ROUTE, headers={"If-None-Match": r.headers["etag"]},params=args).status_code,304)
        self.assertEqual(self.request(V2_ASSET_ROUTE,params={**args,"digest":"0"*64}).status_code,404)
        self.assertEqual(self.request(V2_ASSET_ROUTE,params={**args,"filename":"../../secrets.txt"}).status_code,404)
        self.assertEqual(self.request(V2_ASSET_ROUTE,params={**args,"digest":"G"*64}).status_code,404)

    def test_inert_svg_policy(self):
        asset = next(x for x in build_remote_update_manifest(self.root)["assets"] if x["id"].endswith(".svg"))
        r = self.request(V2_ASSET_ROUTE,params={"digest":asset["sha256"],"filename":asset["id"]})
        self.assertEqual(r.status_code,200)
        self.assertIn("sandbox",r.headers["content-security-policy"])
        p = self.root/"host/harness/luhmSigil.svg"
        p.write_text('<svg><script>alert(1)</script></svg>')
        with self.assertRaisesRegex(ValueError, "SVG_ACTIVE"):
            build_remote_update_manifest(self.root)

    def test_symlink_and_css_remote_source_refused(self):
        p = self.root/"host/harness/fontStack.css"
        p.unlink()
        p.symlink_to(self.root/"plugins/luhm-os/plugin.json")
        with self.assertRaisesRegex(ValueError,"UNSAFE_ASSET"):
            build_remote_update_manifest(self.root)
        p.unlink()
        p.write_text('@import url("https://evil.example/malicious.css");')
        with self.assertRaisesRegex(ValueError,"CSS_REMOTE_IMPORT"):
            build_remote_update_manifest(self.root)

    def test_policy_auto_install_drift_rejected(self):
        p = self.root/"doctrine/selfHostedRemoteUpdatesV1.json"
        obj = json.loads(p.read_text())
        obj["automaticApkInstall"] = True
        p.write_text(json.dumps(obj))
        with self.assertRaisesRegex(ValueError,"AUTHORITY"):
            build_remote_update_manifest(self.root)
        r = self.request(V2_MANIFEST_ROUTE)
        self.assertEqual(r.status_code,503)
        self.assertEqual(r.headers["cache-control"],"no-store")

if __name__ == "__main__":
    unittest.main()

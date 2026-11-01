#!/usr/bin/env python3
"""Negative controls for optional Pi OS loopback web preview and source-only architecture."""
from __future__ import annotations
from copy import deepcopy
import http.client
import importlib.util
import json
from pathlib import Path
import threading
import unittest
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("pi_preview",ROOT/"tools/pi-kiosk/preview.py")
pi=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pi)

class PiKioskTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=json.loads(pi.POLICY_PATH.read_text(encoding="utf-8"))
    def testSourceContractFourByFour(self):
        p=pi.validate_policy(self.model)
        self.assertEqual(len(p["matrix"]),16)
        self.assertEqual([x["hex"] for x in p["matrix"]],[f"0x{i:02X}" for i in range(16)])
        self.assertEqual(p["baseline"]["distribution"],"Raspberry Pi OS Lite")
        self.assertFalse(p["baseline"]["customCompiledKernelInstalled"])
        self.assertFalse(p["baseline"]["physicalBoardVerified"])
        self.assertEqual(p["profiles"][0]["displayManager"],"NONE")
    def testLogicalHexCannotBecomeFirmwareAddress(self):
        for change in ({"hex":"0xD00D"},{"boardVerified":True},{"namespace":"biosPort"},
                       {"proof":"PHYSICAL_DEVICE_GREEN"}):
            with self.subTest(change=change):
                m=deepcopy(self.model)
                m["matrix"][4].update(change)
                with self.assertRaisesRegex(pi.PiPolicyError,"RED_PI_PI_HEX_SCOPE"):
                    pi.validate_policy(m)
    def testNoBootOrNetworkEscalation(self):
        for k in pi.EXPECTED_GUARDS:
            with self.subTest(guard=k):
                m=deepcopy(self.model)
                m["guards"][k]=False
                with self.assertRaisesRegex(pi.PiPolicyError,"RED_PI_PI_GUARDS"):
                    pi.validate_policy(m)
        for key in ("physicalBoardVerified","osImageInstalled","firmwareUpdated",
                    "customCompiledKernelInstalled","conventionalPCBIOS"):
            m=deepcopy(self.model);m["baseline"][key]=True
            with self.assertRaisesRegex(pi.PiPolicyError,"RED_PI_PI_FIRMWARE_TRUTH"):
                pi.validate_policy(m)
    def testHeadlessIsDefaultNotGdm(self):
        m=deepcopy(self.model);m["profiles"][2]["default"]=True
        with self.assertRaisesRegex(pi.PiPolicyError,"RED_PI_PI_HEADLESS_DEFAULT"):
            pi.validate_policy(m)
        m=deepcopy(self.model);m["optionalDisplay"]["gdmDefault"]=True
        with self.assertRaisesRegex(pi.PiPolicyError,"RED_PI_PI_DISPLAY"):
            pi.validate_policy(m)
    def testPreviewStrictLoopbackHttpMethodsAndHeaders(self):
        server=pi.create_server(0)
        thread=threading.Thread(target=server.serve_forever,daemon=True)
        thread.start()
        try:
            self.assertEqual(server.server_address[0],"127.0.0.1")
            port=server.server_address[1]
            conn=http.client.HTTPConnection("127.0.0.1",port,timeout=3)
            for target in ("/","/index.html","/style.css","/app.mjs","/src/workflow-rank.mjs","/healthz"):
                conn.request("GET",target)
                res=conn.getresponse()
                body=res.read()
                self.assertEqual(res.status,200,target)
                self.assertEqual(int(res.getheader("Content-Length")),len(body))
                self.assertIn("default-src 'none'",res.getheader("Content-Security-Policy"))
                self.assertEqual(res.getheader("Cache-Control"),"no-store, max-age=0")
                self.assertEqual(res.getheader("X-Content-Type-Options"),"nosniff")
                self.assertEqual(res.getheader("X-Frame-Options"),"DENY")
                self.assertIsNone(res.getheader("Set-Cookie"))
                if target=="/healthz":
                    payload=json.loads(body)
                    self.assertEqual(payload["status"],"AMBER_LOOPBACK_PREVIEW_ONLY")
                    self.assertFalse(payload["piBoardVerified"])
                    self.assertFalse(payload["serverPublic"])
            for path in ("/../secret","/%2e%2e/secret","/foo?bar=1","/private","/.git/config",
                         "/../../etc/passwd","/src/../../etc/passwd","/favicon.ico"):
                conn.request("GET",path)
                res=conn.getresponse();res.read()
                self.assertEqual(res.status,404,path)
            conn.request("HEAD","/index.html")
            h=conn.getresponse()
            self.assertEqual(h.status,200)
            self.assertGreater(int(h.getheader("Content-Length")),10)
            self.assertEqual(h.read(),b"")
            conn.close()
            for method in ("POST","PUT","DELETE","PATCH","OPTIONS"):
                denied=http.client.HTTPConnection("127.0.0.1",port,timeout=3)
                denied.request(method,"/index.html",body=b"not allowed")
                r=denied.getresponse();r.read()
                self.assertEqual(r.status,405,method)
                self.assertEqual(r.getheader("Allow"),"GET, HEAD")
                denied.close()
        finally:
            server.shutdown()
            thread.join(timeout=3)
            server.server_close()
    def testStaticAssetsBoundedAndNotSymlinks(self):
        for route,path in pi.ROUTES.items():
            data=pi.asset_bytes(path)
            self.assertTrue(0<len(data)<=65536,route)
        with self.assertRaises(pi.PiPolicyError):
            pi.asset_bytes("../../.git/config")
    def testPhoneGuiHasSafeActionsWithoutRuntimeClaims(self):
        page=pi.asset_bytes("demo/index.html").decode("utf-8")
        js=pi.asset_bytes("demo/app.mjs").decode("utf-8")
        sorter=pi.asset_bytes("src/workflow-rank.mjs").decode("utf-8")
        self.assertIn("Studio first.",page)
        self.assertIn("Not a live Godot or Unreal scene",page)
        self.assertIn("connect-src 'none'",page)
        self.assertIn("../src/workflow-rank.mjs",js)
        self.assertIn("session",sorter)
        for word in ("localStorage", "XMLHttpRequest", "fetch(", "eval("):
            self.assertNotIn(word,js)
    def testRejectRemotePortOnNormalRunAndUnknownDeviceGate(self):
        m=deepcopy(self.model)
        m["preview"]["loopbackAddress"]="0.0.0.0"
        with self.assertRaisesRegex(pi.PiPolicyError,"RED_PI_PI_HTTP_BOUNDARY"):
            pi.validate_policy(m)
        with self.assertRaisesRegex(pi.PiPolicyError,"RED_PI_PORT"):
            pi.create_server(-1)

if __name__=="__main__":
    unittest.main()

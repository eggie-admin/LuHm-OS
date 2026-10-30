#!/usr/bin/env python3
"""Offline, read-only K9000 capability server. Not an inference or driver daemon."""
from __future__ import annotations
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sqlite3
import threading
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
HARDWARE = ROOT / "doctrine/k9000UniversalHardwareV1.json"
SURFACE = ROOT / "doctrine/k9000UniversalVendorSurfaceV1.json"

def load_snapshot():
    hardware = json.loads(HARDWARE.read_text(encoding="utf-8"))
    surface = json.loads(SURFACE.read_text(encoding="utf-8"))
    return {
        "/healthz": {"schema":"luhmOs.k9000HeadlessHealth.v1","service":"K9000 local capability core",
                     "running":True,"inferenceRunning":False,"deviceProof":False,
                     "providerCalls":False,"agentWorkers":0,"crownStatus":"STOP"},
        "/v1/capabilities": {
            "schema":"luhmOs.k9000CapabilityInventory.v1",
            "status":"SOURCE_CONFIGURED_ONLY", "offline":True,
            "backend":"python3-stdlib-loopback", "data":"sqlite3-in-memory-smoke-only",
            "cloudProviderRequired":False, "driverWrites":False,
            "app":"LuHm-OS: Crown Cathedral"},
        "/v1/hardware": {"schema":"luhmOs.k9000HardwareReadOnly.v1",
                         "devices":[{"id":d["id"],"kind":d["kind"],"driver":d["driver"],
                                     "verifiedRuntime":d["verifiedRuntime"]} for d in hardware["inventory"]],
                         "physicalEnumeration":False},
        "/v1/providers": {"schema":"luhmOs.k9000ProviderReadOnly.v1",
                          "providerStatuses":{
                             "google":{k:v["readiness"] for k,v in surface["vendors"]["google"]["catalog"].items()},
                             "openAi":surface["vendors"]["openAi"]["readiness"],
                             "apple":surface["vendors"]["apple"]["readiness"]},
                          "connectedFromThisProcess":False}
    }

class LocalOnlyHTTP(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True
    def __init__(self,address,handler):
        host,port=address
        if host != "127.0.0.1":
            raise ValueError("K9000_HEADLESS_REQUIRES_LOOPBACK_BIND")
        super().__init__((host,port),handler)

class Handler(BaseHTTPRequestHandler):
    server_version = "K9000Local/1"
    sys_version = ""
    def log_message(self,format,*args):
        pass
    def do_GET(self):
        snapshots = self.server.snapshots
        if self.path not in snapshots:
            return self.send_result(404,{"error":"UNKNOWN_READ_ONLY_ROUTE"})
        self.send_result(200,snapshots[self.path])
    def do_HEAD(self):
        self.send_result(405,{"error":"GET_ONLY"})
    def do_POST(self):
        self.send_result(405,{"error":"READ_ONLY_NO_MUTATIONS"})
    def do_PUT(self):
        self.send_result(405,{"error":"READ_ONLY_NO_MUTATIONS"})
    def do_DELETE(self):
        self.send_result(405,{"error":"READ_ONLY_NO_MUTATIONS"})
    def send_result(self,status,payload):
        body=(json.dumps(payload,sort_keys=True,separators=(",",":"))+"\n").encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Content-Length",str(len(body)))
        self.send_header("Cache-Control","no-store")
        self.send_header("X-Content-Type-Options","nosniff")
        self.send_header("X-Frame-Options","DENY")
        self.end_headers()
        self.wfile.write(body)

def build_server(port=0):
    server=LocalOnlyHTTP(("127.0.0.1",port),Handler)
    server.snapshots=load_snapshot()
    return server

def sqlite_smoke():
    with sqlite3.connect(":memory:") as db:
        db.execute("CREATE TABLE capability (key TEXT PRIMARY KEY NOT NULL, value TEXT NOT NULL)")
        db.execute("INSERT INTO capability(key,value) VALUES (?,?)",("backend","headless"))
        row=db.execute("SELECT value FROM capability WHERE key=?",("backend",)).fetchone()
        if row != ("headless",):
            raise AssertionError("SQLITE_IN_MEMORY_SMOKE_FAILED")
    return True

def smoke():
    sqlite_smoke()
    server=build_server()
    t=threading.Thread(target=server.serve_forever,daemon=True)
    t.start()
    try:
        base="http://127.0.0.1:"+str(server.server_port)
        with urlopen(base+"/healthz",timeout=3) as response:
            assert json.load(response)["providerCalls"] is False
        with urlopen(base+"/v1/hardware",timeout=3) as response:
            assert len(json.load(response)["devices"]) >= 10
        with urlopen(base+"/v1/providers",timeout=3) as response:
            assert json.load(response)["connectedFromThisProcess"] is False
            assert response.headers.get("Access-Control-Allow-Origin") is None
        for request,expected in (
            (Request(base+"/v1/providers",data=b"{}",method="POST"),405),
            (Request(base+"/v1/undefined"),404)
        ):
            try:
                urlopen(request,timeout=3)
                raise AssertionError("HEADLESS_READ_ONLY_BOUNDARY_BYPASSED")
            except HTTPError as exc:
                if exc.code != expected:
                    raise AssertionError("UNEXPECTED_HTTP_BOUNDARY_STATUS") from exc
    finally:
        server.shutdown()
        server.server_close()
        t.join(timeout=3)
    return {"status":"HEADLESS_LOOPBACK_SMOKE_GREEN","sqlite":"IN_MEMORY_GREEN",
            "deviceHardware":"NOT_TESTED","modelInference":"NOT_CONNECTED",
            "cloudProvider":"NOT_CALLED","publicEndpoint":False}

if __name__ == "__main__":
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--smoke",action="store_true")
    ap.add_argument("--serve",action="store_true")
    ap.add_argument("--port",type=int,default=8789)
    args=ap.parse_args()
    if args.smoke:
        print(json.dumps(smoke(),sort_keys=True))
    elif args.serve:
        if not 1024 <= args.port <= 65535:
            ap.error("nonprivileged port required")
        with build_server(args.port) as srv:
            print("K9000_LOOPBACK_ONLY port="+str(srv.server_port),flush=True)
            srv.serve_forever()
    else:
        ap.error("choose --smoke or --serve")

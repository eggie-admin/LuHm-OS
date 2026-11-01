#!/usr/bin/env python3
"""Read-only Raspberry Pi pocket studio preview. ALWAYS loopback only."""
from __future__ import annotations

import argparse
from hashlib import sha256
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
ASSET_ROOT = ROOT / "tools/luhm-machine-agent"
POLICY_PATH = ROOT / "doctrine/piOsLiteMachineKioskV1.json"
HOST = "127.0.0.1"
MIME = {".html":"text/html; charset=utf-8",".css":"text/css; charset=utf-8",".mjs":"text/javascript; charset=utf-8"}
ROUTES = {
    "/":"demo/index.html",
    "/index.html":"demo/index.html",
    "/style.css":"demo/style.css",
    "/app.mjs":"demo/app.mjs",
    "/src/workflow-rank.mjs":"src/workflow-rank.mjs",
}
HEADERS = {
    "Cache-Control":"no-store, max-age=0",
    "X-Content-Type-Options":"nosniff",
    "X-Frame-Options":"DENY",
    "Referrer-Policy":"no-referrer",
    "Cross-Origin-Resource-Policy":"same-origin",
    "Permissions-Policy":"camera=(), microphone=(), geolocation=(), payment=()",
}
EXPECTED_LAYERS=["piBootKernel","headlessUserspace","studioServices","browserKiosk"]
EXPECTED_COLS=["inventory","authority","safeProof","propose"]
EXPECTED_GUARDS=[
    "noBootOrConfigWrite","noEepromWrite","noKernelBuild","noFlashSd",
    "noGpartedWrite","noGrubWrite","noHostAptInstall","noSystemdUnitInstall",
    "noRootServer","noPublicBind","noTailscaleOrVpnAutomaticSetup",
    "noCredentialsInSource","noPrivateArtExposure","noPaidRemoteCompute",
    "noGpuOrUnrealServer","noAgentPromotion","noProtectedMainMerge",
]
class PiPolicyError(ValueError):
    pass

def need(value, code):
    if not value:
        raise PiPolicyError("RED_PI_"+code)

def validate_policy(p):
    need(type(p) is dict and p.get("schema")=="luhmOs.piOsLiteMachineKiosk.v1" and
         p.get("authority")=="Professor" and p.get("crownStatus")=="STOP" and
         p.get("status")=="DRAFT_SOURCE_ONLY","POLICY")
    need(p.get("sourceLaw")=="AI proposes. Policy authorizes. CI proves. Human promotes.","LAW")
    b=p.get("baseline",{})
    need(b.get("distribution")=="Raspberry Pi OS Lite" and
         b.get("release")=="Debian 13 Trixie" and b.get("architecture")=="aarch64" and
         b.get("upstreamKernelFamily")=="6.18" and
         all(b.get(k) is False for k in (
           "conventionalPCBIOS","pcGrubRequired","customCompiledKernelInstalled",
           "physicalBoardVerified","osImageInstalled","firmwareUpdated")),"PI_FIRMWARE_TRUTH")
    need([x.get("id") for x in p.get("layers",[])]==EXPECTED_LAYERS and
         p.get("columns")==EXPECTED_COLS and len(p.get("matrix",[]))==16,"PI_AXES")
    for i,cell in enumerate(p["matrix"]):
        need(type(cell) is dict and cell=={
            "index":i,"hex":f"0x{i:02X}","namespace":"piOsMachine",
            "layer":EXPECTED_LAYERS[i//4],"column":EXPECTED_COLS[i%4],
            "proof":"SOURCE_ONLY","boardVerified":False
        },"PI_HEX_SCOPE")
    need([x.get("id") for x in p.get("hardware",[])]==
         ["pi5","pi4","pi3","zero2"] and
         all(x.get("proven") is False for x in p["hardware"]),"PI_DEVICE_PROOF")
    profiles=p.get("profiles",[])
    need([x.get("id") for x in profiles]==
         ["headless","remoteStudioPreview","localKiosk","gnomeOrCinnamon"] and
         [x.get("default") for x in profiles]==[True,False,False,False] and
         profiles[0].get("displayManager")=="NONE" and
         profiles[0].get("exposedListeners")==[],"PI_HEADLESS_DEFAULT")
    preview=p.get("preview",{})
    need(preview.get("loopbackAddress")==HOST and
         preview.get("defaultPort")==8765 and
         preview.get("assetPaths")==list(ROUTES)+["/healthz"] and
         preview.get("httpMethods")==["GET","HEAD"] and
         preview.get("maxAssetBytes")==65536 and
         preview.get("authentication")=="LOOPBACK_ONLY_NOT_SAFE_TO_EXPOSE_TO_LAN" and
         all(preview.get(k) is True for k in (
           "noPathTraversal","noSymlinks","blockNetworkClients","stateless")) and
         preview.get("uploadRoutes") is False,"PI_HTTP_BOUNDARY")
    need(all(p.get("guards",{}).get(g) is True for g in EXPECTED_GUARDS) and
         set(p.get("guards",{}))==set(EXPECTED_GUARDS),"PI_GUARDS")
    need(p.get("optionalDisplay",{}).get("gdmDefault") is False and
         p["optionalDisplay"].get("labwcOptional") is True and
         p["optionalDisplay"].get("remoteFirst") is True,"PI_DISPLAY")
    need(p.get("proofGates",[])[-1]=="ownerReleaseApproval","PI_PROMOTION")
    return p

def load_policy():
    return validate_policy(json.loads(POLICY_PATH.read_text(encoding="utf-8")))

def asset_bytes(rel):
    # Server-controlled path list only. Never use input URL as filesystem path.
    p = ASSET_ROOT / rel
    root=ASSET_ROOT.resolve()
    need(not p.is_symlink() and p.is_file() and p.resolve().is_relative_to(root) and
         not any(x.is_symlink() for x in (p.parent,p.parent.parent) if x!=root),
         "ASSET_PATH")
    data=p.read_bytes()
    need(0<len(data)<=65536,"ASSET_SIZE")
    return data

class Handler(BaseHTTPRequestHandler):
    server_version = "LuHm-Pocket/0.1"
    sys_version = ""
    def log_message(self, _format, *args):
        # Never echo paths, query strings, headers or client identifiers.
        return
    def _answer(self, send_body=True):
        # Do not serve a DNS-rebound domain that happens to resolve to 127.0.0.1.
        # Only the advertised local origin may receive the studio assets.
        expected_host=f"127.0.0.1:{self.server.server_port}"
        if self.headers.get("Host", "")!=expected_host:
            data=b"Invalid local host"
            self.send_response(421)
            self.send_header("Content-Type","text/plain; charset=utf-8")
            self.send_header("Content-Length",str(len(data)))
            self.send_header("Cache-Control","no-store")
            self.send_header("X-Content-Type-Options","nosniff")
            self.send_header("Connection","close")
            self.end_headers()
            if send_body:
                self.wfile.write(data)
            self.close_connection=True
            return
        route=self.path
        if route=="/healthz":
            data=json.dumps({
                "schema":"luhmOs.piKioskHealth.v1",
                "status":"AMBER_LOOPBACK_PREVIEW_ONLY",
                "sourceOnly":True,"piBoardVerified":False,
                "serverPublic":False,"remoteAgentStarted":False,"crownStatus":"STOP",
            },sort_keys=True,separators=(",",":")).encode("utf-8")
            mime="application/json; charset=utf-8"
            status=200
        elif route in ROUTES:
            try:
                data=asset_bytes(ROUTES[route])
            except (OSError,PiPolicyError):
                data=b"Missing authorized asset";status=404;mime="text/plain; charset=utf-8"
            else:
                status=200;mime=MIME[Path(ROUTES[route]).suffix]
        else:
            data=b"Not found";status=404;mime="text/plain; charset=utf-8"
        self.send_response(status)
        self.send_header("Content-Type",mime)
        self.send_header("Content-Length",str(len(data)))
        for k,v in HEADERS.items():
            self.send_header(k,v)
        self.send_header("Content-Security-Policy",self.server.policy["preview"]["csp"])
        self.end_headers()
        if send_body:
            self.wfile.write(data)
    def do_GET(self):
        self._answer()
    def do_HEAD(self):
        self._answer(False)
    def do_POST(self):
        self.send_response(405)
        self.send_header("Allow","GET, HEAD")
        self.send_header("Connection","close")
        self.send_header("Content-Length","0")
        self.close_connection=True
        self.end_headers()
    do_PUT=do_POST
    do_PATCH=do_POST
    do_DELETE=do_POST
    def do_OPTIONS(self):
        self.do_POST()

def create_server(port=8765):
    need(type(port) is int and 0<=port<=65535,"PORT")
    policy=load_policy()
    http=HTTPServer((HOST,port),Handler)
    http.policy=policy
    return http

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port",type=int,default=8765)
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    policy=load_policy()
    if args.check:
        rows=[{"asset":k,"sha256":sha256(asset_bytes(v)).hexdigest()}
              for k,v in ROUTES.items() if k!="/"]
        print(json.dumps({"status":"AMBER_SOURCE_ONLY",
            "matrixCells":len(policy["matrix"]),"assets":rows,
            "kernelChanged":False,"deviceVerified":False,"listenerStarted":False,
            "crownStatus":"STOP"},sort_keys=True))
        return
    need(1024<=args.port<=65535,"PORT_RANGE")
    if hasattr(os,"geteuid"):
        need(os.geteuid()!=0,"NO_ROOT_SERVER")
    with create_server(args.port) as http:
        print(f"Pi pocket studio preview is loopback-only: http://{HOST}:{args.port}/",flush=True)
        http.serve_forever(poll_interval=.2)

if __name__=="__main__":
    main()

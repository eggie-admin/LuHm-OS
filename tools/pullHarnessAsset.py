#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import mimetypes
import socket
import ssl
import sys
import urllib.parse
import urllib.request
from pathlib import Path

rootPath=Path(__file__).resolve().parents[1]
policy=json.loads((rootPath/"doctrine/harnessAssetIntakeV1.json").read_text())
maxBytes=int(policy["remoteImagePolicy"]["maxBytes"])
googleHosts=set(policy["lanes"]["googleFonts"]["allowedHosts"])

def die(msg):
    print(json.dumps({"status":"redAssetPull","error":msg},indent=2))
    raise SystemExit(2)

def publicHost(host):
    try:
        infos=socket.getaddrinfo(host,443,type=socket.SOCK_STREAM)
    except OSError as e:
        die(f"dns_failed:{e}")
    for info in infos:
        ip=ipaddress.ip_address(info[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved:
            die(f"non_public_address:{ip}")

def sanitizeSvg(data:bytes)->bytes:
    text=data.decode("utf-8","strict")
    bad=["<script","<foreignObject","javascript:","data:"," onload="," onclick="," onerror="," href="http"," href='http"," xlink:href="http"," xlink:href='http"]
    lower=text.lower()
    for token in bad:
        if token.lower() in lower:
            die(f"unsafe_svg_token:{token}")
    if "<svg" not in lower:
        die("not_svg")
    return text.encode("utf-8")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("url")
    p.add_argument("--out",required=True)
    p.add_argument("--kind",choices=["image","svg","font"],required=True)
    p.add_argument("--allow-host",dest="allowHost",action="append",default=[])
    p.add_argument("--receipt",required=True)
    args=p.parse_args()

    u=urllib.parse.urlparse(args.url)
    if u.scheme!="https" or not u.hostname:
        die("https_url_required")
    allowed=set(args.allowHost)
    if args.kind=="font":
        allowed |= googleHosts
    if u.hostname not in allowed:
        die(f"host_not_allowlisted:{u.hostname}")
    publicHost(u.hostname)

    req=urllib.request.Request(args.url,headers={"User-Agent":"LuHmOS-AssetIntake/1"})
    ctx=ssl.create_default_context()
    with urllib.request.urlopen(req,context=ctx,timeout=30) as r:
        final=urllib.parse.urlparse(r.geturl())
        if final.scheme!="https" or final.hostname not in allowed:
            die("redirect_left_allowlist")
        data=r.read(maxBytes+1)
        ctype=(r.headers.get_content_type() or "application/octet-stream").lower()

    if len(data)>maxBytes:
        die("asset_too_large")
    if args.kind=="svg":
        if ctype not in {"image/svg+xml","text/xml","application/xml","text/plain"}:
            die(f"unexpected_svg_mime:{ctype}")
        data=sanitizeSvg(data)
    elif args.kind=="font":
        if not (ctype.startswith("font/") or ctype in {"application/font-woff","application/octet-stream"}):
            die(f"unexpected_font_mime:{ctype}")
    elif not ctype.startswith("image/"):
        die(f"unexpected_image_mime:{ctype}")

    out=Path(args.out)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_bytes(data)
    sha=hashlib.sha256(data).hexdigest()
    receipt={
      "schema":"luhmOs.assetPullReceipt.v1",
      "status":"quarantined",
      "sourceUrl":args.url,
      "finalUrl":urllib.parse.urlunparse((final.scheme,final.netloc,final.path,"","","")),
      "host":final.hostname,
      "kind":args.kind,
      "mime":ctype,
      "bytes":len(data),
      "sha256":sha,
      "output":str(out),
      "runtimeAuthority":False,
      "promotionAuthority":False,
      "crownStatus":"stop"
    }
    rp=Path(args.receipt)
    rp.parent.mkdir(parents=True,exist_ok=True)
    rp.write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps(receipt,indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())

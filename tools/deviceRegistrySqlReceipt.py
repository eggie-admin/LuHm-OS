#!/usr/bin/env python3
"""Fail-closed JS↔Python↔SQLite STRICT packet parity, source-only and stdin bounded."""
from __future__ import annotations
import base64
import binascii
import hashlib
import hmac
import json
from pathlib import Path
import re
import sqlite3
import sys
import unicodedata

ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/"doctrine/deviceCapabilityRegistryV1.json"
HEX=[f"0x{i:02X}" for i in range(16)]
FIELDS={"schema","registryHex","kind","byteCount","payloadBase64","sha256","rssBytes","rightsState"}
KINDS={"artNote","buildReceipt","benchmarkReceipt"}
BASE64=re.compile(r"(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?\Z",re.ASCII)
DIGEST=re.compile(r"[a-f0-9]{64}\Z",re.ASCII)
MAX_JSON=8192

class DevicePacketError(ValueError):
    pass

def fail(code):
    raise DevicePacketError("RED_"+code)

def registry_check(r):
    if (type(r) is not dict or r.get("schema")!="luhmOs.deviceCapabilityRegistry.v1"
            or r.get("authority")!="Professor" or r.get("crownStatus")!="STOP"
            or r.get("status")!="DRAFT_SOURCE_ONLY" or r.get("namespace")!="deviceCapability"):
        fail("REGISTRY")
    platforms=["android","samsung","ios","webLinux"]
    caps=["runtime","graphics","storage","distribution"]
    if r.get("platforms")!=platforms or r.get("capabilities")!=caps or type(r.get("entries")) is not list or len(r["entries"])!=16:
        fail("REGISTRY_AXES")
    for i,entry in enumerate(r["entries"]):
        if (type(entry) is not dict or entry.get("hex")!=HEX[i] or entry.get("index")!=i
                or entry.get("namespace")!="deviceCapability"
                or entry.get("platform")!=platforms[i//4] or entry.get("capability")!=caps[i%4]
                or entry.get("proof")!="SOURCE_REVIEW_ONLY" or entry.get("deviceVerified") is not False):
            fail("REGISTRY_HEX")
    if (r.get("typedPacket",{}).get("maxUtf8Bytes")!=4096
            or r.get("typedPacket",{}).get("maxRawBase64Bytes")!=4096):
        fail("REGISTRY_LIMITS")
    if r.get("safety",{}).get("sourceOnly") is not True or any(v is not False for k,v in r["safety"].items() if k!="sourceOnly"):
        fail("REGISTRY_PROMOTION")
    return True

def decode_packet(p):
    if (type(p) is not dict or set(p)!=FIELDS
            or p.get("schema")!="luhmOs.typedArtMachinePacket.v1"
            or p.get("registryHex") not in HEX
            or p.get("kind") not in KINDS
            or type(p.get("byteCount")) is not int or not 1<=p["byteCount"]<=4096
            or type(p.get("payloadBase64")) is not str or len(p["payloadBase64"])>5464
            or BASE64.fullmatch(p["payloadBase64"]) is None
            or type(p.get("sha256")) is not str or DIGEST.fullmatch(p["sha256"]) is None
            or p.get("rightsState")!="LOCAL_DRAFT"):
        fail("PACKET_SHAPE")
    rss=p["rssBytes"]
    if rss is not None and (type(rss) is not int or not 0<=rss<=9007199254740991):
        fail("RSS_BYTES")
    try:
        raw=base64.b64decode(p["payloadBase64"],validate=True)
    except (binascii.Error,ValueError) as exc:
        raise DevicePacketError("RED_BASE64") from exc
    if len(raw)!=p["byteCount"] or len(raw)>4096 or base64.b64encode(raw).decode("ascii")!=p["payloadBase64"]:
        fail("BASE64_LENGTH_CANONICAL")
    if not hmac.compare_digest(hashlib.sha256(raw).hexdigest(),p["sha256"]):
        fail("PACKET_HASH")
    try:
        text=raw.decode("utf-8",errors="strict")
    except UnicodeError as exc:
        raise DevicePacketError("RED_PACKET_UTF8") from exc
    if unicodedata.normalize("NFC",text)!=text or not text or any(ord(c)<32 and c not in "\n\t" for c in text) or "\x7f" in text or "\n" in text or "\t" in text:
        fail("TEXT_CANONICAL")
    if text.encode("utf-8")!=raw:
        fail("TEXT_ROUNDTRIP")
    return {"utf8Bytes":len(raw),"registryHex":p["registryHex"],"rssBytes":rss,
            "sha256":p["sha256"],"kind":p["kind"]}

def sql_receipt(packet):
    info=decode_packet(packet)
    with sqlite3.connect(":memory:") as db:
        db.execute("""CREATE TABLE devicePacket(
            hex TEXT NOT NULL CHECK(length(hex)=4),
            byte_count INTEGER NOT NULL CHECK(byte_count BETWEEN 1 AND 4096),
            sha256 TEXT NOT NULL CHECK(length(sha256)=64 AND sha256 NOT GLOB '*[^0-9a-f]*'),
            rss_bytes INTEGER CHECK(rss_bytes BETWEEN 0 AND 9007199254740991)
          ) STRICT""")
        db.execute("INSERT INTO devicePacket VALUES(?,?,?,?)",
                   (info["registryHex"],info["utf8Bytes"],info["sha256"],info["rssBytes"]))
        row=db.execute("SELECT hex,byte_count,sha256,rss_bytes FROM devicePacket").fetchone()
    if tuple(row)!=(info["registryHex"],info["utf8Bytes"],info["sha256"],info["rssBytes"]):
        fail("SQL_PARITY")
    return {"schema":"luhmOs.devicePacketSqlReceipt.v1","status":"AMBER_SOURCE_ONLY",
            "hex":info["registryHex"],"byteCount":info["utf8Bytes"],
            "sha256":info["sha256"],"rssBytes":info["rssBytes"],
            "sqlite":"IN_MEMORY_STRICT","rows":1,"sqlServiceStarted":False,
            "deviceVerified":False,"kernelChanged":False,"crownStatus":"STOP"}

def main():
    registry_check(json.loads(REGISTRY.read_text(encoding="utf-8")))
    data=sys.stdin.buffer.read(MAX_JSON+1)
    if not data or len(data)>MAX_JSON:
        fail("INPUT_BUDGET")
    # Reject NaN, duplicate JSON keys, and parse only a fixed packet.
    def unique(pairs):
        output={}
        for k,v in pairs:
            if k in output:
                fail("JSON_DUPLICATE_KEY")
            output[k]=v
        return output
    obj=json.loads(data.decode("utf-8"),object_pairs_hook=unique,
                   parse_constant=lambda v:fail("JSON_NONFINITE"))
    print(json.dumps(sql_receipt(obj),sort_keys=True,separators=(",",":")))

if __name__=="__main__":
    try:
        main()
    except (DevicePacketError,UnicodeError,ValueError,sqlite3.Error) as error:
        print("DEVICE_PACKET_REJECTED: "+str(error)[:120],file=sys.stderr)
        raise SystemExit(2)

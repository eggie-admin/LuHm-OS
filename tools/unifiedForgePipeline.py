#!/usr/bin/env python3
"""Read-only AI task JSON -> SQLite STRICT JSON1 -> safe UI projection."""
import base64
import binascii
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess

ROOT=Path(__file__).resolve().parents[1]
MAX_BYTES=44*1024
SOURCE=re.compile(r"^[0-9a-f]{40}$")
ID=re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,79}$")
B64=re.compile(r"^[A-Za-z0-9_-]+$")

def no_duplicate_pairs(pairs):
    out={}
    for k,v in pairs:
        if k in out:
            raise ValueError("DUPLICATE_JSON_KEY")
        out[k]=v
    return out

def decode(payload):
    if not isinstance(payload,str) or len(payload)>MAX_BYTES*2 or not B64.fullmatch(payload):
        raise ValueError("INVALID_BASE64URL")
    try:
        raw=base64.urlsafe_b64decode(payload+"="*((-len(payload))%4))
    except (ValueError,binascii.Error) as e:
        raise ValueError("BASE64URL_DECODE_FAILED") from e
    if len(raw)>MAX_BYTES or not raw:
        raise ValueError("MANIFEST_SIZE_LIMIT")
    if base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")!=payload:
        raise ValueError("NON_CANONICAL_BASE64URL")
    try:
        return json.loads(raw.decode("utf-8"),object_pairs_hook=no_duplicate_pairs,
                          parse_constant=lambda v: (_ for _ in ()).throw(ValueError("NONFINITE_JSON")))
    except (UnicodeDecodeError,json.JSONDecodeError) as e:
        raise ValueError("INVALID_JSON_UTF8") from e

def encode(obj):
    raw=json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False,
                   allow_nan=False).encode("utf-8")
    if len(raw)>MAX_BYTES:raise ValueError("MANIFEST_SIZE_LIMIT")
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")

def validate(obj,source_ref):
    if not isinstance(obj,dict) or obj.get("schema")!="luhmOs.aiTaskManifest.v2":
        raise ValueError("MANIFEST_SCHEMA_MISMATCH")
    if not SOURCE.fullmatch(source_ref) or obj.get("sourceRef")!=source_ref:
        raise ValueError("SOURCE_MISMATCH")
    for key in ("taskId","scopeId","providerId","capabilityId"):
        if not isinstance(obj.get(key),str) or not ID.fullmatch(obj[key]):
            raise ValueError("INVALID_FIELD:"+key)
    if obj["providerId"]!="local" or obj["capabilityId"]!="forgeSourceAudit":
        raise ValueError("EXECUTING_PROVIDER_NOT_ALLOWED")
    if obj.get("status")!="SOURCE_CANDIDATE":
        raise ValueError("UNEXPECTED_STATUS")
    budget=obj.get("budget")
    if not isinstance(budget,dict) or budget!={"maxRequests":0,"maxParallel":0,"maxPasses":1}:
        raise ValueError("RUNTIME_BUDGET_NOT_ALLOWED")
    auth=obj.get("authority")
    if auth!={"mutation":False,"green":False,"crown":False}:
        raise ValueError("MANIFEST_AUTHORITY_NOT_ALLOWED")
    if obj.get("inputRefs")!=[] or obj.get("requiredOutputSchema")!="luhmOs.forgeSourceProjection.v1":
        raise ValueError("UNBOUNDED_INPUT_OR_OUTPUT")
    if obj.get("mode") not in ("headless","witchingHour","corporate","githubDevelopment"):
        raise ValueError("INVALID_MODE")
    if type(obj.get("tier")) is not int or not 0<=obj["tier"]<=3:
        raise ValueError("INVALID_ESCALATION")
    permitted={"schema","taskId","sourceRef","scopeId","providerId","capabilityId","status",
               "budget","authority","inputRefs","requiredOutputSchema","mode","tier"}
    if set(obj)!=permitted: raise ValueError("UNKNOWN_MANIFEST_KEYS")
    return obj

def project(obj,source_ref):
    validate(obj,source_ref)
    db=sqlite3.connect(":memory:")
    try:
        db.executescript((ROOT/"host/api/typedLanesV1.sql").read_text(encoding="utf-8"))
        canonical=json.dumps(obj,sort_keys=True,separators=(",",":"),allow_nan=False)
        event="forge-"+hashlib.sha256(canonical.encode()).hexdigest()[:30]
        db.execute("INSERT INTO streamEvent(eventId,taskId,sourceRef,scopeId,workerId,sequenceId,eighthNote,observedAt,evidenceRef) VALUES(?,?,?,?,?,?,?,?,?)",
          (event,obj["taskId"],source_ref,obj["scopeId"],"lum-source-only",0,1,
           "2026-10-30T00:00:00Z","sourceOnly"))
        db.execute("INSERT INTO aiManifestStream(eventId,manifestJson,manifestSchema,providerId,capabilityId) VALUES(?,?,?,?,?)",
          (event,canonical,obj["schema"],obj["providerId"],obj["capabilityId"]))
        row=db.execute("SELECT json_extract(manifestJson,'$.mode'),json_extract(manifestJson,'$.tier'),sourceRef,mutationAuthority,greenAuthority,crownAuthority FROM aiManifestStream JOIN streamEvent USING(eventId) WHERE eventId=?",(event,)).fetchone()
        if row!=(obj["mode"],obj["tier"],source_ref,0,0,0):
            raise ValueError("SQL_JSON1_PROJECTION_MISMATCH")
        db.commit()
    finally:
        db.close()
    return {"schema":"luhmOs.forgeSourceProjection.v1","sourceRef":source_ref,
            "taskId":obj["taskId"],"scopeId":obj["scopeId"],
            "mode":obj["mode"],"tier":obj["tier"],"sql":"SQLITE_STRICT_JSON1_GREEN",
            "workerExecuted":False,"providerConnected":False,"authorityEffect":"none",
            "crownStatus":"STOP","evidenceHash":hashlib.sha256(canonical.encode()).hexdigest()}

def current_source():
    sha=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
    env=os.environ.get("LUHM_SOURCE_REF")
    if env and env!=sha:raise ValueError("EXACT_SOURCE_REQUIRED")
    return sha

if __name__=="__main__":
    sha=current_source()
    obj={"schema":"luhmOs.aiTaskManifest.v2","taskId":"forge-source-smoke",
         "sourceRef":sha,"scopeId":"source-only","providerId":"local","capabilityId":"forgeSourceAudit",
         "status":"SOURCE_CANDIDATE","mode":"headless","tier":0,
         "budget":{"maxRequests":0,"maxParallel":0,"maxPasses":1},
         "authority":{"mutation":False,"green":False,"crown":False},
         "inputRefs":[],"requiredOutputSchema":"luhmOs.forgeSourceProjection.v1"}
    print(json.dumps(project(decode(encode(obj)),sha),sort_keys=True))

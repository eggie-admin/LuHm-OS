#!/usr/bin/env python3
"""One-app four-lane planning receipt. No remote call, socket, user login or tool invocation.

Maps requested read-only capability to a declared transport plan; records it in
an ephemeral SQLite STRICT/JSON1 table and returns an HTML5-safe projection.
This is architecture evidence, NOT evidence that the chosen transport is live.
"""
from __future__ import annotations
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import sqlite3
import subprocess

ROOT=Path(__file__).resolve().parents[1]
CAPABILITIES=("sourceStatus","browserPreview","studioHardwareInventory","mediaPlan")
ROLE_MAP={"sourceStatus":"skuldResearch","browserPreview":"lum",
          "studioHardwareInventory":"tetsu","mediaPlan":"yume"}
TRANSPORTS=("currentRenderDirect","candidateCloudflareTunnel",
            "privateStudioLoopback","offlineFallback")
LANES=("nightly","beta","lts","legacy")
SCHEMA="luhmOs.universalRoutePlan.v1"
SHA_RE=re.compile(r"^[0-9a-f]{40}$")
ID_RE=re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,79}$")

def exact_sha(root=ROOT):
    proc=subprocess.run(["git","rev-parse","HEAD"],cwd=root,
                        capture_output=True,text=True,check=False)
    candidate=proc.stdout.strip()
    if proc.returncode or not SHA_RE.fullmatch(candidate):
        raise ValueError("EXACT_SHA_REQUIRED")
    if os.getenv("LUHM_SOURCE_REF") and os.environ["LUHM_SOURCE_REF"]!=candidate:
        raise ValueError("EXACT_SHA_MISMATCH")
    return candidate

def contract(root=ROOT):
    policy=json.loads((root/"doctrine/universalFourLaneV1.json").read_text())
    if policy.get("schema")!="luhmOs.universalFourLaneV1":
        raise ValueError("POLICY_SCHEMA")
    return policy

def plan(lane,capability,transport,task_id,source_ref,root=ROOT):
    policy=contract(root)
    if lane not in LANES or capability not in CAPABILITIES or transport not in TRANSPORTS:
        raise ValueError("ROUTE_NOT_ALLOWLISTED")
    if not isinstance(task_id,str) or not ID_RE.fullmatch(task_id):
        raise ValueError("INVALID_TASK_ID")
    if not isinstance(source_ref,str) or not SHA_RE.fullmatch(source_ref):
        raise ValueError("INVALID_SOURCE_SHA")
    if policy["agents"]["workersActive"]!=0 or not policy["agents"]["allFifteenQuarantined"]:
        raise ValueError("AGENT_QUARANTINE_REQUIRED")
    if policy["safety"]["crownStatus"]!="STOP":
        raise ValueError("CROWN_STOP_REQUIRED")
    role=ROLE_MAP[capability]
    if role not in policy["agents"]["proposalSix"]:
        raise ValueError("ROLE_IS_NOT_CANONICAL")
    row={"schema":SCHEMA,"sourceRef":source_ref,"taskId":task_id,
         "lane":lane,"transport":transport,"capability":capability,
         "proposedRole":role,"status":"SOURCE_ONLY",
         "routeAvailable":False,"workerExecuted":False,"providerConnected":False,
         "authorizedToMutate":False,"crownStatus":"STOP"}
    canonical=json.dumps(row,sort_keys=True,separators=(",",":"),ensure_ascii=True)
    # No live mailbox or network, only a fixed in-memory database.
    with sqlite3.connect(":memory:") as db:
        db.execute("""CREATE TABLE route_plan (
          task_id TEXT PRIMARY KEY, source_ref TEXT NOT NULL,
          lane TEXT NOT NULL CHECK(lane IN ('nightly','beta','lts','legacy')),
          transport TEXT NOT NULL, manifest TEXT NOT NULL CHECK(json_valid(manifest)),
          crown INTEGER NOT NULL DEFAULT 0 CHECK(crown=0)
        ) STRICT""")
        db.execute("INSERT INTO route_plan(task_id,source_ref,lane,transport,manifest) VALUES(?,?,?,?,?)",
                   (task_id,source_ref,lane,transport,canonical))
        stored=db.execute("SELECT json_extract(manifest,'$.proposedRole'),lane,source_ref,crown FROM route_plan WHERE task_id=?",(task_id,)).fetchone()
        if stored!=(role,lane,source_ref,0):
            raise ValueError("SQL_JSON_PROJECTION_MISMATCH")
    row["evidenceHash"]=hashlib.sha256(canonical.encode()).hexdigest()
    return row

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--lane",default="lts",choices=LANES)
    parser.add_argument("--capability",default="sourceStatus",choices=CAPABILITIES)
    parser.add_argument("--transport",default="offlineFallback",choices=TRANSPORTS)
    parser.add_argument("--task",default="universal-source-receipt")
    args=parser.parse_args()
    result=plan(args.lane,args.capability,args.transport,args.task,exact_sha())
    print(json.dumps(result,sort_keys=True))
if __name__=="__main__":
    main()

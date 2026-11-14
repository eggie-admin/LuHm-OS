#!/usr/bin/env python3
"""LuHm-OS optional remote PostgreSQL audit/sync; disabled until verified provider and explicit approval.

Requires the reviewed typedPostgresReviewV1.sql schema already applied by an authorized migrator.
Never exposes SQL ports, credentials, or untrusted query input. No remote DDL.
"""
from __future__ import annotations
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, parse_qs

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))
from machineLayerSql import MachineLayerError, require, loadManifest, eventsFor

def validateRemoteEnvironment(env=None):
    env=os.environ if env is None else env
    require(env.get("LUHM_REMOTE_SQL_SYNC") == "scopedSourceTxRx", "remote sync not explicitly enabled")
    connUrl=env.get("LUHM_DATABASE_URL", "")
    require(bool(connUrl) and len(connUrl) <= 4096, "private database URL missing")
    parts=urlsplit(connUrl)
    require(parts.scheme in ("postgresql","postgres") and parts.hostname and parts.port != 0, "invalid PostgreSQL target")
    require(bool(parts.username and parts.password), "least-privilege user/password required")
    query=parse_qs(parts.query)
    require(query.get("sslmode")==["verify-full"], "TLS server identity verification required")
    require(bool(query.get("sslrootcert", [""])[0]), "private CA root path required")
    rootCert=Path(query["sslrootcert"][0])
    require(rootCert.is_file(), "configured PostgreSQL CA file missing")
    return connUrl

def synchronize(conn, snapshot, mutate=False):
    # Read/write only known typed event rows, never arbitrary scripts or user-generated SQL.
    sourceRef=snapshot["baselineSourceRef"]
    expected=eventsFor(snapshot)
    now=datetime.now(timezone.utc)
    applied=0
    with conn.transaction():
        with conn.cursor() as cur:
            # Fail closed if the reviewed remote schema has not been installed.
            cur.execute("SELECT to_regclass('public.streamevent'), to_regclass('public.textstream'), to_regclass('public.booleanstream')")
            row=cur.fetchone()
            require(row is not None and all(item is not None for item in row), "reviewed remote schema absent")
            for event in expected:
                if mutate:
                    cur.execute("""INSERT INTO streamEvent(eventId,taskId,sourceRef,scopeId,workerId,sequenceId,eighthNote,observedAt,evidenceRef)
                        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT(eventId) DO NOTHING""",
                        (event["eventId"],event["taskId"],sourceRef,event["scopeId"],event["workerId"],event["sequenceId"],event["eighthNote"],now,"machineLayerSourceSnapshot"))
                    applied+=cur.rowcount
                    for k,v in event["texts"].items():
                        cur.execute("INSERT INTO textStream(eventId,fieldName,textValue) VALUES(%s,%s,%s) ON CONFLICT(eventId,fieldName) DO NOTHING",
                                    (event["eventId"],k,v))
                    for k,v in event["booleans"].items():
                        cur.execute("INSERT INTO booleanStream(eventId,fieldName,booleanValue) VALUES(%s,%s,%s) ON CONFLICT(eventId,fieldName) DO NOTHING",
                                    (event["eventId"],k,v))
                cur.execute("SELECT sourceRef,taskId,scopeId,workerId,sequenceId,eighthNote FROM streamEvent WHERE eventId=%s",(event["eventId"],))
                found=cur.fetchone()
                require(found is not None and tuple(found)==(sourceRef,event["taskId"],event["scopeId"],event["workerId"],event["sequenceId"],event["eighthNote"]), "remote event mismatch")
                for k,v in event["texts"].items():
                    cur.execute("SELECT textValue FROM textStream WHERE eventId=%s AND fieldName=%s",(event["eventId"],k))
                    value=cur.fetchone()
                    require(value is not None and value[0]==v, "remote text mismatch")
                for k,v in event["booleans"].items():
                    cur.execute("SELECT booleanValue FROM booleanStream WHERE eventId=%s AND fieldName=%s",(event["eventId"],k))
                    value=cur.fetchone()
                    require(value is not None and value[0] is v, "remote boolean mismatch")
    return {"status":"REMOTE_TYPED_SQL_TXRX_VERIFIED" if mutate else "REMOTE_READBACK_VERIFIED",
            "verifiedRecords":len(expected),"inserted":applied,"sourceRef":sourceRef,
            "scopeId":"machineLayer","crown":"STOP","quarantine":"UNCHANGED"}

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode",choices=("readBack","txRx"),required=True)
    args=parser.parse_args(argv)
    try:
        snapshot=loadManifest()
        url=validateRemoteEnvironment()
        # Optional import: must be installed in the authenticated Render runtime, not in PR audit.
        import psycopg
        with psycopg.connect(url, connect_timeout=6, autocommit=True) as conn:
            result=synchronize(conn,snapshot,mutate=args.mode=="txRx")
        print(json.dumps(result,sort_keys=True))
        return 0
    except (Exception,) as exc:
        # Do not print connection URLs, DB hostnames, usernames, secrets or provider messages.
        reason="remote SQL not available or verification rejected"
        if isinstance(exc,MachineLayerError): reason=str(exc)
        print(json.dumps({"status":"BLOCKED","reason":reason,"remoteConnectionVerified":False,"crown":"STOP"}))
        return 1

if __name__=="__main__":
    raise SystemExit(main())

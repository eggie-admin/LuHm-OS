#!/usr/bin/env python3
"""LuHm-OS machine-layer: local seeded SQLite, authenticated TX/RX packets, no network."""
from __future__ import annotations
import argparse
import hashlib
import hmac
import json
import os
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "doctrine/machineLayerReconciliation20261114V1.json"
SQL = ROOT / "host/api/typedLanesV1.sql"
CANON_GRID = ROOT / "doctrine/machineCanonFourLoopV1.json"
SHA40 = re.compile(r"^[0-9a-f]{40}$")
MAX_PACKET_BYTES = 131072

class MachineLayerError(ValueError):
    pass

def require(condition, reason):
    if not condition:
        raise MachineLayerError(reason)

def canonical(data):
    return json.dumps(data, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")

def loadManifest(path=MANIFEST):
    raw = Path(path).read_bytes()
    require(len(raw) <= MAX_PACKET_BYTES, "snapshot oversized")
    data = json.loads(raw)
    require(data.get("schema") == "luhmOs.machineLayerReconciliation.v1", "snapshot schema")
    require(data.get("product") == "LuHm-OS", "product identity")
    require(data.get("promotion") is False and data.get("crownStatus") == "STOP", "Crown gate")
    require(data.get("identity", {}).get("agentWorkerExecution") == "QUARANTINED", "agent quarantine")
    sourceRef = data.get("baselineSourceRef")
    require(isinstance(sourceRef, str) and SHA40.fullmatch(sourceRef), "exact source ref")
    levels = data.get("escalation", {}).get("levels", [])
    lanes = data.get("escalation", {}).get("lanes", [])
    cells = data.get("escalation", {}).get("cells", [])
    require(len(levels) == 4 and len(lanes) == 4 and len(cells) == 16, "must be 4x4")
    canon = json.loads(CANON_GRID.read_text(encoding="utf-8"))
    require(canon.get("schema") == "luhmOs.machineCanonFourLoop.v1", "canonical machine grid unavailable")
    require(canon.get("status") == "DRAFT_SOURCE_CHECKLIST_ONLY", "unexpected machine-grid authority")
    require([x.get("id") for x in levels] == canon.get("fourBeats"), "machine audit beats drift")
    require([x.get("id") for x in lanes] == canon.get("lanes"), "machine audit lanes drift")
    require(data.get("canonicalMachineMatrix", {}).get("source") == "doctrine/machineCanonFourLoopV1.json", "machine audit source missing")
    require(data.get("canonicalMachineMatrix", {}).get("sqlProjectionOnly") is True, "SQL projection may not become authority")
    require(all(x.get("allowedAuthority") in ("READ_ONLY", "SOURCE_REVIEW_ONLY") for x in cells), "SQL machine matrix cannot grant authority")
    require(len({x["cellId"] for x in cells}) == 16, "duplicate 4x4 identity")
    require(len({(x["tier"], x["laneId"]) for x in cells}) == 16, "duplicate 4x4 coordinate")
    require({x["tier"] for x in cells} == {0, 1, 2, 3}, "tier gap")
    require({x["laneId"] for x in cells} == {x["id"] for x in lanes}, "lane gap")
    require(all(x["state"] != "FULL_GREEN" for x in cells), "unproved green")
    require(data["database"]["remoteState"] == "BLOCKED_WORKSPACE_UNSELECTED", "remote proof not verified")
    return data

def openLocalDb(path):
    require(path == ":memory:" or (Path(path).suffix in (".db", ".sqlite") and not Path(path).is_symlink()), "unsafe database path")
    if path != ":memory:":
        require(Path(path).parent.is_dir(), "explicit existing local directory required")
    db = sqlite3.connect(path, timeout=5.0)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    db.execute("PRAGMA busy_timeout=5000")
    db.executescript(SQL.read_text(encoding="utf-8"))
    return db

def eventsFor(data):
    rows = []
    sourceRef = data["baselineSourceRef"]
    lanes = [x["id"] for x in data["escalation"]["lanes"]]
    cells = sorted(data["escalation"]["cells"], key=lambda x:(x["tier"], lanes.index(x["laneId"])))
    for index, item in enumerate(cells):
        require(item["tier"] in range(4) and item["laneId"] in lanes, "invalid coordinate")
        rows.append({
            "eventId": "machineCellT%dL%d" % (item["tier"], lanes.index(item["laneId"])),
            "taskId": "machineCanonRecon",
            "sourceRef": sourceRef,
            "scopeId": "machineLayer",
            "workerId": "lum",
            "sequenceId": 1000000 + index,
            "eighthNote": item["tier"] * 2 + 1,
            "texts": {"cellId": item["cellId"], "laneId": item["laneId"], "machineState": item["state"], "authorityGate": item["allowedAuthority"]},
            "booleans": {"remoteVerified": None, "firmwareFlashed": False, "productionPromoted": False}
        })
    return rows

def _store(db, event, observedAt):
    found = db.execute("SELECT eventId,sourceRef,taskId,scopeId,workerId,sequenceId,eighthNote FROM streamEvent WHERE eventId=?", (event["eventId"],)).fetchone()
    if found is not None:
        require(all(found[k] == event[k] for k in ("eventId", "sourceRef", "taskId", "scopeId", "workerId", "sequenceId", "eighthNote")), "conflicting immutable event")
        for key, value in event["texts"].items():
            existing = db.execute("SELECT textValue FROM textStream WHERE eventId=? AND fieldName=?", (event["eventId"], key)).fetchone()
            require(existing is not None and existing[0] == value, "conflicting text receipt")
        for key, value in event["booleans"].items():
            existing = db.execute("SELECT booleanValue FROM booleanStream WHERE eventId=? AND fieldName=?", (event["eventId"], key)).fetchone()
            require(existing is not None and existing[0] == (None if value is None else int(value)), "conflicting boolean receipt")
        return False
    db.execute("INSERT INTO streamEvent(eventId,taskId,sourceRef,scopeId,workerId,sequenceId,eighthNote,observedAt,evidenceRef) VALUES(?,?,?,?,?,?,?,?,?)",
               (event["eventId"], event["taskId"], event["sourceRef"], event["scopeId"], event["workerId"], event["sequenceId"], event["eighthNote"], observedAt, "machineLayerSourceSnapshot"))
    for key, value in event["texts"].items():
        db.execute("INSERT INTO textStream(eventId,fieldName,textValue) VALUES(?,?,?)", (event["eventId"], key, value))
    for key, value in event["booleans"].items():
        db.execute("INSERT INTO booleanStream(eventId,fieldName,booleanValue) VALUES(?,?,?)", (event["eventId"], key, None if value is None else int(value)))
    return True

def seed(db, data):
    now = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    inserted = 0
    with db:
        for event in eventsFor(data):
            inserted += int(_store(db, event, now))
    return {"status": "LOCAL_ONLY", "inserted": inserted, "verified": 16, "remoteConnection": False, "crown": "STOP"}

def _sharedKey():
    key = os.environ.get("LUHM_SQL_SYNC_KEY", "")
    require(len(key) >= 32 and len(key) <= 512, "32+ character environment-only sync key required")
    return key.encode("utf-8")

def makePacket(db, data):
    expected = eventsFor(data)
    for e in expected:
        row = db.execute("SELECT sourceRef FROM streamEvent WHERE eventId=?", (e["eventId"],)).fetchone()
        require(row is not None and row["sourceRef"] == e["sourceRef"], "source row not seeded or conflicts")
    body = {"schema":"luhmOs.machineSqlTxRx.v1","product":"LuHm-OS","sourceRef":data["baselineSourceRef"],"scopeId":"machineLayer",
            "authority":{"mutation":False,"green":False,"crown":False},"events":expected}
    content = canonical(body)
    require(len(content) < MAX_PACKET_BYTES, "packet oversized")
    mac = hmac.new(_sharedKey(), content, hashlib.sha256).hexdigest()
    return {"body":body,"hmacSha256":mac}

def receivePacket(db, data, packet):
    require(type(packet) is dict and set(packet) == {"body", "hmacSha256"}, "packet envelope")
    body = packet["body"]
    require(type(body) is dict and body.get("schema") == "luhmOs.machineSqlTxRx.v1", "packet schema")
    require(body.get("product") == "LuHm-OS" and body.get("sourceRef") == data["baselineSourceRef"] and body.get("scopeId") == "machineLayer", "packet identity")
    require(body.get("authority") == {"mutation":False,"green":False,"crown":False}, "packet cannot grant authority")
    expected = eventsFor(data)
    require(body.get("events") == expected, "packet does not match source snapshot")
    digest = hmac.new(_sharedKey(), canonical(body), hashlib.sha256).hexdigest()
    require(isinstance(packet["hmacSha256"], str) and hmac.compare_digest(digest, packet["hmacSha256"]), "authentication failed")
    now = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    inserted = 0
    with db:
        for event in expected:
            inserted += int(_store(db, event, now))
    return {"status": "RECEIVED_LOCAL", "inserted": inserted, "verified": len(expected), "remoteConnection": False, "crown": "STOP"}

def count(db, data):
    ids = [e["eventId"] for e in eventsFor(data)]
    placeholders = ",".join("?" for _ in ids)
    result = db.execute("SELECT count(*) FROM streamEvent WHERE eventId IN ("+placeholders+") AND sourceRef=?", [*ids,data["baselineSourceRef"]]).fetchone()[0]
    return {"status":"LOCAL_ONLY","present":result,"expected":len(ids),"remoteConnection":False,"crown":"STOP"}

def _sha256_file(path):
    h=hashlib.sha256()
    with open(path, "rb") as source:
        for block in iter(lambda: source.read(1024*1024), b""):
            h.update(block)
    return h.hexdigest()

def verifyBackup(snapshotPath, data, expectedDigest):
    path=Path(snapshotPath)
    require(path.is_file() and not path.is_symlink() and path.suffix in (".db",".sqlite"), "snapshot must be existing local SQLite file")
    require(isinstance(expectedDigest,str) and re.fullmatch(r"[0-9a-f]{64}",expectedDigest), "exact backup digest required")
    actual=_sha256_file(path)
    require(hmac.compare_digest(actual,expectedDigest), "snapshot digest mismatch")
    # SQLite read-only URI: never create an absent file or run DDL during restoration checks.
    readonly=path.resolve().as_uri()+"?mode=ro"
    with sqlite3.connect(readonly,uri=True,timeout=3.0) as check:
        check.row_factory=sqlite3.Row
        require(check.execute("PRAGMA integrity_check").fetchone()[0] == "ok", "SQLite integrity check failed")
        require(len(check.execute("PRAGMA foreign_key_check").fetchall()) == 0, "SQLite foreign key check failed")
        expected=eventsFor(data)
        for event in expected:
            columns=("eventId","taskId","sourceRef","scopeId","workerId","sequenceId","eighthNote")
            row=check.execute("SELECT eventId,taskId,sourceRef,scopeId,workerId,sequenceId,eighthNote FROM streamEvent WHERE eventId=?", (event["eventId"],)).fetchone()
            require(row is not None and all(row[k]==event[k] for k in columns), "backup event identity mismatch")
            for field,value in event["texts"].items():
                found=check.execute("SELECT textValue FROM textStream WHERE eventId=? AND fieldName=?", (event["eventId"],field)).fetchone()
                require(found is not None and found[0]==value, "backup text mismatch")
            for field,value in event["booleans"].items():
                found=check.execute("SELECT booleanValue FROM booleanStream WHERE eventId=? AND fieldName=?", (event["eventId"],field)).fetchone()
                require(found is not None and found[0]==(None if value is None else int(value)), "backup boolean mismatch")
    return {"status":"LOCAL_BACKUP_VERIFIED","sha256":actual,"verifiedRows":len(expected),"productionRestorePerformed":False,"remoteConnection":False,"crown":"STOP"}

def backupSnapshot(db, snapshotPath, data):
    path=Path(snapshotPath)
    require(path.suffix in (".db",".sqlite") and path.parent.is_dir() and not path.parent.is_symlink(), "existing local backup directory required")
    require(not path.exists() and not path.is_symlink(), "never overwrite or follow a snapshot")
    # Exclusive and private file creation: a snapshot does not replace live Canon.
    descriptor=os.open(str(path),os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    os.close(descriptor)
    try:
        destination=sqlite3.connect(str(path),timeout=5.0)
        try:
            db.backup(destination)
        finally:
            destination.close()
        result=verifyBackup(path,data,_sha256_file(path))
        return {"status":"LOCAL_BACKUP_CREATED","sha256":result["sha256"],"verifiedRows":result["verifiedRows"],"productionRestorePerformed":False,"remoteConnection":False,"crown":"STOP"}
    except Exception:
        path.unlink(missing_ok=True)
        raise

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command",choices=["validate","seed","status","tx","rx","backup","verifyBackup"])
    parser.add_argument("--db",default=":memory:")
    parser.add_argument("--input")
    parser.add_argument("--output")
    parser.add_argument("--digest")
    args=parser.parse_args(argv)
    try:
        data=loadManifest()
        if args.command=="validate":
            result={"status":"SNAPSHOT_VALID","cells":16,"sourceRef":data["baselineSourceRef"],"remoteConnection":False,"crown":"STOP"}
        elif args.command=="verifyBackup":
            require(bool(args.input) and bool(args.digest), "--input and --digest required")
            result=verifyBackup(args.input,data,args.digest)
        else:
            with openLocalDb(args.db) as db:
                if args.command=="seed": result=seed(db,data)
                elif args.command=="backup":
                    require(args.db != ":memory:" and bool(args.output), "file-backed database and --output required")
                    result=backupSnapshot(db,args.output,data)
                elif args.command=="status":result=count(db,data)
                elif args.command=="tx":
                    require(bool(args.output),"--output required")
                    path=Path(args.output)
                    require(not path.exists() and path.suffix==".json","output must be new JSON")
                    packet=makePacket(db,data)
                    path.write_bytes(canonical(packet)+b"\n")
                    result={"status":"TX_PACKET_CREATED","bytes":path.stat().st_size,"remoteConnection":False,"crown":"STOP"}
                else:
                    require(bool(args.input),"--input required")
                    path=Path(args.input)
                    require(path.is_file() and path.stat().st_size <= MAX_PACKET_BYTES,"input missing or oversized")
                    packet=json.loads(path.read_text(encoding="utf-8"))
                    result=receivePacket(db,data,packet)
        print(json.dumps(result,sort_keys=True))
        return 0
    except (MachineLayerError,ValueError,OSError,sqlite3.Error,KeyError,TypeError) as exc:
        print(json.dumps({"status":"BLOCKED","reason":str(exc),"remoteConnection":False}))
        return 1

if __name__=="__main__":
    raise SystemExit(main())

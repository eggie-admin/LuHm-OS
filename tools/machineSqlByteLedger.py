#!/usr/bin/env python3
"""Local-only SQLite machine evidence index. No binary storage or release authority."""
import argparse
import hashlib
import json
import re
import sqlite3
from pathlib import Path

HEX40 = re.compile(r"^[a-f0-9]{40}$")
STATUS = {"GREEN", "AMBER", "RED", "BLOCKED"}
LANES = {"testing", "proposed"}

def ingest(db, record):
    sha = record["sourceRef"]
    if not HEX40.fullmatch(sha):
        raise ValueError("invalid exact source SHA")
    lane, status = record["lane"], record["status"]
    if lane not in LANES or status not in STATUS:
        raise ValueError("invalid lane/status")
    task = record["taskId"]
    if not isinstance(task, str) or not re.fullmatch(r"[A-Za-z0-9_.-]{1,100}", task):
        raise ValueError("invalid task")
    blob = record.get("artifactPath")
    digest = None
    size = None
    if blob:
        p = Path(blob)
        if not p.is_file():
            raise ValueError("artifact must exist locally")
        size = p.stat().st_size
        h = hashlib.sha256()
        with p.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                h.update(chunk)
        digest = h.hexdigest()
    with db:
        db.execute("""INSERT OR REPLACE INTO milestone(taskId,sourceRef,lane,status,
                  artifactRef,artifactSha256,sizeBytes) VALUES(?,?,?,?,?,?,?)""",
                  (task,sha,lane,status,blob,digest,size))

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--db", required=True)
    p.add_argument("--input", required=True)
    args = p.parse_args()
    db = sqlite3.connect(args.db)
    db.executescript("""CREATE TABLE IF NOT EXISTS milestone(
      taskId TEXT NOT NULL, sourceRef TEXT NOT NULL, lane TEXT NOT NULL,
      status TEXT NOT NULL, artifactRef TEXT, artifactSha256 TEXT,
      sizeBytes INTEGER, PRIMARY KEY(taskId, sourceRef, lane));
      CREATE INDEX IF NOT EXISTS milestone_lane_status
      ON milestone(lane,status,sourceRef);""")
    ingest(db, json.loads(Path(args.input).read_text(encoding="utf8")))
    result = [dict(zip(("taskId","lane","status","artifactSha256","sizeBytes"),row))
              for row in db.execute("""SELECT taskId,lane,status,artifactSha256,sizeBytes
                                      FROM milestone ORDER BY lane,taskId""")]
    print(json.dumps({"milestones":result,"releaseAuthorized":False},indent=2))

if __name__ == "__main__":
    main()

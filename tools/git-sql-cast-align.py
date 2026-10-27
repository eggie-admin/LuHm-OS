#!/usr/bin/env python3
"""Offline Git to existing SQLite JSON1 + typed-lane alignment for CAST.

--check (default) uses memory only; --write saves only under repository build/.
This does not call Google APIs, migrate production SQL, deploy or grant CROWN.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
SHA = re.compile(r"[0-9a-f]{40}\Z")
LANES = ("app", "plugin")
PROOF = "doctrine/crown-single-proof-v1.json"
TEMPLATE = "doctrine/aiTaskManifestV2.template.json"
SQL_PROOF = "infrastructure/google-cloud-vm/one-proof.sql"
SQL_TYPED = "host/api/typedLanesV1.sql"


def canonical(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def load(root: Path, path: str) -> dict:
    value = json.loads((root / path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("RED_NONOBJECT_CONTRACT")
    return value


def git_head(root: Path) -> str:
    def git(*args: str) -> str:
        return subprocess.check_output(["git", "-C", str(root), *args],
                                       text=True, stderr=subprocess.DEVNULL).strip()
    head = git("rev-parse", "--verify", "HEAD")
    if not SHA.fullmatch(head):
        raise ValueError("RED_GIT_HEAD")
    if git("status", "--porcelain", "--untracked-files=no"):
        raise ValueError("RED_TRACKED_WORKTREE_DIRTY")
    return head


def packet_for(root: Path, head: str, lane: str) -> dict:
    if lane not in LANES or not SHA.fullmatch(head):
        raise ValueError("RED_LANE_OR_GIT_HEAD")
    contract = load(root, TEMPLATE)
    if contract.get("schema") != "luhmOs.aiTaskManifest.v2":
        raise ValueError("RED_MANIFEST_TEMPLATE")
    expected_stops = ["scopeComplete", "evidenceConflict", "sourceMismatch", "budgetExhausted"]
    if contract.get("stopConditions") != expected_stops:
        raise ValueError("RED_STOP_CONTRACT_DRIFT")
    return {
        "schema": contract["schema"], "providerId": "googleAi",
        "capabilityId": "candidateReview",
        "taskId": "castSqlCandidateReview",
        "sourceRef": head, "scopeId": "finalProposed" + lane.capitalize(),
        "inputRefs": [f"github:eggie-admin/LuHm-OS@{head}:{PROOF}"],
        "requiredOutputSchema": "luhmOs.providerExecutionReceipt.v1",
        "budget": {"maxRequests": 1, "maxParallel": 1, "maxPasses": 1},
        "stopConditions": expected_stops,
        "authority": {"mutation": False, "green": False, "crown": False},
    }


def checked_proof(root: Path, head: str) -> dict:
    source = load(root, PROOF)
    if (source.get("schema") != "luhmOs.crownSingleProof.v1"
            or source.get("sourceAuthority") != "eggie-admin/LuHm-OS"
            or not SHA.fullmatch(source.get("sourceRef", ""))
            or source.get("gate", {}).get("crown") != "STOP"
            or source.get("evidence", {}).get("site", {}).get("cacheBridgeGreen") is not False
            or len(source.get("tiers", [])) != 4):
        raise ValueError("RED_CROWN_PROOF_CONTRACT")
    proof = copy.deepcopy(source)
    original = proof["sourceRef"]
    proof["proofId"] += "-" + head[:12]
    proof["sourceRef"] = head
    proof["gitSqlAlignment"] = {
        "gitHead": head, "historicalAnchorRef": original,
        "sqlDialect": "SQLite JSON1 STRICT LOCAL_ONLY",
        "tracks": list(LANES),
        "state": "FINAL_PROPOSED_SOURCE_ONLY",
        "googleCloudShellExecuted": False, "googleProviderCalled": False,
        "publicRelease": False, "crown": "STOP",
    }
    return proof


def init_schema(db: sqlite3.Connection, root: Path) -> None:
    db.execute("PRAGMA foreign_keys = ON")
    db.executescript((root / SQL_PROOF).read_text(encoding="utf-8"))
    db.executescript((root / SQL_TYPED).read_text(encoding="utf-8"))
    if db.execute("PRAGMA foreign_keys").fetchone()[0] != 1:
        raise ValueError("RED_SQL_FOREIGN_KEYS")


def align(db: sqlite3.Connection, root: Path, head: str) -> dict:
    """Immutable-by-head, idempotent and atomic two-product SQL alignment."""
    proof = checked_proof(root, head)
    packets = {lane: packet_for(root, head, lane) for lane in LANES}
    payload = canonical(proof)
    db.execute("BEGIN IMMEDIATE")
    try:
        prior = db.execute("SELECT envelopeJson FROM crownProof WHERE proofId=?",
                           (proof["proofId"],)).fetchone()
        if prior and prior[0] != payload:
            raise ValueError("RED_SAME_PROOF_ID_DIFFERENT_BYTES")
        if not prior:
            db.execute("""INSERT INTO crownProof(proofId,taskId,scopeId,sourceRef,envelopeJson)
                          VALUES(?,?,?,?,?)""",
                       (proof["proofId"], proof["taskId"], proof["scopeId"], head, payload))
        for idx, (lane, manifest) in enumerate(packets.items()):
            eid = f"git-sql-{lane}-{head[:20]}"
            text = canonical(manifest)
            old = db.execute("SELECT sourceRef,taskId,scopeId FROM streamEvent WHERE eventId=?",
                             (eid,)).fetchone()
            identity = (head, manifest["taskId"], manifest["scopeId"])
            if old and old != identity:
                raise ValueError("RED_TYPED_EVENT_IDENTITY_CONFLICT")
            found = db.execute("SELECT manifestJson FROM aiManifestStream WHERE eventId=?",
                               (eid,)).fetchone()
            if found and found[0] != text:
                raise ValueError("RED_TYPED_MANIFEST_DIFFERENT_BYTES")
            if not old:
                db.execute("""INSERT INTO streamEvent
                              (eventId,taskId,sourceRef,scopeId,workerId,sequenceId,
                               eighthNote,observedAt,evidenceRef)
                              VALUES(?,?,?,?,?,?,?,?,?)""",
                           (eid, manifest["taskId"], head, manifest["scopeId"],
                            "gitSqlCastAlignment", int(head[:15], 16)*2+idx, idx+1,
                            datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                            "GIT_HEAD_SOURCE_ONLY"))
            if not found:
                db.execute("""INSERT INTO aiManifestStream
                              (eventId,manifestJson,manifestSchema,providerId,
                               capabilityId,mutationAuthority,greenAuthority,crownAuthority)
                              VALUES(?,?,?,?,?,0,0,0)""",
                           (eid, text, manifest["schema"], manifest["providerId"],
                            manifest["capabilityId"]))
        db.commit()
    except Exception:
        db.rollback()
        raise
    count = db.execute("""SELECT JSON_ARRAY_LENGTH(JSON_EXTRACT(envelopeJson,'$.tiers'))
                          FROM crownProof WHERE proofId=?""",
                       (proof["proofId"],)).fetchone()[0]
    rows = db.execute("""SELECT s.scopeId,s.sourceRef,m.providerId,
                        JSON_EXTRACT(m.manifestJson,'$.authority.crown'),m.crownAuthority
                        FROM streamEvent s JOIN aiManifestStream m USING(eventId)
                        WHERE s.sourceRef=? AND s.workerId=? ORDER BY s.scopeId""",
                      (head, "gitSqlCastAlignment")).fetchall()
    if (count != 4 or len(rows) != 2 or
        any(r[1] != head or r[2] != "googleAi" or r[3] != 0 or r[4] != 0 for r in rows)):
        raise RuntimeError("RED_SQL_ALIGNMENT_RECHECK")
    return {
        "schema": "luhmOs.gitSqlAlignmentReceipt.v1",
        "gitHead": head, "proofId": proof["proofId"],
        "proofSha256": hashlib.sha256(payload.encode("utf-8")).hexdigest(),
        "sqlEngine": "SQLite JSON1 STRICT", "typedPacketCount": len(rows),
        "companyTierCount": count, "appAndPluginScopes": [row[0] for row in rows],
        "providerCalled": False, "siteDeployed": False, "gcpVmCreated": False,
        "sourceState": "SOURCE_ALIGNED_LOCAL_ONLY", "crown": "STOP",
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--check", action="store_true", help="In-memory preview, default")
    p.add_argument("--write", action="store_true", help="Persist to build/ SQLite only")
    p.add_argument("--db", help="SQLite filename strictly inside build/, requires --write")
    args = p.parse_args()
    if args.check and args.write:
        p.error("choose one mode")
    if args.db and not args.write:
        p.error("--db requires --write")
    try:
        root = ROOT.resolve()
        head = git_head(root)
        if args.write:
            path = (root / (args.db or "build/git-sql-cast/crown-proposed.sqlite3")).resolve()
            if not path.is_relative_to(root / "build") or path.suffix != ".sqlite3":
                raise ValueError("RED_SQL_TARGET_MUST_BE_BUILD_DIRECTORY")
            path.parent.mkdir(parents=True, exist_ok=True)
            db = sqlite3.connect(str(path))
        else:
            db = sqlite3.connect(":memory:")
        try:
            init_schema(db, root)
            result = align(db, root, head)
            result["mode"] = "LOCAL_BUILD_SQLITE" if args.write else "MEMORY_ONLY"
            print(json.dumps(result, sort_keys=True, indent=2))
        finally:
            db.close()
        return 0
    except (OSError, subprocess.CalledProcessError, ValueError,
            RuntimeError, sqlite3.Error) as err:
        print("RED_GIT_SQL_ALIGN: " + str(err), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

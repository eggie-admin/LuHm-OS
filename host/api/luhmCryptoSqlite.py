#!/usr/bin/env python3
"""Private local SQLite projection for R1-R4 candidate receipts.

Reuses LuHm's existing four-lane STRICT schema and typedSqlStub. Never stores
original content, secrets, AES-GCM ciphertext, or private media. Does not
connect to a remote DB or create files unless an approved private host passes
its own SQLite path.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
TYPED_PATH = ROOT / "tools" / "typedSqlStub.py"
DIGEST_64 = re.compile(r"^[0-9a-f]{64}$")
DIGEST_128 = re.compile(r"^[0-9a-f]{128}$")
SHA = re.compile(r"^[0-9a-f]{40}$")


def _stub() -> Any:
    spec = importlib.util.spec_from_file_location("typedSqlStub", TYPED_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("RED_SQL_CANON_NOT_FOUND")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _receipt(receipt: dict[str, Any]) -> None:
    if not isinstance(receipt, dict) or receipt.get("schema") != "luhmOs.cryptoBreathingReceipt.v1":
        raise ValueError("not a crypto breathing receipt")
    stub = _stub()
    for k in ("taskId", "scopeId", "artifactId"):
        stub.boundedName(receipt.get(k))
    if not isinstance(receipt.get("sourceRef"), str) or not SHA.fullmatch(receipt["sourceRef"]):
        raise ValueError("exact source required")
    for k, exp in (("sha256", DIGEST_64), ("sha512", DIGEST_128), ("sha3_256", DIGEST_64)):
        if not isinstance(receipt.get(k), str) or not exp.fullmatch(receipt[k]):
            raise ValueError("invalid digest")
    stages = receipt.get("stages")
    if not isinstance(stages, list) or not 1 <= len(stages) <= 4:
        raise ValueError("invalid stage count")
    if [s.get("stage") for s in stages] != ["R1","R2","R3","R4"][:len(stages)]:
        raise ValueError("invalid stage order")
    if receipt.get("greenAuthority") is not False or receipt.get("crownAuthority") is not False:
        raise ValueError("forbidden promoted receipt")
    if receipt.get("state") not in ("HOLD","STOP","HOLD_FOR_PROFESSOR"):
        raise ValueError("no GREEN receipts")


class CryptoSqliteLedger:
    def __init__(self, path: str = ":memory:") -> None:
        if type(path) is not str or not path or path.startswith("file:"):
            raise ValueError("SQLite URI forbidden")
        self._lock = threading.RLock()
        self._db: sqlite3.Connection = _stub().openStub(path)

    def close(self) -> None:
        with self._lock:
            self._db.close()

    def record(self, receipt: dict[str, Any]) -> dict[str, Any]:
        _receipt(receipt)
        task, source, scope = (receipt[x] for x in ("taskId","sourceRef","scopeId"))
        raw = "|".join((task,source,scope,receipt["artifactId"])).encode("utf-8")
        event_id = "evt" + hashlib.sha256(raw).hexdigest()[:32]
        stub = _stub()
        with self._lock:
            self._db.execute("BEGIN IMMEDIATE")
            try:
                row = self._db.execute(
                    "SELECT textValue FROM textStream WHERE eventId=? AND fieldName='sha256Hex'",
                    (event_id,)
                ).fetchone()
                if row is not None:
                    if row["textValue"] != receipt["sha256"]:
                        raise ValueError("RED_CRYPTO_REPLAY_DIGEST_CONFLICT")
                    self._db.commit()
                    return {"eventId":event_id,"state":"IDEMPOTENT_REPLAY",
                            "remoteDb":False,"greenAuthority":False}
                seq = int(self._db.execute(
                    "SELECT COALESCE(MAX(sequenceId),0)+1 FROM streamEvent"
                ).fetchone()[0])
                stub.addEvent(
                    self._db,event_id,task,source,scope,"urdDoctorGoddess",seq,
                    min(len(receipt["stages"])*2,8),
                    datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                )
                for key, col in (("sha256","sha256Hex"),("sha512","sha512Hex"),
                                 ("sha3_256","sha3Digest")):
                    stub.putText(self._db,event_id,col,receipt[key])
                stub.putText(self._db,event_id,"stageState",receipt["state"])
                stub.putText(self._db,event_id,"artifactId",receipt["artifactId"])
                stub.putNumeric(self._db,event_id,"stageCount","integer",len(receipt["stages"]))
                stub.putBoolean(self._db,event_id,"sourceVerified",None)
                stub.putBoolean(self._db,event_id,"projectGreen",False)
                stub.putManifest(self._db,event_id,{
                    "schema":"luhmOs.aiTaskManifest.v2",
                    "taskId":task,"sourceRef":source,"scopeId":scope,
                    "providerId":"deterministicLocal","capabilityId":"cryptoReceipt",
                    "inputRefs":[receipt["sha256"]],
                    "requiredOutputSchema":"luhmOs.cryptoBreathingReceipt.v1",
                    "budget":{"maxRequests":0,"maxParallel":0,"maxPasses":4},
                    "stopConditions":["sourceMismatch","missingProof","professorApprovalRequired"],
                    "authority":{"mutation":False,"green":False,"crown":False},
                })
                self._db.commit()
            except Exception:
                self._db.rollback()
                raise
        return {"eventId":event_id,"state":"RECORDED_LOCAL_CANDIDATE",
                "remoteDb":False,"storedRawBytes":False,
                "greenAuthority":False,"crownAuthority":False}

    def events(self, task_id: str, source_ref: str, scope_id: str, limit: int = 20) -> list[dict[str, Any]]:
        for val in (task_id,scope_id):
            _stub().boundedName(val)
        if not isinstance(source_ref,str) or not SHA.fullmatch(source_ref):
            raise ValueError("exact source required")
        with self._lock:
            return _stub().orderedEvents(self._db,task_id,source_ref,scope_id,limit)

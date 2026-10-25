#!/usr/bin/env python3
"""Real parameterized SQLite JSON1 tuning for candidate Project Premonition system variables.

Preview uses an in-memory DB. Apply persists only to a dedicated local candidate
database, never to doctrine, MariaDB, a connected app, or a release backend.
"""
from __future__ import annotations

import hashlib
import json
import math
import sqlite3
from pathlib import Path
from typing import Any

root = Path(__file__).resolve().parents[1]
defaultDbPath = root / "build/fnCastTuning/systemVariables.sqlite3"


def parseJsonAssignments(assignments: list[str]) -> dict[str, Any]:
    updates: dict[str, Any] = {}
    for assignment in assignments:
        if "=" not in assignment:
            raise ValueError("Tuning assignment requires allowedPath=JSONvalue")
        path, rawValue = assignment.split("=", 1)
        if path in updates:
            raise ValueError("Duplicate tuning path: " + path)
        try:
            updates[path] = json.loads(rawValue, parse_constant=lambda _: (_ for _ in ()).throw(ValueError("Nonfinite value")))
        except json.JSONDecodeError as error:
            raise ValueError("Invalid JSON value for " + path) from error
    return updates


def validateUpdates(updates: dict[str, Any], config: dict) -> None:
    if not isinstance(updates, dict) or not updates:
        raise ValueError("Tuning requires at least one system-variable update")
    rules = config["allowedPaths"]
    for path, value in updates.items():
        if path not in rules:
            raise ValueError("Variable not on allowlist: " + str(path))
        rule = rules[path]
        if isinstance(value, bool) or value is None:
            raise ValueError("Null and booleans are invalid for tuning: " + path)
        if rule["type"] == "integer":
            if not isinstance(value, int):
                raise ValueError("Expected integer: " + path)
        elif rule["type"] == "number":
            if not isinstance(value, (int, float)):
                raise ValueError("Expected numeric JSON value: " + path)
        else:
            raise ValueError("Unsupported tuning type: " + path)
        if not math.isfinite(value) or not rule["minimum"] <= value <= rule["maximum"]:
            raise ValueError("Variable outside allowed numeric range: " + path)


def stableJson(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False)


def tuneSqlJson(
    updates: dict[str, Any],
    contract: dict,
    *,
    apply: bool = False,
    authorized: bool = False,
    dbPath: Path | None = None,
) -> dict:
    """Apply actual SQL json_set, json_extract, json_valid in one transaction."""
    config = contract["sqlJsonTuning"]
    validateUpdates(updates, config)
    if apply and not authorized:
        raise PermissionError("SQLite apply requires explicitly armed fnCast voice intent")
    target = Path(dbPath) if dbPath is not None else defaultDbPath
    # A production database is never an implicit target of the voice command.
    # Test callers can supply their own isolated tempfile under a test fixture.
    if apply and dbPath is None:
        target.parent.mkdir(parents=True, exist_ok=True)

    if apply:
        connection = sqlite3.connect(str(target), timeout=5)
    else:
        connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    try:
        if connection.execute("SELECT json_valid(?)", ('{"test":true}',)).fetchone()[0] != 1:
            raise RuntimeError("SQLite JSON1 unavailable")
        connection.execute("""
            CREATE TABLE IF NOT EXISTS systemVariables (
              recordName TEXT PRIMARY KEY,
              stateJson TEXT NOT NULL CHECK (json_valid(stateJson)),
              revision INTEGER NOT NULL CHECK (revision >= 0)
            )
        """)
        recordName = config["recordName"]
        existing = connection.execute(
            "SELECT stateJson, revision FROM systemVariables WHERE recordName = ?",
            (recordName,),
        ).fetchone()
        if existing is None:
            defaultState = {
                "schema": config["schema"],
                "project": contract["project"],
                "systemVariables": config["defaultVariables"],
            }
            connection.execute(
                "INSERT INTO systemVariables(recordName, stateJson, revision) VALUES(?,?,0)",
                (recordName, stableJson(defaultState)),
            )
            before = defaultState
            previousRevision = 0
        else:
            before = json.loads(existing["stateJson"])
            previousRevision = int(existing["revision"])
        if before.get("schema") != config["schema"] or before.get("project") != contract["project"]:
            raise ValueError("Candidate database schema/project does not match current contract")
        beforeSha = hashlib.sha256(stableJson(before).encode("utf-8")).hexdigest()

        for path, value in sorted(updates.items()):
            sqlPath = "$.systemVariables." + path
            jsonValue = stableJson(value)
            connection.execute(
                """UPDATE systemVariables
                   SET stateJson = json_set(stateJson, ?, json(?)),
                       revision = revision + 1
                   WHERE recordName = ?""",
                (sqlPath, jsonValue, recordName),
            )
            observed = connection.execute(
                "SELECT json_extract(stateJson, ?) AS tunedValue FROM systemVariables WHERE recordName = ?",
                (sqlPath, recordName),
            ).fetchone()["tunedValue"]
            if observed != value:
                raise RuntimeError("SQLite json_extract failed to confirm tuned value: " + path)
        row = connection.execute(
            "SELECT stateJson, revision, json_valid(stateJson) AS validJson "
            "FROM systemVariables WHERE recordName = ?",
            (recordName,),
        ).fetchone()
        if row["validJson"] != 1:
            raise RuntimeError("SQL returned invalid JSON after tuning")
        after = json.loads(row["stateJson"])
        afterSha = hashlib.sha256(stableJson(after).encode("utf-8")).hexdigest()
        # Prevent insertion of authority fields via the tuning surface.
        if sorted(after.keys()) != ["project", "schema", "systemVariables"]:
            raise RuntimeError("Unexpected JSON root keys")
        if apply:
            connection.commit()
        else:
            connection.rollback()
        return {
            "schema": "luhmOs.fnCastSqlJsonReceipt.v1",
            "engine": "SQLite JSON1",
            "sqlOperations": ["json_valid", "json_set", "json_extract"],
            "mode": "APPLIED_LOCAL_CANDIDATE" if apply else "PREVIEW_ONLY",
            "recordName": recordName,
            "revisionBefore": previousRevision,
            "revisionAfter": int(row["revision"]),
            "beforeSha256": beforeSha,
            "afterSha256": afterSha,
            "tunedPaths": sorted(updates.keys()),
            "tunedDocument": after,
            "persistentDatabase": str(target.relative_to(root)) if apply and dbPath is None else None,
            "canonicalDoctrineMutated": False,
            "externalDatabaseMutated": False,
            "releaseAuthority": False,
            "crownAuthority": False,
        }
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

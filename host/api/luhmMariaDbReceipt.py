#!/usr/bin/env python3
"""Optional MariaDB receipt sink, OFF by default, with parameter-only SQL.

Does not open network connections, import a driver at module import,
create schemas, or elevate source/execution/Crown authority. Operator owns
authenticated TLS and database credentials in an approved private host.
"""
from __future__ import annotations

import re
from typing import Any, Mapping

ID = re.compile(r"^[a-z][A-Za-z0-9]{0,79}$")
SHA = re.compile(r"^[0-9a-f]{40}$")
DIGEST = re.compile(r"^[0-9a-f]{64}$")
# MariaDB Connector/Python supports qmark placeholders. No dynamic table names.
INSERT_SQL = (
    "INSERT INTO luhm_update_receipt "
    "(task_id,source_ref,scope_id,artifact_id,sha256_hex,local_state,stage_count) "
    "VALUES (?,?,?,?,?,?,?)"
)


def connection_plan(*, enabled: bool = False,
                    tls_host_identity_proven: bool = False,
                    private_network_proven: bool = False) -> dict[str, Any]:
    blockers = ["MARIADB_DISABLED"] if not enabled else []
    if not tls_host_identity_proven:
        blockers.append("TLS_HOST_IDENTITY_UNVERIFIED")
    if not private_network_proven:
        blockers.append("PRIVATE_NETWORK_UNVERIFIED")
    # This is a configuration evaluation, never a live server receipt.
    return {
        "schema": "luhmOs.mariaDbReceiptPlan.v1",
        "state": "PLAN_ONLY",
        "blockingConditions": blockers,
        "driver": "mariadbConnectorPython",
        "configurationNotConnectionProof": True,
        "connected": False,
        "networkCalls": 0,
        "writes": 0,
        "mutationAuthority": False,
        "greenAuthority": False,
        "crownAuthority": False,
    }


def _row(receipt: Mapping[str, Any]) -> tuple[str, str, str, str, str, str, int]:
    if not isinstance(receipt, Mapping):
        raise ValueError("receipt must be mapping")
    task = receipt.get("taskId")
    source = receipt.get("sourceRef")
    scope = receipt.get("scopeId")
    artifact = receipt.get("artifactId")
    digest = receipt.get("sha256")
    state = receipt.get("state")
    stages = receipt.get("stages")
    if not all(isinstance(v, str) and ID.fullmatch(v) for v in (task, scope, artifact)):
        raise ValueError("invalid task/scope/artifact identity")
    if not isinstance(source, str) or not SHA.fullmatch(source):
        raise ValueError("invalid source identity")
    if not isinstance(digest, str) or not DIGEST.fullmatch(digest):
        raise ValueError("invalid digest")
    if state not in ("HOLD", "STOP", "HOLD_FOR_PROFESSOR"):
        raise ValueError("receipt state may not claim GREEN")
    if not isinstance(stages, list) or not 1 <= len(stages) <= 4:
        raise ValueError("invalid bounded stage list")
    return (task, source, scope, artifact, digest, state, len(stages))


def store_verified_local_receipt(receipt: Mapping[str, Any], *, connection: Any,
                                 allow_private_write: bool = False) -> dict[str, Any]:
    """Intentionally not exported via MCP/FastAPI; private host only.

    Caller must inject an already authenticated, TLS-verified MariaDB connection.
    A valid DB insert proves a row was written, not authenticity of remote source.
    """
    row = _row(receipt)
    if allow_private_write is not True:
        raise PermissionError("MARIADB_WRITE_NOT_AUTHORIZED")
    if connection is None:
        raise ValueError("private host connection required")
    cursor = connection.cursor()
    try:
        cursor.execute(INSERT_SQL, row)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
    return {
        "schema": "luhmOs.mariaDbReceiptWrite.v1",
        "localWriteAttempted": True,
        "providerServerIdentityVerifiedByModule": False,
        "taskId": row[0],
        "sourceRef": row[1],
        "scopeId": row[2],
        "persistedSensitiveContent": False,
        "greenAuthority": False,
        "crownAuthority": False,
    }

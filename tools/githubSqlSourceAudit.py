#!/usr/bin/env python3
"""LuHm SQL source gate: Git blob lock + strict, ephemeral schema proof.

Runs only on checked-out GitHub source. Never connects to MariaDB or applies
schema to a live SQLite path. SQL files are versioned source, not database
state, large media storage, a production migration grant, or Crown evidence.
"""
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "doctrine" / "githubSqlSourceRegistryV1.json"
QUARANTINE = ROOT / "doctrine" / "companyWideOperationalQuarantineV1.json"
STORAGE = ROOT / "doctrine" / "storageTopologyV1.json"
SQLITE = "sqliteStrict"
MARIA = "mariaDbCandidate"
IDENT = re.compile(r"[a-z][A-Za-z0-9]{0,79}\Z")
COMMIT_SHA = re.compile(r"[0-9a-f]{40}\Z")
BLOB_SHA = re.compile(r"[0-9a-f]{40}\Z")
SAFE_DDL_TERMS = re.compile(
    r"\b(?:DROP|DELETE|TRUNCATE|ALTER|ATTACH|DETACH|REPLACE|"
    r"GRANT|REVOKE|INFILE|OUTFILE|EXECUTE|PREPARE|CREATE\s+USER|"
    r"PRAGMA\s+writable_schema)\b",
    re.IGNORECASE
)
EXPECTED = {
    "fourLaneEvents": (
        "host/api/typedLanesV1.sql", SQLITE,
        ("aiManifestStream", "artifactPointer", "booleanStream", "numericStream",
         "streamEvent", "textStream"),
    ),
    "premonitionArt": (
        "host/api/premonitionAssetLedgerV1.sql", SQLITE,
        ("premonitionAssetRecord", "premonitionTransformRecord"),
    ),
    "mariaDbUpdateReceipts": (
        "host/api/luhmMariaDbReceiptV1.sql", MARIA, ("luhm_update_receipt",),
    ),
}


def _json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("RED_REGISTRY_NOT_OBJECT")
    return data


def git_blob_sha1(payload: bytes) -> str:
    """Matches Git's unmodified SHA-1 blob identifier, not a publisher signature."""
    return hashlib.sha1(
        b"blob " + str(len(payload)).encode("ascii") + b"\0" + payload
    ).hexdigest()


def _safe_path(path: Any) -> bool:
    if not isinstance(path, str) or not path or len(path) > 160:
        return False
    if Path(path).is_absolute() or ".." in Path(path).parts or "\\" in path:
        return False
    full = (ROOT / path).resolve()
    return full.is_file() and full.is_relative_to(ROOT.resolve())


def _code(sql: str) -> str:
    # All locked v1 schemas use regular '--' line comments, no block comments.
    if "/*" in sql or "*/" in sql:
        raise ValueError("RED_SQL_BLOCK_COMMENT_REQUIRES_REVIEW")
    return "\n".join(line.split("--", 1)[0] for line in sql.splitlines())


def inspect_sql_source(
    record: Mapping[str, Any], payload: bytes, *,
    parsed: str | None = None,
) -> dict[str, Any]:
    """Deterministic source fixture; passing is NOT a live DB migration."""
    schema_id = record.get("id")
    if schema_id not in EXPECTED:
        raise ValueError("RED_UNKNOWN_SQL_SOURCE")
    path, dialect, table_names = EXPECTED[schema_id]
    if (record.get("path") != path or record.get("dialect") != dialect or
            record.get("version") != 1 or
            record.get("expectedTables") != list(table_names)):
        raise ValueError("RED_SQL_REGISTRY_SHAPE")
    if (not isinstance(payload, bytes) or not payload or
            len(payload) > 256000):
        raise ValueError("RED_SQL_SOURCE_BOUNDS")
    if (not isinstance(record.get("gitBlobSha1"), str) or
            BLOB_SHA.fullmatch(record["gitBlobSha1"]) is None or
            git_blob_sha1(payload) != record["gitBlobSha1"]):
        raise ValueError("RED_SQL_GITHUB_BLOB_DRIFT")
    try:
        sql = payload.decode("utf8")
    except UnicodeError as exc:
        raise ValueError("RED_SQL_UTF8") from exc
    source_sql = sql if parsed is None else parsed
    executable = _code(source_sql)
    if SAFE_DDL_TERMS.search(executable):
        raise ValueError("RED_DESTRUCTIVE_SQL_SOURCE")
    checks = []
    if dialect == SQLITE:
        # Executing DDL only against a brand-new disposable in-memory connection.
        with sqlite3.connect(":memory:") as db:
            db.executescript(source_sql)
            enabled = db.execute("PRAGMA foreign_keys").fetchone()
            if enabled != (1,):
                raise ValueError("RED_SQLITE_FOREIGN_KEYS_DISABLED")
            rows = db.execute(
                "SELECT name,sql FROM sqlite_master WHERE type='table'"
            ).fetchall()
            observed = {name for name, _ in rows}
            if observed != set(table_names):
                raise ValueError("RED_SQLITE_TABLE_IDENTITY")
            for name, definition in rows:
                if name not in table_names or not definition.strip().endswith("STRICT"):
                    raise ValueError("RED_SQLITE_STRICT_REQUIRED")
            if db.execute("PRAGMA foreign_key_check").fetchone() is not None:
                raise ValueError("RED_SQLITE_FK_CHECK")
            if db.execute("PRAGMA integrity_check").fetchone() != ("ok",):
                raise ValueError("RED_SQLITE_INTEGRITY_CHECK")
        checks.extend(["sqliteParseInMemory","sqliteStrict","sqliteForeignKeys"])
    else:
        normalized = " ".join(executable.split()).lower()
        if (normalized.count("create table if not exists ") != 1 or
                "create table if not exists luhm_update_receipt " not in normalized or
                "engine=innodb" not in normalized or
                "unique key exact_receipt" not in normalized or
                "sha256_hex char(64)" not in normalized or
                "source_ref char(40)" not in normalized):
            raise ValueError("RED_MARIADB_STATIC_DDL_CONTRACT")
        checks.extend(["mariaDbStaticGrammarSubsetOnly","neverConnectedToMariaDb"])
    return {
        "schemaId": schema_id, "path": path, "dialect": dialect,
        "gitBlobSha1": git_blob_sha1(payload),
        "contentSha256": hashlib.sha256(payload).hexdigest(),
        "tableCount": len(table_names), "checks": checks,
        "liveDbCompared": False, "liveMigrationApplied": False,
        "greenAuthority": False,
    }


def audit() -> dict[str, Any]:
    policy = _json(REGISTRY)
    problems: list[str] = []
    if policy.get("schema") != "luhmOs.githubSqlSourceRegistry.v1":
        problems.append("RED_SOURCE_REGISTRY_SCHEMA")
    canonical = policy.get("canonicalSource", {})
    if (canonical.get("repo") != "eggie-admin/LuHm-OS" or
            canonical.get("branch") != "main" or
            canonical.get("notRuntimeDatabase") is not True):
        problems.append("RED_GITHUB_SOURCE_AUTHORITY")
    if policy.get("projectBrand") != "LuHm-OS: Project Premonition":
        problems.append("RED_BRAND_IDENTITY")
    if policy.get("dialectOrder") != [SQLITE, MARIA]:
        problems.append("RED_SQL_DIALECTS")
    relations = policy.get("relation", [])
    if not isinstance(relations, list) or len(relations) < 5 or not all(
            _safe_path(item) for item in relations):
        problems.append("RED_CANON_ANCHORS")
    schemas = policy.get("schemas", [])
    if not isinstance(schemas, list) or len(schemas) != len(EXPECTED) or [
            s.get("id") for s in schemas if isinstance(s, dict)] != list(EXPECTED):
        problems.append("RED_SQL_SOURCE_ORDER_OR_COUNT")
        schemas = []
    verified = []
    for record in schemas:
        if not isinstance(record, dict):
            problems.append("RED_SQL_SOURCE_RECORD")
            continue
        if (not _safe_path(record.get("path")) or
                not isinstance(record.get("pythonReaders"), list) or
                not record["pythonReaders"] or not all(
                    _safe_path(reader) for reader in record["pythonReaders"])):
            problems.append("RED_SQL_OR_PYTHON_PATH")
            continue
        try:
            row = inspect_sql_source(record, (ROOT / record["path"]).read_bytes())
        except (OSError, ValueError, sqlite3.Error) as exc:
            problems.append(str(exc) if str(exc).startswith("RED_")
                            else "RED_SQL_SOURCE_VALIDATION")
            continue
        if record.get("liveApplied") is not False:
            problems.append("RED_SQL_FAKE_APPLIED")
        verified.append(row)
    migration = policy.get("migrationPolicy", {})
    for name in (
        "sourceChangesRequireVersionIncrement",
        "pinnedBlobShaMustChangeWithReviewedSource", "noAutoApply",
        "noRuntimeDatabaseConnectionsFromCi", "noDdlApplyFromMcp",
        "migrationExecutionNeedsExactSourceAndBackup", "sqliteForeignKeysOn",
        "mariaDbRequiresPrivateNetworkTlsIdentityAndApproval",
        "sqlNotAnArtworkFileServer", "noPublicSqlPort", "noSecretsInGit",
        "noProductionDatabaseDiscovery", "ciCanExecuteOnlyEphemeralSqlite",
        "companyQuarantineOverrides",
    ):
        if migration.get(name) is not True:
            problems.append("RED_SQL_MIGRATION_POLICY")
            break
    q = _json(QUARANTINE)
    storage = _json(STORAGE)
    if q.get("state") != "QUARANTINED" or q.get("activeTaskWorkersAllowed") is not False:
        problems.append("RED_SQL_QUARANTINE_DRIFT")
    if (storage.get("roles", {}).get("github", {}).get("canonicalSourceAuthority") is not True
            or storage.get("rules", {}).get("databaseMayStoreCanonicalBinary") is not False):
        problems.append("RED_SQL_STORAGE_LAW")
    if (policy.get("actualAppliedMigrations") != 0 or
            policy.get("noAutoMerge") is not True or
            policy.get("noAutoDeploy") is not True or
            policy.get("crownStatus") != "STOP"):
        problems.append("RED_SQL_CROWN_OR_DEPLOY")
    return {
        "schema": "luhmOs.githubSqlSourceAudit.v1",
        "status": "SOURCE_LOCKS_CONSISTENT_ONLY" if not problems else "RED_SOURCE_DRIFT",
        "sourceConsistent": not problems,
        "problems": sorted(set(problems)),
        "verifiedSourceCount": len(verified),
        "verifiedSources": verified,
        "sourceRepo": "eggie-admin/LuHm-OS",
        "runtimeDatabaseConnections": 0, "appliedMigrations": 0,
        "publicSqlEndpoints": 0,
        "workingMigrationApproved": False,
        "actualGithubHeadObserved": False,
        "greenAuthority": False, "crownAuthority": False,
    }


def plan(task_id: str, source_ref: str, scope_id: str,
         schema_id: str) -> dict[str, Any]:
    for value in (task_id, scope_id):
        if type(value) is not str or IDENT.fullmatch(value) is None:
            raise ValueError("RED_SQL_TASK_OR_SCOPE")
    if type(source_ref) is not str or COMMIT_SHA.fullmatch(source_ref) is None:
        raise ValueError("RED_SQL_EXACT_SHA")
    if schema_id not in EXPECTED:
        raise ValueError("RED_SQL_UNKNOWN_SCHEMA")
    status = audit()
    if not status["sourceConsistent"]:
        return {"status": "STOP_SOURCE_DRIFT", "problems": status["problems"],
                "greenAuthority": False, "crownAuthority": False}
    row = next(r for r in status["verifiedSources"] if r["schemaId"] == schema_id)
    return {
        "schema": "luhmOs.githubSqlMigrationPlan.v1",
        "taskId": task_id, "sourceRef": source_ref, "scopeId": scope_id,
        "sqlSchemaId": schema_id, "sourcePath": row["path"],
        "sourceBlobSha1": row["gitBlobSha1"],
        "contentSha256": row["contentSha256"],
        "state": "HOLD_REAL_HOST_BACKUP_AND_OWNER_APPROVAL",
        "required": [
            "exactCurrentGitHubCommitAndCI",
            "approvedTargetDatabaseIdentity",
            "authenticatedPrivateHostAndBackup",
            "runtimeSchemaVersionComparison",
            "dialectSpecificTestAndRollback",
            "explicitProfessorApproval",
        ],
        "runtimeHeadProven": False, "productionDatabaseProven": False,
        "workDoneOnLiveDatabase": False,
        "networkCalls": 0, "writes": 0, "greenAuthority": False,
        "crownAuthority": False,
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2))

#!/usr/bin/env python3
"""Local-only tests for immutable GitHub SQL schema source policy."""
from __future__ import annotations

import copy
import importlib.util
import sqlite3
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "githubSqlSourceAudit", ROOT / "tools/githubSqlSourceAudit.py")
assert spec is not None and spec.loader is not None
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
SHA = "f0cb6ee54066b490c0e80efc2c96200fec76ee2d"


class TestGitHubSqlSource(unittest.TestCase):
    def test_three_real_schemas_and_blob_locks(self):
        result = gate.audit()
        self.assertTrue(result["sourceConsistent"], result["problems"])
        self.assertEqual(result["verifiedSourceCount"], 3)
        self.assertEqual(
            [r["schemaId"] for r in result["verifiedSources"]],
            ["fourLaneEvents", "premonitionArt", "mariaDbUpdateReceipts"])
        self.assertEqual(result["appliedMigrations"], 0)
        self.assertEqual(result["runtimeDatabaseConnections"], 0)
        self.assertFalse(result["greenAuthority"])
        for row in result["verifiedSources"]:
            self.assertEqual(len(row["gitBlobSha1"]), 40)
            self.assertEqual(len(row["contentSha256"]), 64)
            self.assertFalse(row["liveDbCompared"])

    def test_every_schema_held_until_exact_database_target_and_approval(self):
        for schema_id in gate.EXPECTED:
            with self.subTest(schema_id=schema_id):
                p = gate.plan("sqlTask", SHA, "privateScope", schema_id)
                self.assertEqual(p["state"], "HOLD_REAL_HOST_BACKUP_AND_OWNER_APPROVAL")
                self.assertFalse(p["productionDatabaseProven"])
                self.assertEqual(p["writes"], 0)
                self.assertFalse(p["crownAuthority"])

    def test_changed_sql_bytes_require_explicit_new_version_review(self):
        record = gate._json(gate.REGISTRY)["schemas"][0]
        good = (ROOT / record["path"]).read_bytes()
        with self.assertRaisesRegex(ValueError, "RED_SQL_GITHUB_BLOB_DRIFT"):
            gate.inspect_sql_source(record, good + b"\n-- silent rewrite")
        with self.assertRaisesRegex(ValueError, "RED_SQL_REGISTRY_SHAPE"):
            gate.inspect_sql_source({**record, "version": 2}, good)

    def test_ddl_danger_patterns_refuse_even_with_matching_test_blob(self):
        record = gate._json(gate.REGISTRY)["schemas"][2]
        raw = (ROOT / record["path"]).read_bytes()
        for change in ("DROP TABLE luhm_update_receipt;",
                       "GRANT ALL ON *.* TO user;",
                       "DELETE FROM luhm_update_receipt;"):
            with self.subTest(change=change), self.assertRaisesRegex(
                    ValueError, "RED_DESTRUCTIVE_SQL_SOURCE"):
                gate.inspect_sql_source(record, raw, parsed=raw.decode() + change)

    def test_sqlite_art_metadata_rejects_public_claims_and_wrong_source_ref(self):
        sql = (ROOT / "host/api/premonitionAssetLedgerV1.sql").read_text()
        data = ("artOne", "taskOne", SHA, "scopeOne",
                "vectorBrand", "svg", "f" * 64, 96,
                "private:artOne", "PRIVATE_REVIEW", "UNKNOWN", 0)
        stmt = ("INSERT INTO premonitionAssetRecord "
                "(assetId,taskId,sourceRef,scopeId,assetClass,format,"
                "sha256Hex,byteCount,logicalPrivatePointer,rightsState,"
                "provenanceState,publicReleaseAuthorized) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)")
        with sqlite3.connect(":memory:") as db:
            db.executescript(sql)
            db.execute(stmt, data)
            self.assertEqual(db.execute(
                "SELECT COUNT(*) FROM premonitionAssetRecord").fetchone()[0], 1)
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute(stmt, ("artTwo",) + data[1:-1] + (1,))
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute(stmt, ("artThree",) + (data[1], "main") + data[3:])

    def test_quarantine_and_storage_override_blocked(self):
        original = gate._json
        def forged(path):
            policy = original(path)
            if path == gate.REGISTRY:
                policy = copy.deepcopy(policy)
                policy["migrationPolicy"]["noAutoApply"] = False
                policy["actualAppliedMigrations"] = 1
            return policy
        with patch.object(gate, "_json", side_effect=forged):
            result = gate.audit()
        self.assertIn("RED_SQL_MIGRATION_POLICY", result["problems"])
        self.assertIn("RED_SQL_CROWN_OR_DEPLOY", result["problems"])

    def test_unknown_dialect_schema_source_and_task_rejected(self):
        for item in ("nonexistent", "", "dropDatabase"):
            with self.subTest(item=item), self.assertRaises(ValueError):
                gate.plan("sqlTask", SHA, "privateScope", item)
        with self.assertRaises(ValueError):
            gate.plan("sqlTask", "main", "privateScope", "premonitionArt")
        with self.assertRaises(ValueError):
            gate.plan("../etc", SHA, "privateScope", "premonitionArt")

    def test_file_path_escape_not_allowed(self):
        for path in ("../hidden.sql", "/tmp/fake.sql", "host/../../etc/passwd"):
            self.assertFalse(gate._safe_path(path))


if __name__ == "__main__":
    unittest.main()

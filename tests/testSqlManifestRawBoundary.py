"""LuHm-OS: direct-SQL AI manifest fail-closed regression checks.

Runs against disposable SQLite only. Does not invoke a provider, grant agents
authority, or apply migrations to a real database.
"""
import json
import sqlite3
import unittest

from tools.typedSqlStub import addEvent, openStub, putManifest

SOURCE_REF = "a" * 40
NOW = "2026-11-04T15:00:00Z"


class RawAiManifestBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.db = openStub()
        addEvent(self.db, "eventOne", "auditTask", SOURCE_REF, "auditScope", "lum", 1, 1, NOW)

    def tearDown(self):
        self.db.close()

    def manifest(self, **overrides):
        obj = {
            "schema": "luhmOs.aiTaskManifest.v2",
            "taskId": "auditTask",
            "sourceRef": SOURCE_REF,
            "scopeId": "auditScope",
            "providerId": "openAi",
            "capabilityId": "research",
            "authority": {"mutation": False, "green": False, "crown": False},
        }
        obj.update(overrides)
        return obj

    def raw_insert(self, payload, provider_id="openAi", capability_id="research"):
        self.db.execute(
            """INSERT INTO aiManifestStream
            (eventId,manifestJson,manifestSchema,providerId,capabilityId)
            VALUES(?,?,?,?,?)""",
            ("eventOne", json.dumps(payload), "luhmOs.aiTaskManifest.v2",
             provider_id, capability_id),
        )

    def test_adapter_accepts_only_scoped_safe_manifest(self):
        putManifest(self.db, "eventOne", self.manifest())
        self.assertEqual(self.db.execute(
            "SELECT COUNT(*) FROM aiManifestStream").fetchone()[0], 1)

    def test_direct_sql_crown_in_manifest_is_rejected(self):
        forged = self.manifest(authority={"mutation": False, "green": False, "crown": True})
        with self.assertRaises(sqlite3.DatabaseError):
            self.raw_insert(forged)

    def test_direct_sql_missing_authority_is_rejected(self):
        with self.assertRaises(sqlite3.DatabaseError):
            self.raw_insert(self.manifest(authority={}))

    def test_direct_sql_task_source_scope_mismatch_rejected(self):
        for changed in (
            {"taskId": "wrongTask"},
            {"sourceRef": "b" * 40},
            {"scopeId": "wrongScope"},
        ):
            with self.subTest(changed=changed):
                with self.assertRaises(sqlite3.DatabaseError):
                    self.raw_insert(self.manifest(**changed))

    def test_direct_sql_provider_route_mismatch_rejected(self):
        with self.assertRaises(sqlite3.DatabaseError):
            self.raw_insert(self.manifest(), provider_id="otherProvider")

    def test_direct_sql_invalid_root_rejected(self):
        with self.assertRaises(sqlite3.DatabaseError):
            self.raw_insert({"schema": "luhmOs.aiTaskManifest.v2"})

    def test_manifest_updates_cannot_grant_crown(self):
        self.raw_insert(self.manifest())
        forged = self.manifest(authority={"mutation": False, "green": False, "crown": True})
        with self.assertRaises(sqlite3.DatabaseError):
            self.db.execute("UPDATE aiManifestStream SET manifestJson=? WHERE eventId=?",
                            (json.dumps(forged), "eventOne"))

    def test_manifest_parent_event_identity_cannot_mutate(self):
        self.raw_insert(self.manifest())
        with self.assertRaises(sqlite3.DatabaseError):
            self.db.execute("UPDATE streamEvent SET scopeId=? WHERE eventId=?",
                            ("alteredScope", "eventOne"))

    def test_manifest_size_bounded(self):
        with self.assertRaises(sqlite3.DatabaseError):
            self.raw_insert(self.manifest(extraNotes="x" * 65536))


if __name__ == "__main__":
    unittest.main()

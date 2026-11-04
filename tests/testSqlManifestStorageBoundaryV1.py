"""Fail-closed SQL storage tests for AI manifest authority and event identity.

Runs only in disposable in-memory SQLite, no provider or machine access.
"""
import copy
import json
import sqlite3
import unittest

from tools.typedSqlStub import addEvent, openStub, putManifest

SOURCE = "a" * 40
DATE = "2026-11-04T14:00:00Z"


class ManifestStorageBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.db = openStub()
        addEvent(self.db, "firstEvent", "focusedTask", SOURCE, "boundedScope",
                 "lum", 1, 1, DATE)
        self.manifest = {
            "schema": "luhmOs.aiTaskManifest.v2",
            "taskId": "focusedTask",
            "sourceRef": SOURCE,
            "scopeId": "boundedScope",
            "providerId": "openAi",
            "capabilityId": "research",
            "authority": {"mutation": False, "green": False, "crown": False},
        }

    def tearDown(self):
        self.db.close()

    def insert_raw(self, manifest, *, schema="luhmOs.aiTaskManifest.v2",
                   provider="openAi", capability="research"):
        self.db.execute(
            """INSERT INTO aiManifestStream
            (eventId, manifestJson, manifestSchema, providerId, capabilityId)
            VALUES (?, ?, ?, ?, ?)""",
            ("firstEvent", json.dumps(manifest), schema, provider, capability),
        )

    def test_valid_bounded_adapter_manifest_accepted(self):
        putManifest(self.db, "firstEvent", self.manifest)
        self.assertEqual(
            self.db.execute("SELECT COUNT(*) FROM aiManifestStream").fetchone()[0], 1
        )

    def test_direct_sql_forged_authority_rejected(self):
        for field in ("mutation", "green", "crown"):
            with self.subTest(field=field):
                candidate = copy.deepcopy(self.manifest)
                candidate["authority"][field] = True
                with self.assertRaises(sqlite3.IntegrityError):
                    self.insert_raw(candidate)

    def test_direct_sql_missing_or_wrong_authority_rejected(self):
        for authority in ({}, {"mutation": 0, "green": False, "crown": False}, None):
            with self.subTest(authority=authority):
                candidate = copy.deepcopy(self.manifest)
                candidate["authority"] = authority
                with self.assertRaises(sqlite3.IntegrityError):
                    self.insert_raw(candidate)

    def test_direct_sql_task_source_scope_schema_and_route_rejected(self):
        variants = [
            {"taskId": "otherTask"},
            {"sourceRef": "b" * 40},
            {"scopeId": "otherScope"},
            {"schema": "otherSchema"},
            {"providerId": "otherProvider"},
            {"capabilityId": "otherCapability"},
        ]
        for patch in variants:
            with self.subTest(patch=patch):
                candidate = {**self.manifest, **patch}
                with self.assertRaises(sqlite3.IntegrityError):
                    self.insert_raw(candidate)

    def test_immutable_manifest_and_parent_identity(self):
        putManifest(self.db, "firstEvent", self.manifest)
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("UPDATE aiManifestStream SET providerId=? WHERE eventId=?",
                            ("otherProvider", "firstEvent"))
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("UPDATE streamEvent SET sourceRef=? WHERE eventId=?",
                            ("b" * 40, "firstEvent"))


if __name__ == "__main__":
    unittest.main()

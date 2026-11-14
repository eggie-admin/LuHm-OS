"""LamoS SQL machine boundary tests: reject untrusted raw manifests, source-only."""
import json
import sqlite3
import unittest

from tools.typedSqlStub import addEvent, openStub, putManifest

SOURCE_REF = "a" * 40
SCHEMA = "luhmOs.aiTaskManifest.v2"


class AiManifestSqlGuardTests(unittest.TestCase):
    def setUp(self):
        self.db = openStub()
        addEvent(self.db, "firstEvent", "testTask", SOURCE_REF, "testScope",
                 "lum", 1, 1, "2026-11-04T15:00:00Z")
        self.valid = {
            "schema": SCHEMA,
            "taskId": "testTask",
            "sourceRef": SOURCE_REF,
            "scopeId": "testScope",
            "providerId": "openAi",
            "capabilityId": "research",
            "authority": {"mutation": False, "green": False, "crown": False},
        }

    def tearDown(self):
        self.db.close()

    def insert_raw(self, manifest, **overrides):
        columns = {"manifestSchema": SCHEMA, "providerId": "openAi",
                   "capabilityId": "research"}
        columns.update(overrides)
        self.db.execute(
            "INSERT INTO aiManifestStream "
            "(eventId, manifestJson, manifestSchema, providerId, capabilityId) "
            "VALUES (?, ?, ?, ?, ?)",
            ("firstEvent", json.dumps(manifest, allow_nan=False),
             columns["manifestSchema"], columns["providerId"], columns["capabilityId"]),
        )

    def test_adapter_and_direct_valid_manifest(self):
        putManifest(self.db, "firstEvent", self.valid)
        self.assertEqual(self.db.execute(
            "SELECT count(*) FROM aiManifestStream").fetchone()[0], 1)

    def test_reject_authority_flags_in_json_even_when_sql_columns_are_zero(self):
        for key in ("mutation", "green", "crown"):
            with self.subTest(key=key):
                candidate = json.loads(json.dumps(self.valid))
                candidate["authority"][key] = True
                with self.assertRaises(sqlite3.IntegrityError):
                    self.insert_raw(candidate)
        self.assertEqual(self.db.execute(
            "SELECT count(*) FROM aiManifestStream").fetchone()[0], 0)

    def test_reject_missing_or_non_boolean_authority(self):
        cases = [
            {"mutation": False, "green": False},
            {"mutation": 0, "green": False, "crown": False},
            "false",
            None,
        ]
        for authority in cases:
            with self.subTest(authority=authority):
                candidate = dict(self.valid, authority=authority)
                with self.assertRaises(sqlite3.IntegrityError):
                    self.insert_raw(candidate)

    def test_reject_parent_event_identity_mismatch(self):
        for field in ("taskId", "sourceRef", "scopeId"):
            with self.subTest(field=field):
                candidate = dict(self.valid, **{field: "wrong"})
                with self.assertRaises(sqlite3.IntegrityError):
                    self.insert_raw(candidate)

    def test_reject_schema_and_provider_route_mismatch(self):
        candidate = dict(self.valid, schema="luhmOs.legacy")
        with self.assertRaises(sqlite3.IntegrityError):
            self.insert_raw(candidate)
        candidate = dict(self.valid, providerId="untrusted")
        with self.assertRaises(sqlite3.IntegrityError):
            self.insert_raw(candidate)
        candidate = dict(self.valid, capabilityId="untrusted")
        with self.assertRaises(sqlite3.IntegrityError):
            self.insert_raw(candidate)

    def test_reject_raw_update_to_claim_crown(self):
        self.insert_raw(self.valid)
        candidate = json.loads(json.dumps(self.valid))
        candidate["authority"]["crown"] = True
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("UPDATE aiManifestStream SET manifestJson=? WHERE eventId=?",
                            (json.dumps(candidate), "firstEvent"))

    def test_reject_parent_identity_update_after_manifest(self):
        self.insert_raw(self.valid)
        for field in ("taskId", "sourceRef", "scopeId"):
            with self.subTest(field=field):
                with self.assertRaises(sqlite3.IntegrityError):
                    self.db.execute(f"UPDATE streamEvent SET {field}=? WHERE eventId=?",
                                    ("wrong", "firstEvent"))

    def test_permit_unrelated_event_metadata_edit(self):
        self.insert_raw(self.valid)
        self.db.execute("UPDATE streamEvent SET evidenceRef=? WHERE eventId=?",
                        ("receiptOne", "firstEvent"))
        self.assertEqual(self.db.execute(
            "SELECT evidenceRef FROM streamEvent WHERE eventId=?",
            ("firstEvent",)).fetchone()[0], "receiptOne")


if __name__ == "__main__":
    unittest.main()

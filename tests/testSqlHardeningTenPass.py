"""Adversarial SQL checks. These run against a disposable in-memory SQLite database."""
import sqlite3
import unittest
from pathlib import Path

from tools.typedSqlStub import addEvent, openStub, putText

SOURCE_REF = "a" * 40
TIMESTAMP = "2026-10-20T20:00:00Z"


class TenPassSqlTests(unittest.TestCase):
    def setUp(self):
        self.db = openStub()
        addEvent(self.db, "firstEvent", "testTask", SOURCE_REF, "testScope", "lum", 1, 1, TIMESTAMP)

    def tearDown(self):
        self.db.close()

    def event(self, eventId, sourceRef=SOURCE_REF, timestamp=TIMESTAMP):
        self.db.execute(
            """INSERT INTO streamEvent
            (eventId, taskId, sourceRef, scopeId, workerId, sequenceId, eighthNote, observedAt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (eventId, "testTask", sourceRef, "testScope", "lum", 2, 1, timestamp),
        )

    def test_bad_hex_source_reference_rejected_at_database_boundary(self):
        for badRef in ("G" * 40, "z" * 40, "A" * 40, "a" * 39, "a" * 41):
            with self.subTest(badRef=badRef):
                with self.assertRaises(sqlite3.IntegrityError):
                    self.event("secondEvent", badRef)

    def test_empty_or_oversized_event_identity_rejected(self):
        for badId in ("", "a" * 81):
            with self.subTest(badId=badId[:10]):
                with self.assertRaises(sqlite3.IntegrityError):
                    self.event(badId)

    def test_utc_timestamp_guard_rejects_direct_invalid_insert(self):
        for badTime in ("tomorrow", "2026-10-20T20:00:00+01:00", ""):
            with self.subTest(badTime=badTime):
                with self.assertRaises(sqlite3.IntegrityError):
                    self.event("secondEvent", timestamp=badTime)

    def test_direct_sql_infinity_rejected(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(
                """INSERT INTO numericStream
                (eventId, fieldName, valueKind, integerValue, floatValue, scaledValue, decimalScale)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                ("firstEvent", "durationMs", "float", None, float("inf"), None, None),
            )

    def test_missing_float_cannot_bypass_check_via_null(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(
                """INSERT INTO numericStream
                (eventId, fieldName, valueKind, integerValue, floatValue, scaledValue, decimalScale)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                ("firstEvent", "durationMs", "float", None, None, None, None),
            )

    def test_artifact_hash_requires_lower_hex(self):
        for sha in ("g" * 64, "A" * 64, "0" * 63):
            with self.subTest(sha=sha[:8]):
                with self.assertRaises(sqlite3.IntegrityError):
                    self.db.execute(
                        """INSERT INTO artifactPointer
                        (artifactId,eventId,fileName,sha256,storageLane,logicalFileRef,sizeBytes)
                        VALUES (?, ?, ?, ?, ?, ?, ?)""",
                        ("assetOne", "firstEvent", "preview.webp", sha, "githubSource", "assets/preview.webp", 100),
                    )

    def test_manifest_cannot_grant_authority_using_raw_sql(self):
        manifest = '{"schema":"luhmOs.aiTaskManifest.v2"}'
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(
                """INSERT INTO aiManifestStream
                (eventId,manifestJson,manifestSchema,providerId,capabilityId,mutationAuthority)
                VALUES (?, ?, ?, ?, ?, ?)""",
                ("firstEvent", manifest, "luhmOs.aiTaskManifest.v2", "openAi", "research", 1),
            )

    def test_text_parameter_is_data_not_sql(self):
        payload = "note'); DROP TABLE streamEvent; --"
        putText(self.db, "firstEvent", "comment", payload)
        self.assertEqual(self.db.execute("SELECT textValue FROM textStream").fetchone()[0], payload)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM streamEvent").fetchone()[0], 1)

    def test_postgres_review_does_not_claim_live_migration(self):
        sql = Path("host/api/typedPostgresReviewV1.sql").read_text()
        self.assertIn("REVIEW ONLY", sql)
        self.assertIn("CREATE TABLE artifactPointer", sql)
        self.assertIn("sourceRef ~ '^[0-9a-f]{40}$'", sql)
        self.assertIn("sha256 ~ '^[0-9a-f]{64}$'", sql)
        self.assertIn("CHECK((valueKind='integer'", sql)


if __name__ == "__main__":
    unittest.main()

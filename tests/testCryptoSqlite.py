#!/usr/bin/env python3
"""Typed SQLite crypto receipt regression tests. In-memory, no provider calls."""
from __future__ import annotations

import hashlib
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    assert spec is not None and spec.loader is not None
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


crypto = load("luhmCryptoBreathing", "host/api/luhmCryptoBreathing.py")
sqlite = load("luhmCryptoSqlite", "host/api/luhmCryptoSqlite.py")
REF = "f0cb6ee54066b490c0e80efc2c96200fec76ee2d"
DATA = b"fixture"


class TestCryptoSqlite(unittest.TestCase):
    def setUp(self):
        self.ledger = sqlite.CryptoSqliteLedger()
        self.receipt = crypto.run_ladder(
            task_id="taskOne", source_ref=REF, scope_id="scopeOne",
            artifact_id="artifactOne", payload=DATA,
            expected_sha256=hashlib.sha256(DATA).hexdigest(),
        )

    def tearDown(self):
        self.ledger.close()

    def test_records_one_event_and_no_data(self):
        result = self.ledger.record(self.receipt)
        self.assertEqual(result["state"], "RECORDED_LOCAL_CANDIDATE")
        rows = self.ledger.events("taskOne", REF, "scopeOne")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["sourceRef"], REF)
        self.assertFalse(result["storedRawBytes"])
        self.assertNotIn("fixture", str(rows))

    def test_same_receipt_idempotent(self):
        self.ledger.record(self.receipt)
        self.assertEqual(self.ledger.record(self.receipt)["state"], "IDEMPOTENT_REPLAY")
        self.assertEqual(len(self.ledger.events("taskOne", REF, "scopeOne")), 1)

    def test_changed_artifact_digest_cannot_reuse_source_identity(self):
        self.ledger.record(self.receipt)
        different = crypto.run_ladder(
            task_id="taskOne", source_ref=REF, scope_id="scopeOne",
            artifact_id="artifactOne", payload=b"other"
        )
        with self.assertRaisesRegex(ValueError, "REPLAY_DIGEST_CONFLICT"):
            self.ledger.record(different)
        self.assertEqual(len(self.ledger.events("taskOne", REF, "scopeOne")), 1)

    def test_untrusted_green_is_rejected(self):
        with self.assertRaises(ValueError):
            self.ledger.record({**self.receipt, "greenAuthority": True})
        self.assertEqual(self.ledger.events("taskOne", REF, "scopeOne"), [])


if __name__ == "__main__":
    unittest.main()

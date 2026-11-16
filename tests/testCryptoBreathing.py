#!/usr/bin/env python3
"""Offline R1-R4 and private MariaDB adapter regression tests."""
from __future__ import annotations

import hashlib
import hmac
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


crypto = load("luhmCryptoBreathing", "host/api/luhmCryptoBreathing.py")
sql = load("luhmMariaDbReceipt", "host/api/luhmMariaDbReceipt.py")
SHA = "f0cb6ee54066b490c0e80efc2c96200fec76ee2d"
DATA = b"LuHm-OS private offline test artifact"
KEY = b"K" * 32
ENCRYPTION_KEY = b"E" * 32
BASE = dict(task_id="demoTask", source_ref=SHA, scope_id="studioScope",
            artifact_id="assetOne", payload=DATA)


def expected() -> dict:
    return {
        "expected_sha256": hashlib.sha256(DATA).hexdigest(),
        "expected_sha512": hashlib.sha512(DATA).hexdigest(),
        "expected_sha3_256": hashlib.sha3_256(DATA).hexdigest(),
        "snapshot_ref": "snapshotOne",
    }


class CryptoBreathingTests(unittest.TestCase):
    def test_r1_requires_expected_digest(self):
        x = crypto.run_ladder(**BASE)
        self.assertEqual(x["state"], "HOLD")
        self.assertEqual([p["stage"] for p in x["stages"]], ["R1"])
        self.assertFalse(x["greenAuthority"])

    def test_r1_tamper_stops(self):
        x = crypto.run_ladder(**BASE, expected_sha256="0" * 64)
        self.assertEqual(x["state"], "STOP")
        self.assertEqual(x["stages"][0]["reason"], "SHA256_MISMATCH")

    def test_r2_needs_snapshot_and_two_digests(self):
        x = crypto.run_ladder(**BASE, expected_sha256=expected()["expected_sha256"])
        self.assertEqual([p["stage"] for p in x["stages"]], ["R1", "R2"])
        self.assertEqual(x["state"], "HOLD")

    def test_r3_hmac_identity_binding(self):
        e = expected()
        aad = crypto._auth_bytes("demoTask", SHA, "studioScope", "assetOne",
                                 "snapshotOne", e["expected_sha256"])
        mac = hmac.new(KEY, aad, hashlib.sha256).hexdigest()
        x = crypto.run_ladder(**BASE, **e, mac_key=KEY, expected_mac=mac)
        self.assertEqual([p["state"] for p in x["stages"]], ["PASS", "PASS", "PASS", "HOLD"])
        bad = crypto.run_ladder(**BASE, **e, mac_key=KEY, expected_mac="0"*64)
        self.assertEqual(bad["stages"][-1]["reason"], "HOST_MAC_MISMATCH")
        self.assertEqual(bad["state"], "STOP")

    def test_no_secret_leaks(self):
        x = crypto.run_ladder(**BASE, **expected(), mac_key=KEY, expected_mac="f"*64)
        self.assertNotIn(str(KEY), str(x))
        self.assertEqual(x["networkCalls"], 0)
        self.assertEqual(x["mariaDbWrites"], 0)

    def test_id_validation(self):
        with self.assertRaises(ValueError):
            crypto.run_ladder(**{**BASE, "source_ref": "main"})
        with self.assertRaises(ValueError):
            crypto.run_ladder(**{**BASE, "payload": b"x"*(crypto.MAX_BYTES + 1)})

    def test_aead_local_seal_and_decrypt_when_available(self):
        try:
            import cryptography  # noqa: F401
        except ImportError:
            self.skipTest("cryptography optional in local environment")
        e = expected()
        sealed = crypto.seal_local_snapshot(**BASE, snapshot_ref=e["snapshot_ref"],
                                             encryption_key=ENCRYPTION_KEY)
        aad = crypto._auth_bytes("demoTask", SHA, "studioScope", "assetOne",
                                 "snapshotOne", e["expected_sha256"])
        mac = hmac.new(KEY, aad, hashlib.sha256).hexdigest()
        receipt = crypto.run_ladder(**BASE, **e, mac_key=KEY,
                                    expected_mac=mac, encryption_key=ENCRYPTION_KEY,
                                    nonce=sealed["nonce"], encrypted_snapshot=sealed["ciphertext"])
        self.assertEqual(receipt["state"], "HOLD_FOR_PROFESSOR")
        self.assertTrue(all(x["state"] == "PASS" for x in receipt["stages"]))
        self.assertFalse(receipt["greenAuthority"])
        corrupted = sealed["ciphertext"][:-1] + bytes([sealed["ciphertext"][-1] ^ 1])
        failed = crypto.run_ladder(**BASE, **e, mac_key=KEY,
                                   expected_mac=mac, encryption_key=ENCRYPTION_KEY,
                                   nonce=sealed["nonce"], encrypted_snapshot=corrupted)
        self.assertEqual(failed["state"], "STOP")
        self.assertEqual(failed["stages"][-1]["reason"], "AESGCM_AUTHENTICATION_FAILED")


class FakeCursor:
    def __init__(self, fail=False):
        self.args = None
        self.fail = fail
        self.closed = False

    def execute(self, query, params):
        self.args = (query, params)
        if self.fail:
            raise RuntimeError("synthetic DB failure")

    def close(self):
        self.closed = True


class FakeDb:
    def __init__(self, fail=False):
        self.c = FakeCursor(fail)
        self.commits = 0
        self.rollbacks = 0

    def cursor(self):
        return self.c

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


class MariaDbAdapterTests(unittest.TestCase):
    def test_disabled_connection(self):
        x = sql.connection_plan()
        self.assertIn("MARIADB_DISABLED", x["blockingConditions"])
        self.assertFalse(x["connected"])

    def test_explicit_private_gate_and_parameterized_sql(self):
        receipt = crypto.run_ladder(**BASE, **expected())
        db = FakeDb()
        with self.assertRaises(PermissionError):
            sql.store_verified_local_receipt(receipt, connection=db)
        self.assertEqual(db.commits, 0)
        result = sql.store_verified_local_receipt(
            receipt, connection=db, allow_private_write=True)
        query, params = db.c.args
        self.assertEqual(query.count("?"), 7)
        self.assertEqual(len(params), 7)
        self.assertNotIn(params[0], query)
        self.assertEqual(db.commits, 1)
        self.assertFalse(result["greenAuthority"])
        self.assertTrue(db.c.closed)

    def test_rollback_on_database_failure(self):
        db = FakeDb(fail=True)
        with self.assertRaises(RuntimeError):
            sql.store_verified_local_receipt(crypto.run_ladder(**BASE), connection=db,
                                             allow_private_write=True)
        self.assertEqual(db.commits, 0)
        self.assertEqual(db.rollbacks, 1)

    def test_bad_receipt_rejected_before_io(self):
        r = crypto.run_ladder(**BASE)
        db = FakeDb()
        with self.assertRaises(ValueError):
            sql.store_verified_local_receipt({**r, "state": "GREEN"}, connection=db,
                                             allow_private_write=True)
        self.assertEqual(db.commits, 0)


if __name__ == "__main__":
    unittest.main()

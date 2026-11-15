#!/usr/bin/env python3
"""Studio registry fails closed. No credentials, provider requests or live database writes."""
from pathlib import Path
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"tools/buildStudioRegistrySqlite.py"
CANON=ROOT/"doctrine/studioFinalBossControlV1.json"
RECEIPT=ROOT/"campaign/instagramReturn20261115Receipt.json"

class RegistrySafety(unittest.TestCase):
    def test_source_and_receipt_proof(self):
        c=json.loads(CANON.read_text())
        r=json.loads(RECEIPT.read_text())
        self.assertEqual(c["publicDomain"],"eggiebagelface.art")
        self.assertEqual(r["mediaId"],"18149320816563627")
        self.assertTrue(c["verifiedSocial"]["instagram"]["verifiedReadback"])
        self.assertFalse(c["credentials"]["storeOnly"][0] in c["credentials"]["deny"])
        self.assertTrue(c["storage"]["databaseHoldsPrivateKeys"] is False)
        self.assertFalse(c["aiOrchestration"]["automaticExternalApiCalls"])
    def test_sqlite_build_and_gate(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"privateStudio.sqlite3"
            out=subprocess.run([sys.executable,str(SCRIPT),"--output",str(p)],
                           check=False,capture_output=True,text=True)
            self.assertEqual(out.returncode,0,msg=out.stderr)
            self.assertTrue(p.exists())
            conn=sqlite3.connect(p)
            try:
                conn.execute("PRAGMA foreign_keys=ON")
                self.assertEqual(conn.execute("SELECT COUNT(*) FROM brand").fetchone()[0],3)
                self.assertEqual(conn.execute("SELECT COUNT(*) FROM social_release").fetchone()[0],1)
                self.assertEqual(conn.execute("SELECT publication_state FROM firmware_release").fetchall(),[])
                self.assertEqual(conn.execute("SELECT COUNT(*) FROM signing_enrollment WHERE enrollment_state='verified'").fetchone()[0],0)
                self.assertEqual(conn.execute("SELECT COUNT(*) FROM provider_route WHERE billing_authorized=1").fetchone()[0],0)
                with self.assertRaises(sqlite3.IntegrityError):
                    conn.execute("INSERT INTO signing_enrollment VALUES (?,?,?,?,?,?,?)",(
                      "fakeApple","fake","verified",None,"notProvisioned",None,None))
                with self.assertRaises(sqlite3.IntegrityError):
                    conn.execute("INSERT INTO artifact_pointer VALUES (?,?,?,?,?,?,?,?)",(
                      "secretLeak","eggieBagelfaceArt",None,None,"public","pending","pending","cathedralPublic"))
                with self.assertRaises(sqlite3.IntegrityError):
                    conn.execute("INSERT INTO firmware_release VALUES (?,?,?,?,?,?,?,?,?)",(
                      "badPublic",None,"403983ae980671679cb2abaed6041d0073b76bf4",
                      "ltsPublic","android",None,None,None,"published"))
            finally:conn.close()
            again=subprocess.run([sys.executable,str(SCRIPT),"--output",str(p)],
                  capture_output=True,text=True)
            self.assertNotEqual(again.returncode,0)
            self.assertTrue(p.exists())
if __name__=="__main__":unittest.main()

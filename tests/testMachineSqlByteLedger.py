import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from tools.machineSqlByteLedger import ingest

class MachineSqlByteLedgerTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.executescript("""CREATE TABLE milestone(taskId TEXT,sourceRef TEXT,lane TEXT,status TEXT,
            artifactRef TEXT,artifactSha256 TEXT,sizeBytes INTEGER,
            PRIMARY KEY(taskId,sourceRef,lane))""")
        self.sample = {"taskId":"machine1","sourceRef":"a"*40,"lane":"testing","status":"AMBER"}

    def test_sortable_receipt(self):
        ingest(self.db,self.sample)
        row=self.db.execute("SELECT lane,status FROM milestone").fetchone()
        self.assertEqual(row,("testing","AMBER"))

    def test_reject_wrong_sha(self):
        self.sample["sourceRef"]="abc"
        with self.assertRaises(ValueError):
            ingest(self.db,self.sample)

    def test_reject_promotion_lane(self):
        self.sample["lane"]="production"
        with self.assertRaises(ValueError):
            ingest(self.db,self.sample)

    def test_binary_digest_not_binary_storage(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"sample.bin"
            p.write_bytes(bytes.fromhex("00ff10"))
            self.sample["artifactPath"]=str(p)
            ingest(self.db,self.sample)
            row=self.db.execute("SELECT artifactSha256,sizeBytes FROM milestone").fetchone()
            self.assertEqual(len(row[0]),64)
            self.assertEqual(row[1],3)

if __name__ == "__main__":
    unittest.main()

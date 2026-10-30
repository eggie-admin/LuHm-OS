import json,sqlite3,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
K=ROOT/'packages'/'cathedral-kernel'
sys.path.insert(0,str(K))
from cathedral_envelope import CathedralEnvelope,normalize_envelope,source_snapshot
V=json.loads((K/'tests/vectors.json').read_text())
class Tests(unittest.TestCase):
    def test_vectors(self):
        good=V['valid']; a=normalize_envelope(good)
        self.assertEqual(a['hashes'][0],'b'*64)
        self.assertEqual(CathedralEnvelope(good).canonical(),json.dumps(a,separators=(',',':')))
        self.assertFalse(source_snapshot(good)['executable'])
        for row in V['invalid']:
            with self.subTest(row=row['name']),self.assertRaises(ValueError):
                normalize_envelope({**good,**row['patch']})
    def test_sqlite_guard(self):
        c=sqlite3.connect(':memory:')
        c.executescript((K/'schema.sql').read_text())
        good=V['valid']
        c.execute('INSERT INTO sourceReceipt(id,sourceRef,scopeId,canonical) VALUES(?,?,?,?)',(good['taskId'],good['sourceRef'],good['scopeId'],CathedralEnvelope(good).canonical()))
        with self.assertRaises(sqlite3.IntegrityError):
            c.execute('UPDATE sourceReceipt SET approval=1')
        with self.assertRaises(sqlite3.IntegrityError):
            c.execute('UPDATE sourceReceipt SET costCents=1')
        c.close()
if __name__=='__main__':unittest.main()

"""No-network, no-secret, no-Crown negative controls for Canon HEX SQL snapshots."""
from __future__ import annotations
from pathlib import Path
import json
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from tools import canonHexLedger as h


class HexLedgerTests(unittest.TestCase):
    def test_hex_metadata_field_is_explicit_and_exact(self):
        self.assertTrue(h.hex_ref('a'*40,'sourceRef'))
        self.assertTrue(h.hex_ref('b'*64,'certificateFingerprint'))
        self.assertFalse(h.hex_ref('a'*40,'customerRecord'))
        self.assertFalse(h.hex_ref('z'*64,'sha256'))
        self.assertFalse(h.hex_ref('a'*39,'commitSha'))
        self.assertFalse(h.hex_ref('a'*64,'apiTokenSha256'))
        self.assertFalse(h.hex_ref('a'*64,'privateKeyFingerprint'))
        self.assertFalse(h.hex_ref('a'*64,'credentialDigest'))

    def test_hash_inventory_ignores_generic_hex_and_secret_fields(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); (root/'doctrine').mkdir()
            (root/'doctrine'/'sample.json').write_text(json.dumps({
                'sourceRef':'a'*40,'hash': 'b'*64, 'certificateFingerprint':'c'*64,
                'apiTokenSha256':'d'*64, 'privateKeyFingerprint':'e'*64,
                'children':[{'commitSha':'f'*40},{'randomId':'0'*64}]
            }))
            got=h.collected_refs(root)
            self.assertEqual({x[2] for x in got},{'sourceRef','certificateFingerprint','commitSha'})
            self.assertEqual(len(got),3)

    def test_checkpoint_digest_is_deterministic_and_order_sensitive(self):
        self.assertEqual(h.digest({'a':1,'b':2}), h.digest({'b':2,'a':1}))
        self.assertNotEqual(h.digest([1,2]),h.digest([2,1]))

    def test_scale_restrictions(self):
        self.assertEqual(h.SCALES,(256,512,1024))
        self.assertEqual(h.MAX_HASH_REFS,4096)

    def test_canon_source_not_silently_promoted(self):
        self.assertTrue(h.EXCLUDE_FIELD.search('privateKeyFingerprint'))
        self.assertFalse(h.hex_ref('a'*64,'signingKey'))

    def test_full_snapshot_and_negative_controls(self):
        source='a'*40
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/'repo'; root.mkdir(); (root/'doctrine').mkdir()
            (root/'LICENSE').write_text('GNU GENERAL PUBLIC LICENSE\nVersion 3')
            (root/'doctrine'/'sample.json').write_text(json.dumps({'sourceRef':source,'artifactDigest':'f'*64,'apiToken':'b'*64}))
            dbpath=Path(td)/'snap.db'
            statuses=['GREEN_SOURCE','AMBER_EXTERNAL_RECEIPT_REQUIRED','BLOCKED_CROWN']
            cells=[{'hex':f'0x{i:03x}','family':'deb','profile':'debian13Amd64',
                    'stage':('source' if i%3==0 else 'build' if i%3==1 else 'release'),
                    'control':'exactSource', 'status':statuses[i%3],
                    'evidenceRefs':['git:HEAD']} for i in range(256)]
            result={'scale':256,'cells':cells,'counts':dict.fromkeys(statuses,0)}
            patches=(patch.object(h,'exact_git_sha',return_value=source),
                     patch.object(h,'assess',return_value=result),
                     patch.object(h,'history',return_value=[(source,'N'),('b'*40,'G')]),
                     patch.object(h,'timestamp',return_value='2026-11-16T00:00:00Z'))
            with patches[0],patches[1],patches[2],patches[3]:
                with self.assertRaisesRegex(ValueError,'RED_EXACT_SOURCE_MISMATCH'):
                    h.build(root,dbpath,expected_source='c'*40)
                with self.assertRaisesRegex(ValueError,'RED_SQL_OUTPUT_INSIDE_SOURCE_TREE'):
                    h.build(root,root/'bad.db')
                with self.assertRaisesRegex(ValueError,'RED_INVALID_SCALE_SET'):
                    h.build(root,dbpath,scales=(64,))
                got=h.build(root,dbpath,expected_source=source)
            self.assertEqual(got['checkpointCount'],4)
            self.assertEqual(got['recordCounts']['hexSlot'],256)
            self.assertEqual(got['recordCounts']['checkpoint64'],4)
            self.assertEqual(got['recordCounts']['commitMetadata'],2)
            self.assertEqual(got['recordCounts']['sourceDigestMetadata'],2)
            self.assertEqual(got['rootLicense'],'GPL-3.0')
            self.assertEqual(got['crownStatus'],'STOP')
            self.assertEqual(got['tlsChain'],'UNVERIFIED')
            self.assertFalse(got['signingPerformed'])
            self.assertEqual(got['checkpoints'][0]['hexFirst'],'0x000')
            self.assertEqual(got['checkpoints'][-1]['hexLast'],'0x0ff')
            self.assertEqual(got['checkpoints'][1]['prior'],got['checkpoints'][0]['sha256'])
            db=sqlite3.connect(dbpath)
            try:
                self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0],'ok')
                self.assertEqual(db.execute('SELECT count(*) FROM aiManifestStream').fetchone()[0],1)
                self.assertEqual(db.execute('SELECT max(mutationAuthority + greenAuthority + crownAuthority) FROM aiManifestStream').fetchone()[0],0)
                self.assertEqual(db.execute("SELECT count(*) FROM textStream WHERE textValue=?",('b'*64,)).fetchone()[0],0)
                self.assertEqual(db.execute("SELECT count(*) FROM booleanStream WHERE fieldName='releaseApproved' AND booleanValue=1").fetchone()[0],0)
            finally: db.close()

if __name__ == '__main__': unittest.main()

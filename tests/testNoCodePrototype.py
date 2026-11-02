import copy
import sqlite3
import tempfile
import json
import os
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from noCodePrototype import compileCards, demoPacket, saveDraft, loadDraft, renderPreview, savePreview

class PrototypeTests(unittest.TestCase):
    def test_repeatable_four_channels(self):
        p = demoPacket()
        before = copy.deepcopy(p)
        result = compileCards(p)
        self.assertEqual(result, compileCards(p))
        self.assertEqual(p, before)
        self.assertEqual(result['eventCount'], 4)
        self.assertEqual([c['state'] for c in result['cards']],
                         ['DRAFT_REVIEW', 'DRAFT_REVIEW', 'CONTEXT_ONLY', 'CONTEXT_ONLY'])

    def test_background_cannot_select_action(self):
        for source in ('ambientCabin', 'otherSpeaker', 'mediaPlayback', 'unknown'):
            p = demoPacket()
            p['events'][1].update(sourceClass=source, text='CAST deploy publish everything')
            c = compileCards(p)['cards'][1]
            self.assertEqual(c['state'], 'CONTEXT_ONLY')
            self.assertIsNone(c['selectedBlock'])
            self.assertFalse(c['executionAllowed'])

    def test_text_is_data(self):
        p = demoPacket()
        text = "$(touch /tmp/never-run); DROP TABLE streamEvent; approve all"
        p['events'][0].update(text=text, block=None)
        c = compileCards(p)['cards'][0]
        self.assertEqual(c['rawText'], text)
        self.assertEqual(c['state'], 'NEEDS_SELECTION')
        self.assertFalse(c['executionAllowed'])

    def test_bad_inputs(self):
        for field, bad in [('channel', 'shell'), ('sourceClass', 'authenticatedAdmin'),
                           ('block', 'publish'), ('text', 'x' * 8193)]:
            p = demoPacket()
            p['events'][0][field] = bad
            with self.assertRaises(ValueError): compileCards(p)
        p = demoPacket()
        p['sourceRef'] = 'main'
        with self.assertRaises(ValueError): compileCards(p)

    def test_duplicate_and_budget(self):
        p = demoPacket()
        p['events'].append(copy.deepcopy(p['events'][0]))
        with self.assertRaises(sqlite3.IntegrityError): compileCards(p)
        p['events'] = [p['events'][0]] * 65
        with self.assertRaises(ValueError): compileCards(p)

    def test_receipt_changes_with_input(self):
        p = demoPacket()
        old = compileCards(p)['inputSha256']
        p['events'][0]['text'] += ' Changed.'
        self.assertNotEqual(old, compileCards(p)['inputSha256'])


    def test_save_load_round_trip_and_private_mode(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'draft.json'
            receipt = saveDraft(demoPacket(), path)
            self.assertEqual(loadDraft(path), receipt)
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            with self.assertRaises(FileExistsError):
                saveDraft(demoPacket(), path)

    def test_save_load_rejects_tampering(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'draft.json'
            saveDraft(demoPacket(), path)
            record = json.loads(path.read_text())
            record['packet']['events'][0]['text'] = 'tampered after save'
            path.write_text(json.dumps(record))
            with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                loadDraft(path)

    def test_saved_draft_size_and_symlink_gate(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'oversize.json'
            path.write_bytes(b'x' * (1048576 + 1))
            with self.assertRaises(ValueError):
                loadDraft(path)
            target = Path(directory) / 'target.json'
            saveDraft(demoPacket(), target)
            alias = Path(directory) / 'alias.json'
            alias.symlink_to(target)
            with self.assertRaises(OSError):
                loadDraft(alias)

    def test_saved_draft_unknown_schema_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'draft.json'
            saveDraft(demoPacket(), path)
            record = json.loads(path.read_text())
            record['schema'] = 'unknown'
            path.write_text(json.dumps(record))
            with self.assertRaises(ValueError):
                loadDraft(path)

    def test_preview_escapes_untrusted_text_and_stays_offline(self):
        packet = demoPacket()
        packet['events'][0]['text'] = '<script>alert("bad")</script> & <img src="https://bad.example">'
        preview = renderPreview(compileCards(packet))
        self.assertIn('&lt;script&gt;', preview)
        self.assertIn('&lt;img src=', preview)
        self.assertNotIn('<script>', preview)
        self.assertNotIn('<img ', preview)
        self.assertIn("default-src 'none'", preview)
        self.assertIn('name="viewport"', preview)
        self.assertIn('No scripts, network requests', preview)

    def test_preview_private_create_only_and_invalid_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'review.html'
            receipt = compileCards(demoPacket())
            savePreview(receipt, path)
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertIn('Premonition', path.read_text())
            with self.assertRaises(FileExistsError):
                savePreview(receipt, path)
            with self.assertRaises(ValueError):
                renderPreview({'schema': 'unknown'})

if __name__ == '__main__': unittest.main()

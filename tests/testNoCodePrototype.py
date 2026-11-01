import copy
import sqlite3
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from noCodePrototype import compileCards, demoPacket

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

if __name__ == '__main__': unittest.main()

"""Reject unsafe or misleading catalog changes before regenerating the page."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('gallery', ROOT / 'tools/renderYumeReferenceGallery.py')
gallery = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gallery)

class CatalogSafetyTest(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(gallery.CATALOG.read_text())

    def test_catalog_and_escaping(self):
        self.assertEqual(len(gallery.validate(self.data)), 29)
        self.data['cards'][0]['title'] = '<script>alert(1)</script>'
        page = gallery.render(self.data)
        self.assertNotIn('<script>alert(1)</script>', page)
        self.assertIn('&lt;script&gt;', page)

    def test_rejects_bad_sources(self):
        for url in ('javascript:alert(1)', 'https://www.nexusmods.com/fallout4/mods/top', 'https://github.com.evil.test/repo', 'https://secret@github.com/repo'):
            with self.subTest(url=url):
                changed = copy.deepcopy(self.data)
                changed['cards'][0]['url'] = url
                with self.assertRaises(ValueError): gallery.validate(changed)

    def test_rejects_duplicates(self):
        self.data['cards'].append(self.data['cards'][0])
        with self.assertRaises(ValueError): gallery.validate(self.data)

    def test_rejects_short_or_incomplete_catalog(self):
        self.data['cards'] = self.data['cards'][:23]
        with self.assertRaises(ValueError): gallery.validate(self.data)

if __name__ == '__main__':
    unittest.main()

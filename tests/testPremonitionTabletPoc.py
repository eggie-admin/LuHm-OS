"""Android POC source constraints; real device still needs human install receipt."""
from pathlib import Path
import hashlib
import unittest

ROOT=Path(__file__).resolve().parents[1]

class PremonitionTabletPocTests(unittest.TestCase):
    def test_original_art_hash(self):
        art=ROOT/'frontEnd/premonition-hero.webp'
        self.assertEqual(hashlib.sha256(art.read_bytes()).hexdigest(),
            'a8982f8f7d79a092735ba551be1d62c505bf31bc9967811dfd8ae2477bc522c0')
    def test_original_branded_start_screen_and_world_entry(self):
        html=(ROOT/'frontEnd/index.html').read_text()
        css=(ROOT/'frontEnd/styles.css').read_text()
        for key in ('PROJECT <em>PREMONITION</em>','premonition-hero.webp','data-luhm-play-aramoor'):
            self.assertIn(key,html)
        self.assertIn('.premonitionHeroPortrait',css)
        self.assertNotIn('http://',html)
        self.assertNotIn('https://',html)
    def test_workflow_debug_signing_and_separate_package(self):
        wf=(ROOT/'.github/workflows/aramoor-samsung-arm64-test-apk.yml').read_text()
        for key in ('art.eggiebagelface.luhmos.premonitionpoc','--export-debug','apksigner',
                    'zipalign','disposableSigner','ownerReleaseSigner','permissions/internet=false',
                    'a8982f8f7d79a092735ba551be1d62c505bf31bc9967811dfd8ae2477bc522c0'):
            self.assertIn(key,wf)
        self.assertNotIn('gh release create',wf)
        self.assertNotIn('gh release upload',wf)
    def test_icon_generator_source_is_local(self):
        src=(ROOT/'tools/premonitionPocIcons.py').read_text()
        self.assertIn("def image(n):",src)
        self.assertNotIn('requests',src)
        self.assertNotIn('subprocess',src)
    def test_icon_png_is_deterministic_and_valid(self):
        from tools import premonitionPocIcons as i
        pic=i.image(192)
        self.assertTrue(pic.startswith(b'\x89PNG\r\n\x1a\n'))
        self.assertEqual(pic,i.image(192))

if __name__=='__main__':
    unittest.main()

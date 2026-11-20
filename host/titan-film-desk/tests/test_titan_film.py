import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from titan_film import Studio, SCHEMA, probe, digest_file


class FilmDeskTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
            raise unittest.SkipTest('FFmpeg required for integration test')

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.studio = Studio(self.root / 'studio')
        self.src = self.root / 'synthetic.mp4'
        subprocess.run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-y',
                        '-f','lavfi','-i','testsrc2=size=320x180:rate=24:duration=3',
                        '-c:v','libx264','-pix_fmt','yuv420p',str(self.src)],check=True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_ingest_hash_dedupe_and_proxy(self):
        original = digest_file(self.src)
        a = self.studio.ingest(self.src)
        self.assertEqual(a['sha256'], original)
        self.assertEqual(self.studio.ingest(self.src)['mediaId'], a['mediaId'])
        self.assertEqual(len(self.studio.list_assets()), 1)
        p = self.studio.proxy(a['mediaId'])
        self.assertEqual(p['status'], 'PROXY_READY_PRIVATE')
        self.assertTrue((self.studio.root / 'cache' / a['mediaId'] / 'contact.png').exists())
        self.assertEqual(digest_file(self.src), original)

    def test_render_and_reject_out_of_bounds(self):
        x = self.studio.ingest(self.src)
        edl = {'schema': SCHEMA, 'cuts': [{'mediaId': x['mediaId'], 'startSeconds': 0.4,
                                           'endSeconds': 1.3, 'effect': 'stressShake'},
                                          {'mediaId': x['mediaId'], 'startSeconds': 1.5,
                                           'endSeconds': 2.5, 'effect': 'hardMono'}]}
        rendered = self.studio.render(edl)
        preview = self.studio.root / 'exports' / rendered['outputName']
        self.assertTrue(preview.exists())
        self.assertEqual((probe(preview)['width'], probe(preview)['height']), (540, 960))
        self.assertGreater(rendered['durationSeconds'], 1.7)
        self.assertLess(rendered['durationSeconds'], 2.2)
        edl['cuts'][0]['endSeconds'] = 20
        with self.assertRaises(ValueError):
            self.studio.render(edl)
        edl['cuts'][0]['endSeconds'] = 1.3
        edl['cuts'][0]['effect'] = 'arbitraryShellFilter'
        with self.assertRaises(ValueError):
            self.studio.render(edl)

    def test_no_media_or_filename_escape(self):
        with self.assertRaises(ValueError): self.studio.ingest(self.src, name='text.txt')
        with self.assertRaises(ValueError): self.studio.media('../../etc/passwd')
        with self.assertRaises(ValueError): self.studio.render({'schema': SCHEMA, 'cuts': []})

if __name__ == '__main__': unittest.main()

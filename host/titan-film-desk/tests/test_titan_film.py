import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from http.server import ThreadingHTTPServer
from unittest.mock import patch
import urllib.error
import urllib.request
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import titan_film
from titan_film import Studio, SCHEMA, probe, digest_file, input_args, ProcessingBusyError


class FilmDeskSafetyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.studio = Studio(self.root / 'studio')

    def tearDown(self):
        self.tmp.cleanup()

    def test_ffprobe_rejects_non_file_protocols(self):
        result = {'format': {'duration': '1'}, 'streams': [
            {'codec_type': 'video', 'width': 16, 'height': 16, 'codec_name': 'h264'}]}
        with patch('titan_film.run', return_value=type('Result', (), {
                'stdout': json.dumps(result)})()) as run_mock:
            probe(Path('concat:https://example.invalid/video.mp4'))
        args = run_mock.call_args.args
        self.assertIn(('-protocol_whitelist', 'file,pipe'), tuple(zip(args, args[1:])))
        self.assertEqual(args[-2:], ('-i', 'concat:https:/example.invalid/video.mp4'))
        self.assertEqual(input_args(Path('concat:https://example.invalid/video.mp4')),
                         ('-protocol_whitelist', 'file,pipe', '-i',
                          'concat:https:/example.invalid/video.mp4'))

    def test_configured_token_is_never_printed(self):
        token = 'private-test-token-that-must-not-leak'

        class FakeServer:
            def __init__(self, address, handler):
                pass

            def serve_forever(self):
                pass

        output = io.StringIO()
        with patch.dict(os.environ, {'TITAN_TOKEN': token}), \
                patch.object(sys, 'argv', ['titan_film.py', '--root', str(self.root / 'server'), 'serve']), \
                patch('titan_film.ThreadingHTTPServer', FakeServer), \
                contextlib.redirect_stdout(output):
            titan_film.main()
        self.assertNotIn(token, output.getvalue())
        self.assertNotIn('TITAN_TOKEN=', output.getvalue())

    def test_storage_quota_rejects_oversized_addition(self):
        cached = self.studio.root / 'cache' / 'existing'
        cached.write_bytes(b'x' * 80)
        with patch.object(titan_film, 'MAX_TOTAL_MEDIA_BYTES', 100):
            self.studio.ensure_storage_capacity(20)
            with self.assertRaisesRegex(ValueError, 'storage limit'):
                self.studio.ensure_storage_capacity(21)

    def test_ingest_checks_quota_before_probing_or_copying(self):
        source = self.root / 'incoming.mp4'
        source.write_bytes(b'x')
        (self.studio.root / 'cache' / 'existing').write_bytes(b'x' * 100)
        with patch.object(titan_film, 'MAX_TOTAL_MEDIA_BYTES', 100), \
                patch('titan_film.probe') as probe_mock:
            with self.assertRaisesRegex(ValueError, 'storage limit'):
                self.studio.ingest(source)
        probe_mock.assert_not_called()
        self.assertFalse(any((self.studio.root / 'imports').iterdir()))

    def test_processing_slot_rejects_concurrent_job(self):
        with self.studio.processing_job():
            with self.assertRaises(ProcessingBusyError):
                with self.studio.processing_job():
                    pass
        with self.studio.processing_job():
            pass

    def test_http_authorization_and_busy_response(self):
        token = 'private-test-token-with-at-least-24-chars'
        server = ThreadingHTTPServer(('127.0.0.1', 0), titan_film.make_handler(self.studio, token))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f'http://127.0.0.1:{server.server_port}'
        try:
            with self.assertRaises(urllib.error.HTTPError) as response:
                urllib.request.urlopen(base + '/api/assets')
            self.assertEqual(response.exception.code, 401)
            request = urllib.request.Request(base + '/api/assets',
                                             headers={'Authorization': 'Bearer ' + token})
            self.assertEqual(json.load(urllib.request.urlopen(request)), {'assets': []})
            with self.studio.processing_job():
                request = urllib.request.Request(
                    base + '/api/proxy',
                    data=b'{"mediaId":"000000000000000000000000"}',
                    headers={'Authorization': 'Bearer ' + token,
                             'Content-Type': 'application/json'})
                with self.assertRaises(urllib.error.HTTPError) as response:
                    urllib.request.urlopen(request)
                self.assertEqual(response.exception.code, 503)
        finally:
            server.shutdown()
            thread.join()
            server.server_close()


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

    def capture_ffmpeg(self):
        commands = []
        run = titan_film.run

        def capture(*args, **kwargs):
            if args[0] == 'ffmpeg':
                commands.append(args)
            return run(*args, **kwargs)

        return commands, capture

    def test_ingest_hash_dedupe_and_proxy(self):
        original = digest_file(self.src)
        a = self.studio.ingest(self.src)
        self.assertEqual(a['sha256'], original)
        self.assertEqual(self.studio.ingest(self.src)['mediaId'], a['mediaId'])
        self.assertEqual(len(self.studio.list_assets()), 1)
        commands, capture = self.capture_ffmpeg()
        with patch('titan_film.run', side_effect=capture):
            p = self.studio.proxy(a['mediaId'])
        self.assert_protocol_allowlist(commands, {'file,pipe'})
        self.assertEqual(p['status'], 'PROXY_READY_PRIVATE')
        self.assertTrue((self.studio.root / 'cache' / a['mediaId'] / 'contact.png').exists())
        self.assertEqual(digest_file(self.src), original)

    def test_render_and_reject_out_of_bounds(self):
        x = self.studio.ingest(self.src)
        edl = {'schema': SCHEMA, 'cuts': [{'mediaId': x['mediaId'], 'startSeconds': 0.4,
                                           'endSeconds': 1.3, 'effect': 'stressShake'},
                                          {'mediaId': x['mediaId'], 'startSeconds': 1.5,
                                           'endSeconds': 2.5, 'effect': 'hardMono'}]}
        commands, capture = self.capture_ffmpeg()
        with patch('titan_film.run', side_effect=capture):
            rendered = self.studio.render(edl)
        self.assert_protocol_allowlist(commands, {'file,pipe', 'concat,file,pipe'})
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

    def test_authenticated_upload_probes_extensionless_temporary_file(self):
        token = 'private-test-token-with-at-least-24-chars'
        server = ThreadingHTTPServer(('127.0.0.1', 0), titan_film.make_handler(self.studio, token))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            request = urllib.request.Request(
                f'http://127.0.0.1:{server.server_port}/api/ingest',
                data=self.src.read_bytes(),
                headers={'Authorization': 'Bearer ' + token, 'X-Filename': 'clip.mp4',
                         'Content-Type': 'application/octet-stream'})
            with urllib.request.urlopen(request) as response:
                result = json.load(response)
            self.assertEqual(result['status'], 'CACHED_LOCAL_WORKING_COPY')
            self.assertEqual(len(self.studio.list_assets()), 1)
            self.assertEqual([path.suffix for path in (self.studio.root / 'imports').iterdir()],
                             ['.mp4'])
        finally:
            server.shutdown()
            thread.join()
            server.server_close()

    def assert_protocol_allowlist(self, commands, allowed):
        self.assertTrue(commands)
        for command in commands:
            input_index = command.index('-i')
            self.assertLess(command.index('-protocol_whitelist'), input_index)
            self.assertIn(command[command.index('-protocol_whitelist') + 1], allowed)

    def test_no_media_or_filename_escape(self):
        with self.assertRaises(ValueError): self.studio.ingest(self.src, name='text.txt')
        with self.assertRaises(ValueError): self.studio.media('../../etc/passwd')
        with self.assertRaises(ValueError): self.studio.render({'schema': SCHEMA, 'cuts': []})

if __name__ == '__main__': unittest.main()

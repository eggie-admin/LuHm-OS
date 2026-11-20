#!/usr/bin/env python3
"""Operation Titan 7: private, explicit FFmpeg media ingest and edit workbench.

Standard-library-only control plane. FFmpeg/ffprobe are subprocess tools.
Files on Drive are authoritative; cached imports are only working copies.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import math
import os
from pathlib import Path
import re
import secrets
import shutil
import sqlite3
import subprocess
import tempfile
import threading
from urllib.parse import unquote, urlparse

HERE = Path(__file__).resolve().parent
FORMATS = {'.mp4', '.mov', '.mkv', '.webm', '.m4v', '.avi'}
MAX_UPLOAD_BYTES = 500_000_000
MAX_TOTAL_MEDIA_BYTES = 2_000_000_000
MAX_GENERATED_FILE_BYTES = 256_000_000
SCHEMA = 'pirateDaddyFilm.edl.v1'
MEDIA_ID = re.compile(r'^[a-f0-9]{24}$')
ALLOWED_EFFECTS = {'none', 'stressShake', 'hardMono'}


class ProcessingBusyError(RuntimeError):
    pass


def input_args(path: Path, protocols: str = 'file,pipe') -> tuple[str, ...]:
    return ('-protocol_whitelist', protocols, '-i', str(path))


def digest_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def run(*cmd: str, timeout: int = 240) -> subprocess.CompletedProcess:
    return subprocess.run(list(cmd), check=True, capture_output=True, text=True, timeout=timeout)


def probe(path: Path) -> dict:
    data = json.loads(run('ffprobe', '-protocol_whitelist', 'file,pipe', '-v', 'error',
                          '-show_format', '-show_streams', '-of', 'json', '-i', str(path)).stdout)
    video = next((s for s in data.get('streams', []) if s.get('codec_type') == 'video'), None)
    if not video:
        raise ValueError('No video stream found; media rejected')
    duration = float(data['format'].get('duration', video.get('duration', 0)))
    if not 0 < duration < 86400:
        raise ValueError('Media duration unavailable or invalid')
    return {'durationSeconds': duration, 'width': int(video.get('width', 0)),
            'height': int(video.get('height', 0)), 'codec': video.get('codec_name', 'unknown'),
            'hasAudio': any(s.get('codec_type') == 'audio' for s in data['streams'])}


class Studio:
    def __init__(self, root: Path):
        self.root = root.expanduser().resolve()
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        for folder in ('imports', 'cache', 'exports'):
            (self.root / folder).mkdir(exist_ok=True, mode=0o700)
        self.db = self.root / 'titan.sqlite3'
        self.processing_lock = threading.BoundedSemaphore(1)
        with self.connection() as conn:
            conn.executescript('''
              CREATE TABLE IF NOT EXISTS media_assets (
                media_id TEXT PRIMARY KEY, basename TEXT NOT NULL, sha256 TEXT NOT NULL UNIQUE,
                extension TEXT NOT NULL, size_bytes INTEGER NOT NULL,
                duration_seconds REAL NOT NULL, width INTEGER NOT NULL, height INTEGER NOT NULL,
                codec TEXT NOT NULL, has_audio INTEGER NOT NULL, state TEXT NOT NULL DEFAULT 'CACHED_LOCAL',
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
              );
              CREATE TABLE IF NOT EXISTS render_receipts (
                render_id TEXT PRIMARY KEY, edl_sha256 TEXT NOT NULL,
                output_sha256 TEXT NOT NULL, output_name TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
              );
            ''')

    def connection(self):
        return sqlite3.connect(self.db, timeout=30)

    def storage_bytes(self) -> int:
        return sum(path.stat().st_size for folder in ('imports', 'cache', 'exports')
                   for path in (self.root / folder).rglob('*')
                   if not path.is_symlink() and path.is_file())

    def ensure_storage_capacity(self, additional_bytes: int = 0):
        if additional_bytes < 0 or self.storage_bytes() + additional_bytes > MAX_TOTAL_MEDIA_BYTES:
            raise ValueError('Total working media/cache storage limit reached')

    @contextmanager
    def processing_job(self):
        if not self.processing_lock.acquire(blocking=False):
            raise ProcessingBusyError('Media processing is busy; retry when the current job completes')
        try:
            yield
        finally:
            self.processing_lock.release()

    def ingest(self, source: Path, name: str | None = None) -> dict:
        source = source.expanduser().resolve(strict=True)
        if not source.is_file():
            raise ValueError('Source must be a regular file')
        basename = Path(name or source.name).name
        ext = Path(basename).suffix.lower()
        if ext not in FORMATS:
            raise ValueError('Unsupported video extension')
        size = source.stat().st_size
        if not 0 < size <= MAX_UPLOAD_BYTES:
            raise ValueError('File exceeds the bounded single-file intake limit')
        digest = digest_file(source)
        media_id = digest[:24]
        dest = self.root / 'imports' / (media_id + ext)
        if not dest.exists():
            self.ensure_storage_capacity(size)
        facts = probe(source)
        if not dest.exists():
            with tempfile.NamedTemporaryFile(dir=dest.parent, delete=False) as tmp:
                temp_path = Path(tmp.name)
            try:
                shutil.copyfile(source, temp_path)
                if digest_file(temp_path) != digest:
                    raise ValueError('Working copy failed hash verification')
                os.replace(temp_path, dest)
            finally:
                temp_path.unlink(missing_ok=True)
        with self.connection() as conn:
            conn.execute('INSERT OR IGNORE INTO media_assets '
                         '(media_id,basename,sha256,extension,size_bytes,duration_seconds,width,height,codec,has_audio) '
                         'VALUES (?,?,?,?,?,?,?,?,?,?)',
                         (media_id, basename, digest, ext, size, facts['durationSeconds'], facts['width'],
                          facts['height'], facts['codec'], int(facts['hasAudio'])))
        return {'mediaId': media_id, 'basename': basename, 'sha256': digest,
                'sizeBytes': size, 'status': 'CACHED_LOCAL_WORKING_COPY', **facts}

    def list_assets(self) -> list[dict]:
        with self.connection() as conn:
            rows = conn.execute('SELECT media_id,basename,sha256,size_bytes,duration_seconds,width,height,has_audio,state '
                                'FROM media_assets ORDER BY created_at DESC, basename').fetchall()
        keys = ('mediaId', 'basename', 'sha256', 'sizeBytes', 'durationSeconds', 'width', 'height', 'hasAudio', 'state')
        return [dict(zip(keys, r)) for r in rows]

    def media(self, media_id: str) -> tuple[Path, float]:
        if not MEDIA_ID.fullmatch(media_id):
            raise ValueError('Invalid media ID')
        with self.connection() as conn:
            row = conn.execute('SELECT extension,duration_seconds FROM media_assets WHERE media_id=?', (media_id,)).fetchone()
        if not row:
            raise ValueError('Unknown registered media ID')
        path = self.root / 'imports' / (media_id + row[0])
        if not path.is_file():
            raise ValueError('Working copy missing; reingest from original Drive master')
        return path, float(row[1])

    def proxy(self, media_id: str, seconds: int = 300) -> dict:
        src, duration = self.media(media_id)
        self.ensure_storage_capacity(MAX_GENERATED_FILE_BYTES)
        target = self.root / 'cache' / media_id
        target.mkdir(exist_ok=True)
        preview = target / 'proxy.mp4'
        sheet = target / 'contact.png'
        with tempfile.TemporaryDirectory(dir=target) as scratch:
            p = Path(scratch) / 'proxy.mp4'
            run('ffmpeg', '-nostdin', '-hide_banner', '-loglevel', 'error', '-y',
                *input_args(src),
                '-t', str(min(seconds, 300)), '-vf', 'scale=480:-2,fps=24', '-an',
                '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '29', '-pix_fmt', 'yuv420p',
                '-movflags', '+faststart', '-fs', str(MAX_GENERATED_FILE_BYTES), str(p), timeout=600)
            if not probe(p)['durationSeconds']:
                raise ValueError('Empty proxy')
            os.replace(p, preview)
        frame_count = max(1, min(20, math.ceil(min(duration, seconds) / 8)))
        self.ensure_storage_capacity(MAX_GENERATED_FILE_BYTES)
        run('ffmpeg', '-nostdin', '-hide_banner', '-loglevel', 'error', '-y',
            *input_args(preview),
            '-vf', f'select=not(mod(n\\,192)),scale=160:90,tile=layout=5x4:nb_frames={frame_count}:padding=3:margin=3', '-frames:v', '1',
            '-fs', str(MAX_GENERATED_FILE_BYTES), str(sheet), timeout=120)
        return {'mediaId': media_id, 'proxySha256': digest_file(preview),
                'contactSha256': digest_file(sheet), 'secondsCached': min(duration, seconds),
                'status': 'PROXY_READY_PRIVATE'}

    def render(self, edl: dict) -> dict:
        if not isinstance(edl, dict) or edl.get('schema') != SCHEMA:
            raise ValueError('Expected pirateDaddyFilm.edl.v1 JSON')
        cuts = edl.get('cuts')
        if not isinstance(cuts, list) or not 1 <= len(cuts) <= 24:
            raise ValueError('EDL requires between one and 24 cuts')
        normalized = []
        total = 0.0
        for c in cuts:
            if not isinstance(c, dict):
                raise ValueError('Every cut must be an object')
            src, duration = self.media(c.get('mediaId', ''))
            start, end = float(c.get('startSeconds', -1)), float(c.get('endSeconds', -1))
            if not 0 <= start < end <= duration + 0.04:
                raise ValueError('Cut is outside media duration')
            length = end - start
            if length < 0.09 or length > 120:
                raise ValueError('Each cut must be 0.09 to 120 seconds')
            effect = c.get('effect', 'none')
            if effect not in ALLOWED_EFFECTS:
                raise ValueError('Unknown effect preset; allowlist only')
            total += length
            normalized.append((src, start, length, effect))
        if total > 600:
            raise ValueError('Total rough-cut duration exceeds 10 minutes')
        encoded = json.dumps(edl, sort_keys=True, separators=(',', ':')).encode('utf-8')
        edl_hash = hashlib.sha256(encoded).hexdigest()
        render_id = secrets.token_hex(12)
        output = self.root / 'exports' / (render_id + '.mp4')
        with tempfile.TemporaryDirectory(dir=self.root / 'exports') as scratch:
            scratch = Path(scratch)
            segments = []
            for idx, (src, start, length, effect) in enumerate(normalized):
                self.ensure_storage_capacity(MAX_GENERATED_FILE_BYTES)
                segment = scratch / f'part_{idx:02d}.mp4'
                vf = ('scale=540:960:force_original_aspect_ratio=decrease,'
                      'pad=540:960:(ow-iw)/2:(oh-ih)/2:color=black')
                if effect == 'stressShake':
                    vf += ",crop=520:940:x='10+5*sin(t*33)':y='10+6*sin(t*27)',scale=540:960"
                elif effect == 'hardMono':
                    vf += ',hue=s=0,eq=contrast=1.28:brightness=-0.03'
                vf += ',fps=24'
                run('ffmpeg', '-nostdin', '-hide_banner', '-loglevel', 'error', '-y',
                    '-ss', f'{start:.6f}', *input_args(src), '-t', f'{length:.6f}',
                    '-vf', vf,
                    '-an', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '27',
                    '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
                    '-fs', str(MAX_GENERATED_FILE_BYTES), str(segment), timeout=300)
                segments.append(segment)
            concat = scratch / 'concat.txt'
            concat.write_text(''.join(f"file 'part_{i:02d}.mp4'\n" for i in range(len(segments))), encoding='utf-8')
            self.ensure_storage_capacity(MAX_GENERATED_FILE_BYTES)
            candidate = scratch / 'preview.mp4'
            run('ffmpeg', '-nostdin', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'concat',
                '-safe', '0', *input_args(concat, 'concat,file,pipe'), '-c', 'copy',
                '-movflags', '+faststart', '-fs', str(MAX_GENERATED_FILE_BYTES), str(candidate))
            details = probe(candidate)
            if not (details['width'] == 540 and details['height'] == 960):
                raise ValueError('Output frame mismatch')
            shutil.move(str(candidate), str(output))
        output_hash = digest_file(output)
        with self.connection() as conn:
            conn.execute('INSERT INTO render_receipts (render_id,edl_sha256,output_sha256,output_name) '
                         'VALUES (?,?,?,?)', (render_id, edl_hash, output_hash, output.name))
        receipt = {'renderId': render_id, 'outputName': output.name,
                   'outputSha256': output_hash, 'edlSha256': edl_hash,
                   'durationSeconds': details['durationSeconds'], 'width': 540, 'height': 960,
                   'audio': 'SILENT_ROUGH_CUT_ONLY', 'state': 'PRIVATE_REVIEW_CANDIDATE'}
        (self.root / 'exports' / (render_id + '.receipt.json')).write_text(json.dumps(receipt, indent=2) + '\n')
        return receipt


def make_handler(studio: Studio, token: str):
    class Handler(BaseHTTPRequestHandler):
        def send_json(self, status: int, obj: dict | list):
            data = json.dumps(obj).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def send_file(self, path: Path, mime: str, filename: str | None = None):
            self.send_response(200)
            self.send_header('Content-Type', mime)
            self.send_header('Content-Length', str(path.stat().st_size))
            self.send_header('Cache-Control', 'no-store')
            if filename:
                self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
            self.end_headers()
            with path.open('rb') as f:
                for chunk in iter(lambda: f.read(1024 * 1024), b''):
                    try:
                        self.wfile.write(chunk)
                    except (BrokenPipeError, ConnectionResetError):
                        break

        def authorized(self) -> bool:
            candidate = self.headers.get('Authorization', '')
            return secrets.compare_digest(candidate, 'Bearer ' + token)

        def do_GET(self):
            path = urlparse(self.path).path
            if path == '/':
                raw = (HERE / 'web' / 'index.html').read_bytes()
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(raw)))
                self.send_header('Cache-Control', 'no-store')
                self.end_headers()
                self.wfile.write(raw)
                return
            if path == '/healthz':
                self.send_json(200, {'state': 'LOCAL_WORKER_PRESENT', 'publicPublishing': False})
                return
            if not self.authorized():
                self.send_json(401, {'error': 'Bearer token required'})
                return
            if path == '/api/assets':
                self.send_json(200, {'assets': studio.list_assets()})
                return
            if path.startswith('/api/export/'):
                render_id = path[len('/api/export/'): ]
                if not MEDIA_ID.fullmatch(render_id):
                    self.send_json(400, {'error': 'Invalid render ID'}); return
                with studio.connection() as conn:
                    row = conn.execute('SELECT output_name FROM render_receipts WHERE render_id=?', (render_id,)).fetchone()
                if not row:
                    self.send_json(404, {'error': 'Unknown render ID'}); return
                file = studio.root / 'exports' / row[0]
                if not file.is_file():
                    self.send_json(404, {'error': 'Output not found'}); return
                self.send_file(file, 'video/mp4', filename='Reaper_Rough_Cut_'+render_id+'.mp4')
                return
            for prefix, suffix, mime in (('/api/proxy/', 'proxy.mp4', 'video/mp4'),
                                          ('/api/contact/', 'contact.png', 'image/png')):
                if path.startswith(prefix):
                    id_ = path[len(prefix):]
                    if not MEDIA_ID.fullmatch(id_):
                        self.send_json(400, {'error': 'Invalid ID'}); return
                    file = studio.root / 'cache' / id_ / suffix
                    if not file.is_file():
                        self.send_json(404, {'error': 'Cache not generated'}); return
                    self.send_file(file, mime)
                    return
            self.send_json(404, {'error': 'Unknown route'})

        def do_POST(self):
            if not self.authorized():
                self.send_json(401, {'error': 'Unauthorized'}); return
            try:
                with studio.processing_job():
                    self.handle_post()
            except ProcessingBusyError:
                self.send_json(503, {'error': 'Media processing is busy; retry later'})

        def handle_post(self):
            if not self.authorized():
                self.send_json(401, {'error': 'Bearer token required'}); return
            path = urlparse(self.path).path
            try:
                size = int(self.headers.get('Content-Length', '0'))
                if not 0 < size <= MAX_UPLOAD_BYTES:
                    raise ValueError('Invalid or over-limit body length')
                if path == '/api/ingest':
                    name = unquote(self.headers.get('X-Filename', 'incoming.mp4'))
                    suffix = Path(name).suffix.lower()
                    if suffix not in FORMATS:
                        raise ValueError('Unsupported input extension')
                    studio.ensure_storage_capacity(size)
                    with tempfile.NamedTemporaryFile(dir=studio.root / 'imports', suffix=suffix, delete=False) as temp:
                        temp_path = Path(temp.name)
                        remaining = size
                        while remaining:
                            chunk = self.rfile.read(min(1024*1024, remaining))
                            if not chunk: raise ValueError('Truncated upload')
                            temp.write(chunk); remaining -= len(chunk)
                    try:
                        result = studio.ingest(temp_path, name=name)
                    finally:
                        temp_path.unlink(missing_ok=True)
                elif path in ('/api/proxy', '/api/render'):
                    if size > 128_000: raise ValueError('JSON body exceeds limit')
                    data = json.loads(self.rfile.read(size))
                    result = studio.proxy(data['mediaId']) if path == '/api/proxy' else studio.render(data)
                else:
                    self.send_json(404, {'error': 'Unknown route'}); return
                self.send_json(200, result)
            except (ValueError, KeyError, TypeError, json.JSONDecodeError) as err:
                self.send_json(400, {'error': str(err)})
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as err:
                self.send_json(422, {'error': 'Media processing failed', 'type': type(err).__name__})

        def log_message(self, fmt, *args):
            # Do not log bearer tokens, filenames, URL query strings, or private edits.
            pass
    return Handler


def main():
    parser = argparse.ArgumentParser(description='Titan7 local-first video workbench')
    parser.add_argument('--root', type=Path, default=Path(os.getenv('TITAN_MEDIA_ROOT', '~/.local/share/luhm/titan-film')))
    sub = parser.add_subparsers(dest='command', required=True)
    ingest = sub.add_parser('ingest'); ingest.add_argument('file', type=Path)
    proxy_cmd = sub.add_parser('proxy'); proxy_cmd.add_argument('media_id')
    render = sub.add_parser('render'); render.add_argument('edl', type=Path)
    sub.add_parser('list')
    serve = sub.add_parser('serve'); serve.add_argument('--bind', default='127.0.0.1'); serve.add_argument('--port', type=int, default=8786)
    args = parser.parse_args()
    st = Studio(args.root)
    if args.command == 'ingest': out = st.ingest(args.file)
    elif args.command == 'proxy': out = st.proxy(args.media_id)
    elif args.command == 'render': out = st.render(json.loads(args.edl.read_text()))
    elif args.command == 'list': out = st.list_assets()
    else:
        if args.bind not in ('127.0.0.1', '::1', '0.0.0.0'):
            parser.error('Explicit network binding required')
        token = os.getenv('TITAN_TOKEN', '')
        if len(token) < 24:
            parser.error('TITAN_TOKEN must be configured with at least 24 characters')
        print('Listening on http://' + args.bind + ':' + str(args.port) + ' (API requires token)', flush=True)
        ThreadingHTTPServer((args.bind, args.port), make_handler(st, token)).serve_forever()
        return
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()

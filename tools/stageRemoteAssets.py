#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def download_gdrive(drive_id: str, out: Path, max_bytes: int) -> None:
    urls = [
        f'https://drive.usercontent.google.com/download?id={drive_id}&export=download&confirm=t',
        f'https://drive.google.com/uc?export=download&id={drive_id}&confirm=t',
    ]
    last_error = None
    for url in urls:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'LuHmOS-CI/1.0'})
            with urllib.request.urlopen(req, timeout=60) as response, out.open('wb') as fh:
                total = 0
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > max_bytes:
                        raise RuntimeError(f'remote archive exceeded maxDownloadBytes={max_bytes}')
                    fh.write(chunk)
            if out.stat().st_size:
                return
        except Exception as exc:
            last_error = exc
            out.unlink(missing_ok=True)
    raise RuntimeError(f'asset download failed: {last_error}')


def ensure_relative_repo_path(value: str, required_prefix: str | None = None) -> Path:
    p = Path(value)
    if p.is_absolute() or '..' in p.parts:
        raise RuntimeError(f'unsafe path: {value}')
    if required_prefix and (not p.parts or p.parts[0] != required_prefix):
        raise RuntimeError(f'path must stay under {required_prefix}/: {value}')
    return ROOT / p


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest', required=True)
    args = parser.parse_args()

    manifest_path = ensure_relative_repo_path(args.manifest)
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    if manifest.get('schema') != 'luhm-os.remote-asset-pack.v1':
        raise RuntimeError('unexpected asset manifest schema')
    if manifest.get('transport') != 'google_drive':
        raise RuntimeError('unsupported transport')

    members = manifest.get('members') or []
    if not members:
        raise RuntimeError('asset manifest has no members')

    jar_out = ensure_relative_repo_path(manifest['jarOutput'], 'build')
    jar_out.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix='luhm-assets-') as tmp_dir:
        tmp = Path(tmp_dir)
        archive = tmp / 'remote-assets.zip'
        download_gdrive(manifest['driveId'], archive, int(manifest['maxDownloadBytes']))

        actual_archive_sha = sha256_file(archive)
        expected_archive_sha = manifest['archiveSha256'].lower()
        if actual_archive_sha != expected_archive_sha:
            raise RuntimeError(f'archive SHA mismatch: {actual_archive_sha} != {expected_archive_sha}')

        staged = []
        with zipfile.ZipFile(archive) as zf:
            selected_total = 0
            for item in members:
                member_name = item['archivePath']
                try:
                    info = zf.getinfo(member_name)
                except KeyError as exc:
                    raise RuntimeError(f'missing expected member: {member_name}') from exc
                selected_total += info.file_size
                if selected_total > int(manifest['maxSelectedUncompressedBytes']):
                    raise RuntimeError('selected remote assets exceed maxSelectedUncompressedBytes')
                mode = (info.external_attr >> 16) & 0o170000
                if mode == 0o120000:
                    raise RuntimeError(f'symlink member rejected: {member_name}')
                data = zf.read(info)
                digest = hashlib.sha256(data).hexdigest()
                if digest != item['sha256'].lower():
                    raise RuntimeError(f'member SHA mismatch for {member_name}')
                output_rel = Path(item['output'])
                if output_rel.is_absolute() or '..' in output_rel.parts or not output_rel.parts or output_rel.parts[0] != 'assets':
                    raise RuntimeError(f'unsafe staged output: {output_rel}')
                temp_output = tmp / output_rel
                temp_output.parent.mkdir(parents=True, exist_ok=True)
                temp_output.write_bytes(data)
                staged.append((output_rel, temp_output))

        with zipfile.ZipFile(jar_out, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as jar:
            for output_rel, temp_output in staged:
                jar.write(temp_output, arcname=output_rel.as_posix())

        # Re-open the normalized JAR and stage only its verified asset paths into the project.
        with zipfile.ZipFile(jar_out) as jar:
            for output_rel, _ in staged:
                data = jar.read(output_rel.as_posix())
                target = ROOT / output_rel
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)

    report = {
        'manifest': args.manifest,
        'archiveSha256': expected_archive_sha,
        'jar': str(jar_out.relative_to(ROOT)),
        'jarBytes': jar_out.stat().st_size,
        'members': [
            {
                'output': item['output'],
                'sha256': item['sha256'],
                'bytes': (ROOT / item['output']).stat().st_size,
            }
            for item in members
        ],
    }
    report_path = ROOT / 'build/remote-assets/stage-report.json'
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()

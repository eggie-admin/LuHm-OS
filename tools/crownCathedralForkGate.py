#!/usr/bin/env python3
"""Fail-closed, reproducible source-only Ash Cathedral fork package.

This tool does not approve or publish art, change global Canon, or create releases.
"""
import argparse
import hashlib
import json
import re
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / 'plugins/luhm-os/skills/premonition-combat-studio/assets/godot'
PREFIX = 'ash-cathedral/'
FILES = (
    '.gitignore',
    'Main.tscn',
    'README.md',
    'project.godot',
    'scripts/arena.gd',
    'scripts/arena.gd.uid',
    'tests/hardening.gd',
    'tests/smoke.gd',
)
BLOCKED_MARKERS = (
    '-----BEGIN PRIVATE KEY-----',
    'github_pat_',
    'ghp_',
    'sk-proj-',
    'drive.usercontent.google.com',
    'drive.google.com/uc',
    'Meshy_AI_Lum_Midnight_1996_biped',
)
NOTICE = """# Crown Cathedral / Ash Cathedral source fork

This package contains GPL-3.0-covered source and procedural gameplay placeholders only.
The GPL-3.0 text is included as LICENSE; review third-party obligations before
redistributing modifications. No original protected character art, Live2D masters,
3D character rigs, private HTML source, audio, private Drive assets, signing keys,
or commercial third-party game assets are licensed or distributed by this package.

Open project.godot in a compatible Godot 4.6 editor. Run the supplied tests.
This is a reviewable prototype, not a signed APK, hosted ChatGPT runtime, or
full Crown Cathedral production release.
"""


def digest(data):
    return hashlib.sha256(data).hexdigest()


def checked_sources(root=ROOT):
    demo = root / DEMO.relative_to(ROOT)
    selected = {}
    for rel in FILES:
        path = demo / rel
        if path.is_symlink() or not path.is_file():
            raise ValueError(f'blocked: missing/symlink source: {rel}')
        if path.stat().st_size > 1_000_000:
            raise ValueError(f'blocked: oversized source: {rel}')
        data = path.read_bytes()
        try:
            content = data.decode('utf-8')
        except UnicodeDecodeError as exc:
            raise ValueError(f'blocked: non-text payload: {rel}') from exc
        for marker in BLOCKED_MARKERS:
            if marker in content:
                raise ValueError(f'blocked: private material marker: {rel}')
        selected[rel] = data
    for rel, data in selected.items():
        source = data.decode('utf-8')
        for ref in re.findall(r'res://([A-Za-z0-9_./-]+)', source):
            if ref not in selected:
                raise ValueError(f'blocked: out-of-package resource {ref} in {rel}')
    license_file = root / 'LICENSE'
    if license_file.is_symlink() or not license_file.is_file():
        raise ValueError('blocked: source GPL license missing')
    license_text = license_file.read_bytes()
    if b'GNU GENERAL PUBLIC LICENSE' not in license_text:
        raise ValueError('blocked: missing GPL license text')
    selected['LICENSE'] = license_text
    selected['FORK_NOTICES.md'] = NOTICE.encode('utf-8')
    return selected


def expected(root=ROOT):
    selected = checked_sources(root)
    entries = {PREFIX + path: data for path, data in selected.items()}
    manifest = {
        'schema': 'luhmOs.crownCathedralForkReceipt.v1',
        'scope': 'sourceOnlyProceduralPlaceholderDemo',
        'license': 'GPL-3.0',
        'protectedArtIncluded': False,
        'fullPublicReleaseGreen': False,
        'files': {key: digest(value) for key, value in sorted(entries.items())},
    }
    entries[PREFIX + 'SOURCE_MANIFEST.json'] = (json.dumps(manifest, sort_keys=True, indent=2) + '\n').encode()
    return entries


def package(path, root=ROOT):
    entries = expected(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for rel, data in sorted(entries.items()):
            info = zipfile.ZipInfo(rel, date_time=(2020, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    verify(path, root)
    path.with_suffix(path.suffix + '.sha256').write_text(f'{digest(path.read_bytes())}  {path.name}\n')
    return path


def verify(path, root=ROOT):
    entries = expected(root)
    with zipfile.ZipFile(path, 'r') as z:
        names = z.namelist()
        if len(names) != len(set(names)) or set(names) != set(entries):
            raise ValueError('blocked: archive has missing, duplicate or unapproved entries')
        for name in names:
            info = z.getinfo(name)
            if info.is_dir() or info.file_size > 1_000_000:
                raise ValueError(f'blocked: non-file/oversized entry {name}')
            if z.read(name) != entries[name]:
                raise ValueError(f'blocked: source mismatch for {name}')
    print('GREEN_SCOPED_FORK_SOURCE_FIREWALL', digest(path.read_bytes()))


def self_test():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        root = tmp / 'fixture'
        base = root / DEMO.relative_to(ROOT)
        base.mkdir(parents=True)
        for file in FILES:
            dest = base / file
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text('test\n')
        (root / 'LICENSE').write_text('GNU GENERAL PUBLIC LICENSE\n')
        archive = tmp / 'candidate.zip'
        package(archive, root)
        (root / 'private-art').mkdir()
        (root / 'private-art' / 'master.psd').write_text('confidential')
        verify(archive, root)
        with zipfile.ZipFile(archive, 'a') as z:
            z.writestr('ash-cathedral/private-art/master.psd', 'confidential')
        try:
            verify(archive, root)
        except ValueError:
            pass
        else:
            raise AssertionError('negative test failed: private file leaked into package')
        (base / 'Main.tscn').write_text('load("res://private-art/master.psd")')
        try:
            expected(root)
        except ValueError:
            pass
        else:
            raise AssertionError('negative test failed: out-of-package resource allowed')
    print('GREEN_FORK_NEGATIVE_CONTROLS')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, help='write reviewed source ZIP')
    parser.add_argument('--verify', type=Path, help='verify exact archive against checkout')
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        self_test()
    if args.output:
        print('BUILT_SCOPED_SOURCE_FORK', package(args.output))
    if args.verify:
        verify(args.verify)
    if not (args.self_test or args.output or args.verify):
        parser.error('provide --self-test, --output, or --verify')


if __name__ == '__main__':
    main()

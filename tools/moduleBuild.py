#!/usr/bin/env python3
"""Content-addressed module reuse; APK/signing/final audits are never cached."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
NATIVE_INPUTS = ['native/kaiwebview', 'cockpit', 'addons/kai_webview', 'tools/moduleBuild.py', 'scripts/buildNativeWebglass.sh', 'scripts/buildCathedralWebglass.sh', 'scripts/buildCathedralReleaseCandidate.sh', 'project.godot', 'export_presets.cfg']
OUTPUTS = ['kaiwebview-debug.aar', 'kaiwebview-release.aar']
TOOLCHAIN = 'godot=4.7.2;java=17;android=36;build-tools=36.1.0;node=24;cache-format=1'

def fingerprint(root=ROOT):
    names = subprocess.check_output(['git', 'ls-files', '-z', '--', *NATIVE_INPUTS], cwd=root).decode().split('\0')
    digest = hashlib.sha256(TOOLCHAIN.encode())
    for name in sorted(filter(None, names)):
        path = root / name
        if path.is_symlink():
            raise ValueError('Symlink input forbidden: ' + name)
        digest.update(name.encode() + b'\0' + path.read_bytes() + b'\0')
    return digest.hexdigest()

def restore(cache, destination, key):
    try:
        receipt = json.loads((cache / 'receipt.json').read_text())
        if receipt['input_sha256'] != key or set(receipt['outputs']) != set(OUTPUTS):
            return False
        for name in OUTPUTS:
            path = cache / name
            if path.is_symlink() or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != receipt['outputs'][name]:
                return False
    except (OSError, ValueError, KeyError, TypeError):
        return False
    destination.mkdir(parents=True, exist_ok=True)
    for name in OUTPUTS:
        shutil.copyfile(cache / name, destination / name)
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['key', 'restore', 'save'])
    args = parser.parse_args()
    key = fingerprint()
    if args.action == 'key':
        print(key)
        return 0
    cache = ROOT / '.luhm-cache' / 'nativeWebglass' / key
    destination = ROOT / 'addons/kai_webview/bin'
    if args.action == 'restore':
        hit = restore(cache, destination, key)
        print('NATIVE_WEBGLASS_CACHE=' + ('VERIFIED_HIT' if hit else 'MISS'))
        return 0 if hit else 1
    cache.mkdir(parents=True, exist_ok=True)
    outputs = {}
    for name in OUTPUTS:
        data = (destination / name).read_bytes()
        if not data:
            raise ValueError('Empty native module')
        shutil.copyfile(destination / name, cache / name)
        outputs[name] = hashlib.sha256(data).hexdigest()
    (cache / 'receipt.json').write_text(json.dumps({'input_sha256': key, 'outputs': outputs, 'toolchain': TOOLCHAIN}, indent=2)+'\n')
    print('NATIVE_WEBGLASS_CACHE=SAVED')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())

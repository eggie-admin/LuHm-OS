"""Fail-closed source and final APK checks for the offline Samsung candidate."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = re.compile(r'127\.0\.0\.1|localhost|FastAPI|PySimpleGUI|RUN_COMMAND|OPENAI_API_KEY|AIza|sk-proj-|cms_registry|api_bridge|web_cms_bridge|cage_manager|HTTPRequest|MANIFEST_URL|SpringBoneSimulator3D|FaceController|LipSyncController')
RUNTIME_SCOPE = {
    'scripts': {'.gd'},
    'scenes': {'.tscn', '.tres'},
    'cutscenes': {'.json'},
}

def require(ok, message):
    if not ok:
        raise ValueError(message)

def scan_runtime(root):
    files = []
    for name, extensions in RUNTIME_SCOPE.items():
        folder = root / name
        require(folder.is_dir(), f'missing runtime directory: {name}')
        files.extend(
            p for p in folder.rglob('*')
            if p.is_file() and p.suffix.lower() in extensions
        )
    require(bool(files), 'empty runtime scope')
    for p in files:
        require(not p.is_symlink(), f'symlink in runtime: {p.name}')
        content = p.read_text(encoding='utf-8')
        require(not FORBIDDEN.search(content), f'forbidden runtime capability in {p.relative_to(root)}')

def source(root):
    scan_runtime(root)
    contract = json.loads((root / 'doctrine/androidCandidate.json').read_text())
    require(len((root / 'scripts/main.gd').read_text().splitlines()) <= 150, 'main orchestration exceeds approved scope')
    for path, marker in {
        'scripts/game/neonWorld.gd':'StaticBody3D',
        'scripts/game/playerController.gd':'SpringArm3D',
        'scripts/game/lumAvatar.gd':'get_rig_summary',
        'scripts/game/bodyProportionModifier.gd':'SkeletonModifier3D',
        'scripts/game/characterCreatorRuntime.gd':'avatar_tune_requested',
        'scripts/cutsceneDirector.gd':'CANCEL_POLL_SECONDS',
        'frontEnd/jquery/luhm.cockpit.js':'luhmCockpit'
    }.items():
        require(marker in (root / path).read_text(), f'missing architecture contract: {path}')
    preset = (root / 'export_presets.cfg').read_text()
    expected = [f'package/unique_name="{contract["package"]}"', f'version/code={contract["versionCode"]}',
                f'version/name="{contract["versionName"]}"', 'gradle_build/min_sdk="24"',
                'gradle_build/target_sdk="36"', 'architectures/arm64-v8a=true', 'permissions/internet=false']
    for value in expected:
        require(preset.splitlines().count(value) == 1, f'export contract mismatch: {value}')
    for abi in ('armeabi-v7a', 'x86', 'x86_64'):
        require(f'architectures/{abi}=false' in preset, f'unexpected ABI {abi}')
    require('permissions/custom_permissions=PackedStringArray()' in preset, 'unexpected custom permissions')
    sequence = json.loads((root / 'cutscenes/lumBeaconIntro.json').read_text())['beats']
    require([x['type'] for x in sequence] == ['lock_player', 'camera_move', 'lum_beacon_pulse', 'dialogue', 'restore'], 'cutscene contract mismatch')
    require(sequence[3]['event'] == 'lum_beacon_linked', 'cutscene event mismatch')
    print('SOURCE CONTRACT AND RUNTIME BOUNDARY PASS')

def elf_alignment(data):
    require(data[:6] == b'\x7fELF\x02\x01', 'expected little-endian ELF64')
    phoff = struct.unpack_from('<Q', data, 32)[0]
    entsize, count = struct.unpack_from('<HH', data, 54)
    require(entsize >= 56 and count > 0 and phoff + entsize * count <= len(data), 'invalid ELF program headers')
    loads = []
    for i in range(count):
        kind, flags, offset, vaddr, paddr, filesz, memsz, alignment = struct.unpack_from('<IIQQQQQQ', data, phoff + i * entsize)
        if kind == 1:
            require(alignment >= 16384 and alignment & (alignment - 1) == 0, 'ELF LOAD alignment below 16KB or invalid')
            require((vaddr - offset) % 16384 == 0, 'ELF LOAD offset incongruent with 16KB pages')
            loads.append(alignment)
    require(bool(loads), 'ELF has no LOAD segments')
    return loads

def verify_apk(apk, badging, signature, manifest):
    contract = json.loads((ROOT / 'doctrine/androidCandidate.json').read_text())
    for token in (f"package: name='{contract['package']}'", f"versionCode='{contract['versionCode']}'", f"versionName='{contract['versionName']}'", "sdkVersion:'24'", "targetSdkVersion:'36'", "native-code: 'arm64-v8a'"):
        require(token in badging, f'APK metadata mismatch: {token}')
    require(not re.search(r'^uses-permission', badging, re.M), 'offline candidate unexpectedly requests permission')
    require('application-debuggable' in badging, 'candidate debug state differs from declared lane')
    require(not re.search(r'uses-permission', manifest), 'manifest includes permission')
    fingerprint = re.search(r'Signer #1 certificate SHA-256 digest: ([0-9a-fA-F]{64})', signature)
    require(fingerprint is not None, 'missing signer fingerprint')
    libs = {}
    with zipfile.ZipFile(apk) as z:
        names = z.namelist()
        require(len(names) == len(set(names)), 'duplicate ZIP entries')
        for name in names:
            if name.startswith('lib/') and name.endswith('.so'):
                require(name.startswith('lib/arm64-v8a/'), 'unexpected native ABI')
                libs[name] = elf_alignment(z.read(name))
    require(bool(libs), 'APK has no native runtime')
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    require(head == os.environ['CANDIDATE_HEAD'], 'checkout is not exact requested source')
    receipt = {'status': 'AMBER_CI_CANDIDATE_DEVICE_PROOF_PENDING', 'sourceCommit': head,
               'workflowRun': os.environ.get('GITHUB_RUN_ID'), 'contract': contract,
               'apkSha256': hashlib.sha256(apk.read_bytes()).hexdigest(),
               'certificateSha256': fingerprint[1].lower(), 'nativeElfLoadAlignments': libs,
               'assetSha256': {name: hashlib.sha256((ROOT / 'assets/lum' / name).read_bytes()).hexdigest() for name in ('luhm.glb', 'luhmRunning.glb')},
               'persistentSigner': False, 'signatureVerifiedBy': 'apksigner',
               'zipAlignmentVerifiedBy': 'zipalign -c -P 16 -v 4',
               'deviceProof': {'S24FE': 'pending', 'SM-X400': 'pending'},
               'pageSizeRuntimeProof': 'pending', 'promotion': False}
    (apk.parent / 'candidateReceipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--apk', type=Path)
    args = p.parse_args()
    if args.apk:
        folder = args.apk.parent
        verify_apk(args.apk, (folder / 'badging.txt').read_text(), (folder / 'signature.txt').read_text(), (folder / 'manifest.txt').read_text())
    else:
        source(ROOT)

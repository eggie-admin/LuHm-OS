"""Inventory final bytes and add packaged-resource/native checks; never relax size gate."""
import hashlib
import json
from pathlib import Path
import sys
import zipfile
from candidateGate import elf_alignment


def audit(path):
    rows = []
    groups = {}
    with zipfile.ZipFile(path) as apk:
        names = apk.namelist()
        if len(names) != len(set(names)):
            raise ValueError('duplicate ZIP entry names')
        for info in apk.infolist():
            data = apk.read(info)
            sha = hashlib.sha256(data).hexdigest()
            row = {'path': info.filename, 'apkEntryBytes': info.compress_size,
                   'uncompressedBytes': info.file_size, 'sha256': sha}
            if info.filename.endswith('.so'):
                if not info.filename.startswith('lib/arm64-v8a/'):
                    raise ValueError('unexpected native ABI')
                row['elfLoadAlignments'] = elf_alignment(data)
            rows.append(row)
            if info.file_size > 100000:
                groups.setdefault(sha, []).append(info.filename)
        for required in ('assets/doctrine/DOCUMENT_MUTATION_AUDIT_WORKFLOW.json',
                         'assets/doctrine/DOCUMENT_MUTATION_AUDIT_SEAL_20260926.json',
                         'lib/arm64-v8a/libgodot_android.so'):
            if required not in names:
                raise ValueError('required packaged resource missing: ' + required)
        if any(name.startswith('assets/build/') for name in names):
            raise ValueError('build cache leaked into APK')
        textures = [name for name in names if name.endswith('.ctex') and 'lumShared' in name]
        if len(textures) != 1:
            raise ValueError('shared Lum atlas missing or duplicated')
    rows.sort(key=lambda row: row['apkEntryBytes'], reverse=True)
    result = {'apkBytes': path.stat().st_size, 'apkSha256': hashlib.sha256(path.read_bytes()).hexdigest(),
              'entries': rows, 'largeDuplicateGroups': [v for v in groups.values() if len(v) > 1]}
    (path.parent / 'apk-inventory.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({**result, 'entries': rows[:15]}, indent=2))


if __name__ == '__main__':
    audit(Path(sys.argv[1]))

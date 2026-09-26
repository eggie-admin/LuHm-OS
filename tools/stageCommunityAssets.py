"""Stage an explicitly selected, hash-pinned CC0 pack. No archive-wide extraction."""
import hashlib
import json
from pathlib import Path
import sys
import zipfile

DIGEST = '5b381164e5760f3830a2dbee43b972deee38b2a695d091b56e238ab2910c96d2'
MEMBERS = ('building-a.glb', 'chimney-large.glb', 'shipping-container-a.glb', 'Textures/colormap.png')

def stage(archive, root):
    data = Path(archive).read_bytes()
    if hashlib.sha256(data).hexdigest() != DIGEST:
        raise ValueError('Community archive hash mismatch')
    with zipfile.ZipFile(archive) as pack:
        payloads = {name: pack.read('Models/GLB format/' + name) for name in MEMBERS}
        license_text = pack.read('License.txt').decode('utf-8-sig')
    if 'Creative Commons Zero' not in license_text:
        raise ValueError('Expected CC0 license missing')
    if sum(map(len, payloads.values())) > 1000000:
        raise ValueError('Community source budget exceeded')
    output = Path(root) / 'assets/community/industrial'
    for name, value in payloads.items():
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(value)
    (output / 'LICENSE.txt').write_text(license_text)
    receipt = {'archiveSha256': DIGEST, 'license': 'CC0-1.0', 'creator': 'Kenney',
               'files': {name: {'bytes': len(value), 'sha256': hashlib.sha256(value).hexdigest()} for name, value in payloads.items()}}
    path = Path(root) / 'build/communityAssets.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    return receipt

if __name__ == '__main__':
    print(json.dumps(stage(sys.argv[1], Path(__file__).resolve().parents[1]), indent=2))

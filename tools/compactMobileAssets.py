"""Build-only, pinned-source derivatives; canonical GLBs remain in the verified JAR."""
import hashlib
import json
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def prepare(root):
    manifest = json.loads((root / 'remoteAssets/lum-full-pack.json').read_text())
    records = []
    shared = None
    shared_materials = None
    for member in manifest['members']:
        path = root / member['output']
        data = path.read_bytes()
        if digest(data) != member['sha256']:
            raise ValueError('unverified source GLB')
        magic, version, length = struct.unpack_from('<4sII', data)
        if (magic, version, length) != (b'glTF', 2, len(data)):
            raise ValueError('invalid GLB')
        json_size, kind = struct.unpack_from('<II', data, 12)
        if kind != 0x4E4F534A:
            raise ValueError('missing GLB JSON')
        document = json.loads(data[20:20 + json_size])
        if shared_materials is not None and document.get('materials') != shared_materials:
            raise ValueError('materials differ; shared mesh would change appearance')
        shared_materials = document.get('materials')
        binary_chunk = data[20 + json_size:]
        binary = binary_chunk[8:]
        if len(document['images']) != 1:
            raise ValueError('unexpected image layout')
        view = document['bufferViews'][document['images'][0]['bufferView']]
        start = view.get('byteOffset', 0)
        png = binary[start:start + view['byteLength']]
        if shared is not None and png != shared:
            raise ValueError('textures differ; deduplication forbidden')
        shared = png
        preserved = {k: v for k, v in document.items() if k != 'images'}
        document['images'] = [{'uri': 'lumShared.png', 'name': 'LumSharedAtlas'}]
        encoded = json.dumps(document, separators=(',', ':')).encode()
        encoded += b' ' * (-len(encoded) % 4)
        derivative = struct.pack('<4sII', b'glTF', 2, 20 + len(encoded) + len(binary_chunk))
        derivative += struct.pack('<II', len(encoded), 0x4E4F534A) + encoded + binary_chunk
        parsed = json.loads(derivative[20:20 + len(encoded)])
        assert {k: v for k, v in parsed.items() if k != 'images'} == preserved
        assert derivative[20 + len(encoded):] == binary_chunk
        path.write_bytes(derivative)
        path.with_suffix('.glb.import').write_text('[remap]\nimporter="scene"\ntype="PackedScene"\n\n[params]\nimport_script/path="res://tools/compactSceneImport.gd"\n')
        records.append({'path': member['output'], 'sourceSha256': member['sha256'],
                        'derivativeSha256': digest(derivative),
                        'nonImageDocumentAndBinaryPreserved': True})
    texture = root / 'assets/lum/lumShared.png'
    texture.write_bytes(shared)
    texture.with_suffix('.png.import').write_text('''[remap]
importer="texture"
type="CompressedTexture2D"

[params]
compress/mode=1
compress/lossy_quality=0.95
mipmaps/generate=true
process/fix_alpha_border=false
detect_3d/compress_to=0
''')
    report = {'schema': 'luhm.mobile-derivatives.v1', 'canonicalSources': manifest['jarOutput'],
              'textureSourceSha256': digest(shared), 'textureQuality': 0.95,
              'textureResolutionUnchanged': True, 'members': records}
    (root / 'build/remote-assets/mobile-derivatives.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    prepare(ROOT)

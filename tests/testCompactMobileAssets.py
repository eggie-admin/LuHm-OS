import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('compact', Path(__file__).resolve().parents[1] / 'tools/compactMobileAssets.py')
compact = importlib.util.module_from_spec(spec)
spec.loader.exec_module(compact)


class CompactTests(unittest.TestCase):
    def fixture(self, root, second_texture=b'abcd'):
        (root / 'remoteAssets').mkdir()
        (root / 'assets/lum').mkdir(parents=True)
        (root / 'build/remote-assets').mkdir(parents=True)
        members = []
        for name, texture in [('luhm.glb', b'abcd'), ('luhmRunning.glb', second_texture)]:
            doc = {'asset': {'version': '2.0'}, 'images': [{'bufferView': 0}],
                   'bufferViews': [{'byteOffset': 0, 'byteLength': 4}],
                   'materials': [{'name': 'preserved'}], 'animations': [{'name': name}]}
            encoded = json.dumps(doc).encode()
            encoded += b' ' * (-len(encoded) % 4)
            blob = struct.pack('<4sII', b'glTF', 2, 32 + len(encoded))
            blob += struct.pack('<II', len(encoded), 0x4E4F534A) + encoded
            blob += struct.pack('<II', 4, 0x004E4942) + texture
            output = 'assets/lum/' + name
            (root / output).write_bytes(blob)
            members.append({'output': output, 'sha256': hashlib.sha256(blob).hexdigest()})
        (root / 'remoteAssets/lum-full-pack.json').write_text(json.dumps({'members': members, 'jarOutput': 'build/remote-assets/original.jar'}))

    def test_tampered_source_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.fixture(root)
            (root / 'assets/lum/luhm.glb').write_bytes(b'tampered')
            with self.assertRaises(ValueError):
                compact.prepare(root)

    def test_different_texture_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.fixture(root, b'efgh')
            with self.assertRaises(ValueError):
                compact.prepare(root)

    def test_preserve_animation_and_binary(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.fixture(root)
            compact.prepare(root)
            blob = (root / 'assets/lum/luhmRunning.glb').read_bytes()
            size = struct.unpack_from('<I', blob, 12)[0]
            doc = json.loads(blob[20:20 + size])
            self.assertEqual(doc['animations'], [{'name': 'luhmRunning.glb'}])
            self.assertEqual(blob[-4:], b'abcd')
            self.assertEqual((root / 'assets/lum/lumShared.png').read_bytes(), b'abcd')


if __name__ == '__main__':
    unittest.main()

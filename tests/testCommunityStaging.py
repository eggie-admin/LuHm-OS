"""Negative controls for asset ingress; no network or Godot needed."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import hashlib
import zipfile

spec = importlib.util.spec_from_file_location('stager', Path(__file__).resolve().parents[1] / 'tools/stageCommunityAssets.py')
stager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stager)

class StagingTests(unittest.TestCase):
    def fixture(self, path, duplicate=False, huge=False):
        with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
            for name in stager.MEMBERS:
                z.writestr('Models/GLB format/' + name, b'x' * (1_000_001 if huge else 4))
            z.writestr('License.txt', 'Creative Commons Zero')
            if duplicate:
                z.writestr('License.txt', 'Creative Commons Zero')
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def test_rejections_leave_no_assets(self):
        for case in ('hash', 'duplicate', 'expanded', 'symlink', 'archive_size'):
            with self.subTest(case=case), tempfile.TemporaryDirectory() as temp:
                base = Path(temp); root = base / 'project'; root.mkdir()
                archive = base / 'pack.zip'
                digest = self.fixture(archive, duplicate=case=='duplicate', huge=case=='expanded')
                if case == 'symlink':
                    (root / 'assets').symlink_to(base / 'outside', target_is_directory=True)
                if case == 'archive_size':
                    with archive.open('ab') as f: f.truncate(8_000_001)
                with patch.object(stager, 'DIGEST', 'wrong' if case=='hash' else digest):
                    with self.assertRaises(ValueError): stager.stage(archive, root)
                self.assertFalse((root / 'build/communityAssets.json').exists())
                self.assertFalse((base / 'outside').exists())

if __name__ == '__main__': unittest.main()

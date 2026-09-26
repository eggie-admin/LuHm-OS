import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('gate', Path(__file__).resolve().parents[1] / 'tools/candidateGate.py')
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

class GateTests(unittest.TestCase):
    def test_runtime_forbidden_and_read_errors_fail(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for name in ('scripts', 'scenes', 'cutscenes'):
                (root / name).mkdir()
            fixture = root / 'scripts/main.gd'
            fixture.write_text('extends Node\n')
            gate.scan_runtime(root)
            fixture.write_text('var command = "RUN_COMMAND"\n')
            with self.assertRaises(ValueError):
                gate.scan_runtime(root)
            fixture.write_bytes(b'\xff')
            with self.assertRaises(UnicodeError):
                gate.scan_runtime(root)
    def test_missing_scope_fails(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                gate.scan_runtime(Path(d))
    def test_native_alignment_negative_controls(self):
        data = bytearray(120)
        data[:6] = b'\x7fELF\x02\x01'
        struct.pack_into('<Q', data, 32, 64)
        struct.pack_into('<HH', data, 54, 56, 1)
        struct.pack_into('<IIQQQQQQ', data, 64, 1, 5, 0, 0, 0, 0, 0, 16384)
        self.assertEqual(gate.elf_alignment(data), [16384])
        struct.pack_into('<Q', data, 112, 4096)
        with self.assertRaises(ValueError):
            gate.elf_alignment(data)
        struct.pack_into('<Q', data, 112, 16384)
        struct.pack_into('<Q', data, 80, 4096)
        with self.assertRaises(ValueError):
            gate.elf_alignment(data)

if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python3
"""Offline negative tests for the existing studio FFmpeg path boundary.

No FFmpeg subprocess, network, device, or rendering is invoked.
"""
import importlib.util
import pathlib
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "host/ai-ffmpeg/ai-ffmpeg.py"
spec = importlib.util.spec_from_file_location("luhm_ai_ffmpeg", SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class StudioPathBoundary(unittest.TestCase):
    def test_safe_child(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "input.png").write_bytes(b"synthetic")
            self.assertEqual(module.childPath(root, "input.png", True), root / "input.png")

    def test_traversal_absolute_and_nul(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            for name in ("../escape.png", "/tmp/escape.png", "bad\x00name.png", ""):
                with self.subTest(name=repr(name)), self.assertRaises(ValueError):
                    module.childPath(root, name, False)

    def test_symlink_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            outside = root.parent / (root.name + "-outside.png")
            outside.write_bytes(b"synthetic")
            try:
                (root / "link.png").symlink_to(outside)
                with self.assertRaises(ValueError):
                    module.childPath(root, "link.png", True)
            finally:
                outside.unlink(missing_ok=True)

    def test_unapproved_render_rejected_before_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = {"schema": module.schema, "jobId": "test-job", "shots": [],
                        "output": "out.mp4", "reviewApproved": False}
            with self.assertRaises(PermissionError):
                module.validate(manifest, tmp, tmp)

    def test_unknown_manifest_fields_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = {"schema": module.schema, "jobId": "test-job", "shots": [],
                        "output": "out.mp4", "reviewApproved": True, "shell": "echo unsafe"}
            with self.assertRaises(ValueError):
                module.validate(manifest, tmp, tmp)


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Bounded negative controls for the accepted-source identity fast path."""
import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from tools.jqueryPluginContinuity import verify_entry


class TestPluginReuse(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.path = self.root / "frontEnd" / "jquery" / "demo.js"
        self.path.parent.mkdir(parents=True)
        self.path.write_bytes(b"(function ($) { return $; }(jQuery));\n")
        raw = self.path.read_bytes()
        sha = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\x00" + raw).hexdigest()
        self.entry = {"path": "frontEnd/jquery/demo.js", "gitBlobSha": sha}

    def tearDown(self):
        self.temp.cleanup()

    def test_exact_identity_reuses_acceptance(self):
        self.assertEqual(verify_entry(self.root, self.entry), (True, "sameSourceAccepted"))

    def test_changed_code_requires_only_delta_review(self):
        self.path.write_bytes(b"var changed = true;\n")
        self.assertEqual(verify_entry(self.root, self.entry)[1], "changedSourceNeedsDeltaReview")

    def test_path_traversal_rejected(self):
        self.assertEqual(verify_entry(self.root, {"path": "../private.js", "gitBlobSha": self.entry["gitBlobSha"]})[1], "invalidPath")

    def test_bad_hash_rejected(self):
        self.assertEqual(verify_entry(self.root, {"path": self.entry["path"], "gitBlobSha": "0" * 39})[1], "invalidHash")

    def test_symlink_rejected(self):
        target = self.root / "target.js"
        target.write_bytes(self.path.read_bytes())
        self.path.unlink()
        self.path.symlink_to(target)
        self.assertEqual(verify_entry(self.root, self.entry)[1], "symlinkNotAllowed")

    def test_absent_source_not_assumed_present(self):
        self.path.unlink()
        self.assertEqual(verify_entry(self.root, self.entry)[1], "missingOrOutsideRoot")


if __name__ == "__main__":
    unittest.main()

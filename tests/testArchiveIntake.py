"""Offline ZIP safety and repeatability regression."""
import io
import pathlib
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tools"))
import archiveIntake as intake

class ArchiveIntakeTests(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.root = pathlib.Path(self.t.name)
        self.source = self.root/"sources"
        self.target = self.root/"staging"
        self.source.mkdir()

    def make_zip(self, name, mapping):
        with zipfile.ZipFile(self.source/name, "w") as z:
            for key, value in mapping.items():
                z.writestr(key, value)

    def test_zip_sorted_and_repeatable(self):
        self.make_zip("trial.zip", {"art/one.png":b"PNG", "code/run.py":b"print('ok')", "docs/notes.md":b"Hi"})
        result = intake.stage(self.source, self.target)
        self.assertEqual(result["fileCount"], 3)
        self.assertEqual(result["archives"][0]["status"], "STAGED_NO_PROMOTION")
        before = sorted(str(x) for x in (self.target/"byType").rglob("*") if x.is_file())
        self.assertEqual(result["fileCount"], intake.stage(self.source, self.target)["fileCount"])
        after = sorted(str(x) for x in (self.target/"byType").rglob("*") if x.is_file())
        self.assertEqual(before, after)
        self.assertTrue(any("artRaster" in x for x in after))
        self.assertTrue(any("codePython" in x for x in after))

    def test_path_traversal_is_blocked(self):
        self.make_zip("bad.zip", {"../out.txt":b"not allowed"})
        result = intake.stage(self.source, self.target)
        self.assertEqual(result["fileCount"], 0)
        self.assertEqual(result["archives"][0]["status"], "BLOCKED")
        self.assertFalse((self.root/"out.txt").exists())

    def test_unknown_type_stays_unclassified(self):
        self.make_zip("unknown.zip", {"opaque.weird":b"x"})
        result = intake.stage(self.source, self.target)
        self.assertEqual(result["archives"][0]["files"][0]["typeFolder"], "reviewUnclassified")

    def test_source_and_destination_must_not_nest(self):
        with self.assertRaises(intake.IntakeError):
            intake.stage(self.source, self.source/"output")

if __name__ == "__main__":
    unittest.main()

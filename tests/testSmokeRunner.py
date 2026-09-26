import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("smokeRunner", Path(__file__).resolve().parents[1] / "tools/runGodotSmoke.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

class SmokeGateTests(unittest.TestCase):
    def test_zero_exit_with_script_error_is_rejected(self):
        with self.assertRaises(ValueError):
            runner.validate("SCRIPT ERROR: bad call\nPASS", 0, "PASS")
    def test_missing_completion_is_rejected(self):
        with self.assertRaises(ValueError):
            runner.validate("started", 0, "PASS")
    def test_nonzero_exit_is_rejected(self):
        with self.assertRaises(ValueError):
            runner.validate("PASS", 1, "PASS")
    def test_clean_completion(self):
        runner.validate("PASS", 0, "PASS")

if __name__ == "__main__":
    unittest.main()

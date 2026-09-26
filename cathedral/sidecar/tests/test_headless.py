import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[1]))
import kai9000_headless as h


class HeadlessContractTests(unittest.TestCase):
    def test_loopback_only(self):
        self.assertEqual(h.validate_base("http://127.0.0.1:11434"), "http://127.0.0.1:11434")
        with self.assertRaises(ValueError):
            h.validate_base("https://example.com")
        with self.assertRaises(ValueError):
            h.validate_base("http://0.0.0.0:11434")

    def test_models_are_discovered(self):
        with patch.object(h, "ollama_json", return_value={"models": [{"name": "a:1"}, {"name": "b:1"}]}):
            self.assertEqual(h.models(), ["a:1", "b:1"])

    def test_chat_rejects_missing_model(self):
        with patch.object(h, "models", return_value=["a:1"]):
            with self.assertRaises(ValueError):
                h.chat("b:1", "hello")

    def test_memory_is_candidate_only(self):
        with tempfile.TemporaryDirectory() as td:
            old_state, old_file = h.STATE_DIR, h.MEMORY_FILE
            try:
                h.STATE_DIR = Path(td)
                h.MEMORY_FILE = Path(td) / "memory-candidates.jsonl"
                receipt = h.memory_candidate("Keep the bridge typed.", ["repo@sha"], ["bridge"])
                self.assertEqual(receipt["state"], "CANDIDATE_NOT_ACTIVE")
                self.assertIn('"promotion_authorized":false', h.MEMORY_FILE.read_text())
            finally:
                h.STATE_DIR, h.MEMORY_FILE = old_state, old_file


if __name__ == "__main__":
    unittest.main()

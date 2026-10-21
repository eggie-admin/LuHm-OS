"""Professor compatibility order: OpenAI #1, GitHub #2, no executable Vertex."""
import json
import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class ActiveCompatibilityOrderTests(unittest.TestCase):
    def test_canonical_priority_is_exact(self):
        truth = json.loads((ROOT / "doctrine/currentSourceTruthV3.json").read_text())
        compatibility = truth["activeCompatibilityOrder"]
        self.assertEqual([compatibility["first"], compatibility["second"]], ["chatGptOpenAi", "github"])
        self.assertEqual(compatibility["sourceAuthority"], "github")
        self.assertTrue(compatibility["noProviderFallbackToVertex"])
        self.assertEqual(compatibility["vertexAi"], "DISABLED_LEGACY_ARCHIVAL_ONLY")

    def test_studio_never_selects_google_or_vertex(self):
        sys.path.insert(0, str(ROOT / "tools"))
        import studioFastMesh
        from lumTaskRouter import ROUTES
        for kind in ROUTES:
            for heavy in (False, True):
                with self.subTest(kind=kind, heavy=heavy):
                    receipt = studioFastMesh.plan(kind, heavy=heavy)
                    self.assertNotIn(receipt["providerCandidate"], ("googleAi", "vertexAi"))
                    self.assertFalse(receipt["vertexAllowed"])
                    self.assertFalse(receipt["autoVertexFallback"])
                    self.assertFalse(receipt["mayInvokeProvider"])

    def test_legacy_vertex_network_actions_blocked_before_credentials(self):
        entry = ROOT / "host/api/luhmVideoJobWorker.py"
        for action in ("submit", "poll"):
            with self.subTest(action=action):
                child = subprocess.run(
                    [sys.executable, str(entry), action, "--approve-spend", "--cost-ceiling-usd", "99.00"],
                    cwd=ROOT, capture_output=True, text=True, timeout=10,
                )
                self.assertEqual(child.returncode, 2)
                self.assertIn("CROWN_STOP_VERTEX_DISABLED_OPENAI_FIRST_GITHUB_SECOND", child.stderr)

    def test_old_vertex_submit_path_also_blocked(self):
        import importlib.util
        file = ROOT / "tools/yumeVertexVeoQueue.py"
        spec = importlib.util.spec_from_file_location("historicalYumeVeo", file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with self.assertRaises(PermissionError):
            module.submit_one("irrelevant", "lum", {})


if __name__ == "__main__":
    unittest.main()

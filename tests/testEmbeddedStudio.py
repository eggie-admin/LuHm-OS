"""Schema, route, CSP and unknown-authority regression checks."""
import copy
import json
import os
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "host/mcp"))
from luhmHarness import _headers, _safe_file, _studio_contract, _studio_page
from jsonschema import Draft202012Validator


class StudioTests(unittest.TestCase):
    def test_shared_resource_render(self):
        for filename, widget in (("index.html", False), ("widget.html", True)):
            root = ROOT / "host/harness"
            page = _studio_page(root, (root / filename).read_text(), widget=widget)
            self.assertEqual(page.count('id="luhmStudioDeck"'), 1)
            self.assertNotIn("<!-- LUHM_STUDIO_DECK -->", page)
            self.assertNotIn("wireStudio();", page)

    def test_narrow_csp(self):
        policy = _headers(html=True)["Content-Security-Policy"]
        self.assertIn("frame-src 'self' https://www.youtube-nocookie.com;", policy)
        self.assertIn("script-src 'self';", policy)
        self.assertNotIn("youtube.com", policy)
        self.assertNotIn("youtube-nocookie", _headers(html=True, godot_embed=True)["Content-Security-Policy"])

    def test_contract_does_not_grant_execution(self):
        value = _studio_contract(ROOT)
        self.assertEqual(value["lane"], "testing")
        self.assertIs(value["productionPromotion"], False)
        self.assertIs(value["quarantine"]["activeTaskWorkersAllowed"], False)
        self.assertEqual(value["sourceRef"], os.environ.get("RENDER_GIT_COMMIT", "UNKNOWN"))

    def test_no_asset_path_escape(self):
        self.assertIsNone(_safe_file(ROOT / "host/harness", "../../AGENTS.md"))

    def test_register_schema_and_negative_authority(self):
        schema = json.loads((ROOT / "doctrine/assetRegisterV1.schema.json").read_text())
        validator = Draft202012Validator(schema)
        sample = {"schema":"luhmOs.assetRegister.v1","sourceRef":"UNKNOWN","createdAt":"2026-10-20T23:00:00Z","serverWrites":False,"productionPromotion":False,"assets":[]}
        validator.validate(sample)
        for field in ("serverWrites", "productionPromotion"):
            wrong = copy.deepcopy(sample); wrong[field] = True
            self.assertTrue(list(validator.iter_errors(wrong)))
        export = os.environ.get("LUHM_STUDIO_EXPORT")
        if export and Path(export).is_file():
            validator.validate(json.loads(Path(export).read_text()))


if __name__ == "__main__":
    unittest.main()

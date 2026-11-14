"""LuHm-OS Creator Studio validation and SQLite round-trip tests."""
import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("creatorStudio", ROOT / "tools/creatorStudio.py")
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)
SOURCE = ROOT / "game/studio/nightglassHubV1.json"
SHA = "a6e3ce843d099361a8696eab68869dcf367c4f26"

class CreatorStudioTests(unittest.TestCase):
    def setUp(self):
        self.world = module.readWorld(SOURCE)

    def test_canonical_world(self):
        receipt = module.validateWorld(self.world)
        self.assertEqual(receipt["worldId"], "nightglassCrossroads")
        self.assertEqual(receipt["scenes"], 2)
        self.assertEqual(receipt["dialogueLines"], 7)

    def test_bar_opens_with_original_vesper(self):
        bar = next(s for s in self.world["scenes"] if s["sceneId"] == "nightglassBarHub")
        self.assertEqual(bar["spawnDialogueId"],"vesperEcho")
        original = next(r for r in self.world["dialogue"] if r["lineId"]=="vesperEcho")
        self.assertEqual(original["speakerId"],"vesperNocturne")
        self.assertFalse(next(c for c in self.world["characters"] if c["characterId"]=="vesperNocturne")["approvedRig"])

    def test_no_llmos_alias(self):
        self.assertEqual(self.world["product"], "LuHm-OS")
        self.assertEqual(self.world["orchestration"]["productAuthority"], "LuHm-OS")
        self.assertFalse(self.world["orchestration"]["sqlPromotionFromSuggestion"])

    def test_cross_scene_jump_rejected(self):
        bad = copy.deepcopy(self.world)
        bad["dialogue"][0]["choices"][0]["nextLineId"] = "shoreRune"
        with self.assertRaises(module.StudioError):
            module.validateWorld(bad)

    def test_unregistered_speaker_rejected(self):
        bad = copy.deepcopy(self.world)
        bad["dialogue"][0]["speakerId"] = "someNewAgent"
        with self.assertRaises(module.StudioError):
            module.validateWorld(bad)

    def test_rights_and_quarantine_gates(self):
        for mutation in ("assets", "workers", "release"):
            bad = copy.deepcopy(self.world)
            if mutation == "assets": bad["assetPolicy"]["thirdPartyDataAllowed"] = True
            if mutation == "workers": bad["orchestration"]["liveWorkerState"] = "ACTIVE"
            if mutation == "release": bad["release"]["cast"] = "GREEN"
            with self.assertRaises(module.StudioError):
                module.validateWorld(bad)

    def test_roundtrip_sqlite_export(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "creator.sqlite"
            with module.connect(str(path)) as db:
                db.row_factory = __import__("sqlite3").Row
                proof = module.importWorld(db, self.world, SHA)
                self.assertFalse(proof["promoted"])
                self.assertEqual(module.listWorlds(db)[0]["worldId"], "nightglassCrossroads")
                count = db.execute("SELECT COUNT(*) FROM studioDialogue").fetchone()[0]
                self.assertEqual(count, 7)
                output = Path(folder) / "out.json"
                module.exportWorld(db, "nightglassCrossroads", output)
                self.assertEqual(json.loads(output.read_text()), self.world)
                with self.assertRaises(module.StudioError):
                    module.exportWorld(db, "nightglassCrossroads", output)

    def test_invalid_source_ref_rejected(self):
        with module.connect(":memory:") as db:
            with self.assertRaises(module.StudioError):
                module.importWorld(db, self.world, "main")

if __name__ == "__main__":
    unittest.main()

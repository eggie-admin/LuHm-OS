"""Source-only integrity tests for the derived Canon Control Room snapshot."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "sites" / "canon-control-room"
CAMEL = re.compile(r"^[a-z][A-Za-z0-9]*$")

class CanonControlRoomSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((SITE / "canonSnapshotV1.json").read_text(encoding="utf-8"))
        cls.script = (SITE / "app.js").read_text(encoding="utf-8")
        cls.markup = (SITE / "index.html").read_text(encoding="utf-8")

    def test_explicit_derived_authority(self):
        self.assertEqual(self.data["schema"], "luhmOs.canonControlRoomSnapshot.v1")
        self.assertEqual(self.data["canonicalRepository"], "eggie-admin/LuHm-OS")
        self.assertEqual(self.data["canonAuthorityPath"], "doctrine/currentSourceTruthV3.json")
        self.assertEqual(self.data["naming"]["machine"], "camelHump")
        self.assertTrue(self.data["naming"]["doNotRewriteHistory"])
        self.assertIn("Human promotes", self.data["sourceLaw"])

    def test_ids_statuses_and_stages(self):
        allowed = {"implemented", "tentative", "missing", "blocked"}
        for kind in ("systems", "assets", "gaps", "compliance", "agents", "deploy"):
            values = self.data[kind]
            ids = [item["id"] for item in values]
            self.assertEqual(len(ids),len(set(ids)),kind)
            for item in values:
                self.assertRegex(item["id"], CAMEL, kind)
                if "status" in item:
                    self.assertIn(item["status"],allowed)
        self.assertEqual(
            [x["id"] for x in self.data["auditStages"]],
            ["sanityCheck","audit","ingest","mutation","test","apply","continue","deploy"]
        )
        self.assertEqual(self.data["auditStages"][-1]["state"],"blocked")

    def test_all_evidence_paths_are_present_and_relative(self):
        for kind in ("systems", "assets", "compliance", "deploy"):
            for item in self.data[kind]:
                evidence = item["evidence"]
                self.assertFalse(evidence.startswith(("http:", "https:", "/")),evidence)
                self.assertNotIn("..",evidence)
                self.assertTrue((ROOT / evidence).is_file(),evidence)

    def test_browser_is_local_only_and_safe(self):
        self.assertIn("localStorage",self.script)
        self.assertIn("JSON.stringify",self.script)
        self.assertIn("touchstart",self.script)
        self.assertIn("ArrowDown",self.script)
        self.assertIn("exportState",self.script)
        self.assertIn("importState",self.script)
        self.assertNotIn("fetch(\"https://",self.script)
        self.assertNotIn("eval(",self.script)
        self.assertNotIn("innerHTML = incoming",self.script)
        self.assertIn("3D LUM MOUNT: UNVERIFIED",self.markup)

    def test_no_private_source_handles(self):
        text = (SITE / "canonSnapshotV1.json").read_text(encoding="utf-8")
        self.assertNotIn("drive.google.com/file/d/",text)
        self.assertNotIn("drive.google.com/drive/folders/",text)
        self.assertNotRegex(text,r"sk-[A-Za-z0-9]{15,}")
        self.assertNotIn("PRIVATE_KEY",text)

if __name__=="__main__":
    unittest.main()

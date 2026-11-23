"""Source-only safeguards for Pirate Daddy Film human-footage production manifest."""
from pathlib import Path
import json
import unittest

ROOT=Path(__file__).resolve().parents[1]
CANON=ROOT / "doctrine" / "reaperHumanFilmProductionV1.json"

class ReaperHumanFilmCanonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc=json.loads(CANON.read_text(encoding="utf-8"))

    def test_identity_and_separate_studio(self):
        d=self.doc
        self.assertEqual(d["title"],"The Reaper Is My Only G")
        self.assertEqual(d["productionLabel"],"Pirate Daddy Film")
        self.assertEqual(d["toolingLabel"],"Pirate Daddy Studios")
        self.assertEqual(len(d["palette"]),7)

    def test_privacy_rights_release_gates(self):
        d=self.doc
        self.assertFalse(d["aiGeneratedHumanPerformances"])
        self.assertTrue(d["licensePolicy"]["provenancePerFileRequired"])
        self.assertTrue(d["licensePolicy"]["nonmonetizedIsNotLicense"])
        self.assertFalse(d["gates"]["automaticAgentActivation"])
        self.assertFalse(d["gates"]["automaticPublicUpload"])
        self.assertFalse(d["gates"]["automaticPublishing"])
        self.assertEqual(d["gates"]["crownStatus"],"STOP")
        self.assertFalse(d["safety"]["graphicMethodDepiction"])

if __name__=="__main__":
    unittest.main()

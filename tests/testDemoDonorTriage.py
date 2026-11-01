import copy
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile
from tools.demoDonorTriage import DEFAULT, inspect_candidate, pick, validate

DOC = json.loads(DEFAULT.read_text(encoding="utf-8"))

class DonorTriageTests(unittest.TestCase):
    def test_4_scenes_have_real_candidates(self):
        validate(DOC)
        for name in ("cathedral", "neonRiverwalk", "lumCoffeeHouse", "characterBench"):
            rows = pick(DOC, name)
            self.assertTrue(rows)
            self.assertLessEqual(len(rows), 3)
            self.assertTrue(all(x["state"] == "DISCOVERED_NOT_IMPORTED" for x in rows))
    def test_no_import_or_public_rights_are_fabricated(self):
        for c in DOC["candidates"]:
            self.assertIs(c["publicAllowed"], False)
            self.assertNotEqual(c["godotImport"], "TESTED")
        self.assertEqual(DOC["proof"]["thirdPartyHashesVerified"], False)
    def test_unknown_license_and_false_promotion_rejected(self):
        d = copy.deepcopy(DOC)
        d["candidates"][2]["publicAllowed"] = True
        with self.assertRaisesRegex(ValueError, "FALSE_GAME_READY_PROMOTION"):
            validate(d)
        d = copy.deepcopy(DOC)
        d["candidates"][2]["sourceHash"] = "a"*64
        with self.assertRaisesRegex(ValueError, "UNSUPPORTED_DOWNLOADED_EVIDENCE"):
            validate(d)
        d = copy.deepcopy(DOC)
        d["candidates"][2]["license"] = "UNKNOWN"
        with self.assertRaisesRegex(ValueError, "UNVERIFIED_EXTERNAL_LICENSE"):
            validate(d)
    def test_no_autonomous_downloads_or_fanout(self):
        for key in ("automaticDownload", "autoMerge", "autoDeploy", "autoPublish"):
            d = copy.deepcopy(DOC)
            d["escalation"][key] = True
            with self.assertRaisesRegex(ValueError, "UNAUTHORIZED_AUTO_ESCALATION"):
                validate(d)
        d = copy.deepcopy(DOC)
        d["escalation"]["maxSimultaneousDonorPacks"] = 32
        with self.assertRaisesRegex(ValueError, "UNBOUNDED_DONOR_ESCALATION"):
            validate(d)
    def test_untrusted_zip_is_inspected_not_extracted_or_shipped(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            good = root / "donor.zip"
            with ZipFile(good, "w") as z:
                z.writestr("models/arch.glb", b"not-a-real-model")
                z.writestr("LICENSE.txt", "CC0 https://creativecommons.org/publicdomain/zero/1.0/")
            result = inspect_candidate(DOC, "kenney-castle", good)
            self.assertEqual(result["archiveStatus"], "ZIP_SCAN_PASS")
            self.assertEqual(result["modelFormatEntries"], 1)
            self.assertIs(result["extractionPerformed"], False)
            self.assertIs(result["publicAllowed"], False)
            self.assertIs(result["needsGodotImportTest"], True)
            self.assertFalse((root / "models").exists())
            with ZipFile(good, "w") as z:
                z.writestr("../escape.glb", b"bad")
            result = inspect_candidate(DOC, "kenney-castle", good)
            self.assertEqual(result["archiveStatus"], "FAIL_QUARANTINE")
            self.assertFalse((root / "escape.glb").exists())
    def test_legacy_cc0_claim_is_not_current_qal_license(self):
        conflicts = DOC["knownLicenseConflicts"]
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0]["currentOfficialPageLicense"], "QAL")
        self.assertEqual(conflicts[0]["currentState"], "HOLD_UNTIL_EXACT_QAL_TERMS_REVIEW")
        self.assertFalse(conflicts[0]["publicAllowed"])
        self.assertNotIn(conflicts[0]["assetId"], [a["assetId"] for a in DOC["candidates"]])
    def test_lum_private_biped_matches_historical_canon_not_game_ready(self):
        from pathlib import Path
        receipt = json.loads(Path("game/demo/lumRigSourceInspectionV1.json").read_text())
        candidate = next(x for x in DOC["candidates"] if x["assetId"] == "luhm-lum-rigged-biped")
        self.assertEqual(candidate["sourceHash"], receipt["archiveSha256"])
        self.assertTrue(receipt["zipCrcPass"])
        self.assertEqual(len(receipt["models"]), 2)
        self.assertTrue(all(x["joints"] == 24 and x["skins"] == 1 and x["godotImported"] is False for x in receipt["models"]))
        self.assertFalse(candidate["publicAllowed"])
        self.assertEqual(candidate["godotImport"], "NOT_TESTED")
        self.assertEqual(receipt["sourceStorageSharing"], "EXPOSED_ANYONE_WRITER_NEEDS_OWNER_RESTRICTION")
        self.assertTrue(receipt["ownerOnlyQuarantine"]["copyOwnerOnlyMetadataVerified"])
        self.assertTrue(receipt["ownerOnlyQuarantine"]["copySha256Verified"])
        self.assertEqual(receipt["ownerOnlyQuarantine"]["copySha256"], receipt["archiveSha256"])
        self.assertTrue(receipt["ownerOnlyQuarantine"]["originalShareExposureUnfixed"])
    def test_legacy_archive_hash_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "donor.zip"
            with ZipFile(p, "w") as z:
                z.writestr("safe/model.glb", b"dummy")
            r = inspect_candidate(DOC, "luhm-pocket-art-starter", p)
            self.assertEqual(r["archiveStatus"], "HASH_MISMATCH")
            self.assertIs(r["publicAllowed"], False)

if __name__ == "__main__":
    unittest.main()

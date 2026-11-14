"""LuHm-OS Canon and stockroom source-only assertions.

Review-only. These tests do not move files or synchronize Google Drive and Library.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class CanonStockroomNamingTests(unittest.TestCase):
    def test_canonical_identity_and_global_hold(self):
        truth = read("doctrine/currentSourceTruthV3.json")
        brand = read("doctrine/brandCanonV1.json")
        self.assertEqual(truth["product"], "LuHm-OS")
        self.assertEqual(brand["identity"]["product"]["display"], "LuHm-OS")
        self.assertIn("Project Hydra", brand["identity"]["world"]["legacyAliases"])
        self.assertFalse(truth["promotion"])
        self.assertEqual(truth["crownStatus"], "STOP")

    def test_private_stockroom_is_not_a_master_or_sync(self):
        truth = read("doctrine/currentSourceTruthV3.json")
        storage = read("doctrine/storageTopologyV1.json")
        self.assertEqual(truth["storageTopology"]["contract"], "doctrine/storageTopologyV1.json")
        self.assertEqual(storage["roles"]["googleDrive"]["role"], "fileServer")
        self.assertTrue(storage["roles"]["googleDrive"]["canonicalBinaryStorage"])
        self.assertTrue(storage["roles"]["github"]["canonicalSourceAuthority"])
        library = storage["roles"]["chatGptLibrary"]
        self.assertEqual(library["role"], "workingReviewLayer")
        self.assertFalse(library["canonicalSourceAuthority"])
        self.assertFalse(library["canonicalBinaryStorage"])
        self.assertFalse(library["promotionAuthority"])
        self.assertFalse(library["automaticallySynchronizedWithDrive"])
        self.assertFalse(library["mayReplaceDriveMaster"])
        self.assertFalse(storage["rules"]["chatGptLibraryMayReplaceDriveMaster"])
        self.assertFalse(storage["rules"]["chatGptLibraryAutomaticSyncProven"])
        self.assertFalse(truth["storageTopology"]["automaticDriveLibrarySyncProven"])
        self.assertFalse(truth["storageTopology"]["promotion"])


if __name__ == "__main__":
    unittest.main()

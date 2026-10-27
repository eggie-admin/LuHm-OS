"""Offline Git/SQLite JSON1 manifest + four-tier Crown alignment tests."""
import importlib.util
import sqlite3
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "git_sql_cast_align", ROOT / "tools/git-sql-cast-align.py")
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)
HEAD = "a" * 40


class git_sql_cast_tests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        module.init_schema(self.db, ROOT)

    def tearDown(self):
        self.db.close()

    def test_four_tiers_two_lanes_source_only(self):
        record = module.align(self.db, ROOT, HEAD)
        self.assertEqual(record["companyTierCount"], 4)
        self.assertEqual(record["typedPacketCount"], 2)
        self.assertEqual(record["appAndPluginScopes"],
                         ["final-proposed-app", "final-proposed-plugin"])
        self.assertFalse(record["providerCalled"])
        self.assertFalse(record["siteDeployed"])
        self.assertEqual(record["crown"], "STOP")
        rows = self.db.execute("""SELECT s.sourceRef,
               JSON_EXTRACT(m.manifestJson,'$.sourceRef'),m.mutationAuthority,
               m.greenAuthority,m.crownAuthority FROM streamEvent s
               JOIN aiManifestStream m USING(eventId)""").fetchall()
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(row == (HEAD,HEAD,0,0,0) for row in rows))
        site = self.db.execute("""SELECT JSON_EXTRACT(envelopeJson,'$.evidence.site.cacheBridgeGreen')
                                 FROM crownProof""").fetchone()[0]
        self.assertEqual(site, 0)

    def test_idempotent_and_append_only_per_git_head(self):
        first = module.align(self.db, ROOT, HEAD)
        second = module.align(self.db, ROOT, HEAD)
        self.assertEqual(first["proofSha256"], second["proofSha256"])
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM crownProof").fetchone()[0], 1)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM aiManifestStream").fetchone()[0], 2)
        third = module.align(self.db, ROOT, "b"*40)
        self.assertNotEqual(first["proofId"], third["proofId"])
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM crownProof").fetchone()[0], 2)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM aiManifestStream").fetchone()[0], 4)

    def test_refuse_existing_proof_tamper_and_preserve_transaction(self):
        first = module.align(self.db, ROOT, HEAD)
        self.db.execute("UPDATE crownProof SET envelopeJson=? WHERE proofId=?",
                        ('{"forged":true}', first["proofId"]))
        self.db.commit()  # Persist the corrupt row before align() owns its transaction.
        with self.assertRaisesRegex(ValueError, "RED_SAME_PROOF_ID_DIFFERENT_BYTES"):
            module.align(self.db, ROOT, HEAD)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM aiManifestStream").fetchone()[0], 2)

    def test_fk_and_unverified_provider_authority(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("""INSERT INTO aiManifestStream
                             (eventId,manifestJson,manifestSchema,providerId,capabilityId)
                             VALUES ('missing','{}','bad','googleAi','candidateReview')""")
        for lane in module.LANES:
            packet = module.packet_for(ROOT, HEAD, lane)
            self.assertEqual(packet["authority"],
                             {"mutation": False, "green": False, "crown": False})
            self.assertEqual(packet["providerId"], "googleAi")
        with self.assertRaisesRegex(ValueError, "RED_LANE_OR_GIT_HEAD"):
            module.packet_for(ROOT, "not-a-sha", "app")


if __name__ == "__main__":
    unittest.main()

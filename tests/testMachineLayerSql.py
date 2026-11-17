import copy
import importlib.util
import os
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("machineLayerSql",ROOT/"tools/machineLayerSql.py")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class MachineLayerSqlTest(unittest.TestCase):
    def setUp(self):
        self.manifest=mod.loadManifest()
        self.original=os.environ.get("LUHM_SQL_SYNC_KEY")
        os.environ["LUHM_SQL_SYNC_KEY"]="testOnlyEphemeralKeyForCiNeverDeploy001"
    def tearDown(self):
        if self.original is None: os.environ.pop("LUHM_SQL_SYNC_KEY",None)
        else: os.environ["LUHM_SQL_SYNC_KEY"]=self.original
    def test_four_by_four(self):
        self.assertEqual(len(self.manifest["escalation"]["cells"]),16)
        self.assertEqual(len(mod.eventsFor(self.manifest)),16)
        self.assertEqual(self.manifest["product"],"LuHm-OS")
    def test_unmerged_artifact_pointer_collision_remains_blocked(self):
        c=self.manifest["database"]["schemaCollision"]
        self.assertEqual(c["table"],"artifactPointer")
        self.assertFalse(c["structurallyCompatible"])
        self.assertTrue(c["remoteMigrationBlocked"])
        bad=copy.deepcopy(self.manifest)
        bad["database"]["schemaCollision"]["migrationPerformed"]=True
        with tempfile.TemporaryDirectory() as folder:
            file=Path(folder)/"migration.json"
            file.write_text(__import__("json").dumps(bad))
            with self.assertRaises(mod.MachineLayerError):
                mod.loadManifest(file)
    def test_mirrors_existing_canon_grid(self):
        canon=__import__("json").loads((ROOT/"doctrine/machineCanonFourLoopV1.json").read_text())
        self.assertEqual([x["id"] for x in self.manifest["escalation"]["levels"]], canon["fourBeats"])
        self.assertEqual([x["id"] for x in self.manifest["escalation"]["lanes"]], canon["lanes"])
        self.assertEqual(self.manifest["canonicalMachineMatrix"]["sqlProjectionOnly"], True)
    def test_canon_axis_drift_rejected(self):
        bad=copy.deepcopy(self.manifest)
        bad["escalation"]["lanes"][0]["id"]="newUnapprovedLane"
        with tempfile.TemporaryDirectory() as folder:
            file=Path(folder)/"axis.json"
            file.write_text(__import__("json").dumps(bad))
            with self.assertRaises(mod.MachineLayerError):
                mod.loadManifest(file)
    def test_machine_cells_cannot_gain_execution_authority(self):
        bad=copy.deepcopy(self.manifest)
        bad["escalation"]["cells"][0]["allowedAuthority"]="FULL_GREEN"
        with tempfile.TemporaryDirectory() as folder:
            file=Path(folder)/"promotion.json"
            file.write_text(__import__("json").dumps(bad))
            with self.assertRaises(mod.MachineLayerError):
                mod.loadManifest(file)
    def test_seed_is_idempotent(self):
        with mod.openLocalDb(":memory:") as db:
            self.assertEqual(mod.seed(db,self.manifest)["inserted"],16)
            self.assertEqual(mod.seed(db,self.manifest)["inserted"],0)
            self.assertEqual(mod.count(db,self.manifest)["present"],16)
    def test_tx_rx_authentic_and_idempotent(self):
        with mod.openLocalDb(":memory:") as sender,mod.openLocalDb(":memory:") as receiver:
            mod.seed(sender,self.manifest)
            p=mod.makePacket(sender,self.manifest)
            self.assertEqual(mod.receivePacket(receiver,self.manifest,p)["inserted"],16)
            self.assertEqual(mod.receivePacket(receiver,self.manifest,p)["inserted"],0)
    def test_packet_tamper_rejected(self):
        with mod.openLocalDb(":memory:") as sender,mod.openLocalDb(":memory:") as receiver:
            mod.seed(sender,self.manifest)
            p=mod.makePacket(sender,self.manifest)
            p["body"]["events"][0]["texts"]["machineState"]="FULL_GREEN"
            with self.assertRaises(mod.MachineLayerError): mod.receivePacket(receiver,self.manifest,p)
            self.assertEqual(mod.count(receiver,self.manifest)["present"],0)
    def test_wrong_secret_rejected(self):
        with mod.openLocalDb(":memory:") as sender,mod.openLocalDb(":memory:") as receiver:
            mod.seed(sender,self.manifest)
            p=mod.makePacket(sender,self.manifest)
            os.environ["LUHM_SQL_SYNC_KEY"]="differentSecretKeyAtLeast32CharsForTestOnly"
            with self.assertRaises(mod.MachineLayerError): mod.receivePacket(receiver,self.manifest,p)
    def test_explicit_quarantine_gate(self):
        bad=copy.deepcopy(self.manifest)
        bad["promotion"]=True
        with tempfile.TemporaryDirectory() as folder:
            candidate=Path(folder)/"bad.json"
            candidate.write_text(__import__("json").dumps(bad))
            with self.assertRaises(mod.MachineLayerError): mod.loadManifest(candidate)
    def test_backup_round_trip_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            local=Path(folder)/"live.sqlite"
            backup=Path(folder)/"backup.sqlite"
            with mod.openLocalDb(str(local)) as db:
                mod.seed(db,self.manifest)
                result=mod.backupSnapshot(db,backup,self.manifest)
            self.assertEqual(result["verifiedRows"],16)
            self.assertEqual(mod.verifyBackup(backup,self.manifest,result["sha256"])["status"],"LOCAL_BACKUP_VERIFIED")
            with mod.openLocalDb(str(local)) as db:
                with self.assertRaises(mod.MachineLayerError): mod.backupSnapshot(db,backup,self.manifest)
    def test_backup_wrong_digest_denied(self):
        with tempfile.TemporaryDirectory() as folder:
            local=Path(folder)/"live.sqlite"
            backup=Path(folder)/"backup.sqlite"
            with mod.openLocalDb(str(local)) as db:
                mod.seed(db,self.manifest)
                mod.backupSnapshot(db,backup,self.manifest)
            with self.assertRaises(mod.MachineLayerError):
                mod.verifyBackup(backup,self.manifest,"0"*64)
    def test_backup_rejects_unseeded_db(self):
        with tempfile.TemporaryDirectory() as folder:
            local=Path(folder)/"empty.sqlite"
            backup=Path(folder)/"backup.sqlite"
            with mod.openLocalDb(str(local)) as db:
                with self.assertRaises(mod.MachineLayerError):
                    mod.backupSnapshot(db,backup,self.manifest)
            self.assertFalse(backup.exists())
    def test_database_rejects_unsafe_path(self):
        with self.assertRaises(mod.MachineLayerError): mod.openLocalDb("/tmp/test-no-extension")

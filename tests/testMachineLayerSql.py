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
    def test_database_rejects_unsafe_path(self):
        with self.assertRaises(mod.MachineLayerError): mod.openLocalDb("/tmp/test-no-extension")

import copy
import json
import unittest
from pathlib import Path
from tools.finiteDemoQueue import resolve

ROOT = Path(__file__).resolve().parents[1]
SOURCE = json.loads((ROOT / "game/demo/demoAssetPriorityV1.json").read_text(encoding="utf-8"))

class DemoQueueTest(unittest.TestCase):
    def test_four_slots_without_inventing_game_names(self):
        self.assertEqual(len(SOURCE["gameSlots"]), 4)
        self.assertEqual(SOURCE["gameSlots"][0]["confirmedProject"], "firstNightCircuit")
        for row in SOURCE["gameSlots"][1:]:
            self.assertIsNone(row["confirmedProject"])
    def test_generator_is_finite_and_never_posts(self):
        self.assertEqual(SOURCE["generator"]["maxNights"], 3)
        self.assertEqual(SOURCE["generator"]["stepsPerNight"], 4)
        self.assertFalse(SOURCE["generator"]["autoPublish"])
        self.assertFalse(SOURCE["boundedWork"]["generateNewTasksWhenEmpty"])
    def test_dag_is_acyclic_and_current_queue_is_read_only(self):
        receipt = resolve(SOURCE)
        self.assertEqual(receipt["newTasksGenerated"], 0)
        self.assertFalse(receipt["terminal"])
        self.assertFalse(receipt["automaticExecution"])
        self.assertFalse(receipt["publicPublication"])
        self.assertIn("demo-01", receipt["readyNow"])
        self.assertNotIn("release-01", receipt["readyNow"])
    def test_reject_false_done(self):
        doc = copy.deepcopy(SOURCE)
        doc["boundedWork"]["queue"][0]["state"] = "DONE"
        with self.assertRaisesRegex(ValueError, "RED_FAKE_COMPLETION"):
            resolve(doc)
    def test_reject_cycles_or_new_dependencies(self):
        doc = copy.deepcopy(SOURCE)
        doc["boundedWork"]["queue"][0]["dependsOn"] = ["release-01"]
        with self.assertRaisesRegex(ValueError, "RED_CYCLIC_DEMO_QUEUE"):
            resolve(doc)
        doc = copy.deepcopy(SOURCE)
        doc["boundedWork"]["queue"][0]["dependsOn"] = ["phantom"]
        with self.assertRaisesRegex(ValueError, "RED_UNKNOWN_DEPENDENCY"):
            resolve(doc)
    def test_full_evidenced_queue_exhausts_without_spawning_tasks(self):
        doc = copy.deepcopy(SOURCE)
        for row in doc["boundedWork"]["queue"]:
            row["state"] = "DONE"
            row["evidenceRefs"] = ["synthetic-test-only"]
        receipt = resolve(doc)
        self.assertTrue(receipt["terminal"])
        self.assertEqual(receipt["readyNow"], [])
        self.assertEqual(receipt["newTasksGenerated"], 0)

if __name__ == "__main__":
    unittest.main()

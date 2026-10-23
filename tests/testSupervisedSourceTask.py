import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("sourceTask", Path(__file__).resolve().parents[1] / "tools/supervisedSourceTask.py")
task = importlib.util.module_from_spec(spec)
spec.loader.exec_module(task)


class SourceTaskTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git("init", "-q")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        names = [f"agent{i}" for i in range(15)]
        docs = [{"requiredAgents": names}, {"agents": dict.fromkeys(names, {})},
                {"registeredAgents": names, "state": "QUARANTINED", "activeTaskWorkersAllowed": False}]
        for name, doc in zip(task.FILES, docs):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(doc))
        self.commit()

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.root, text=True).strip()

    def commit(self):
        self.git("add", ".")
        self.git("commit", "-qm", "fixture")
        self.sha = self.git("rev-parse", "HEAD")

    def run_task(self, sha=None):
        return task.inspect(self.root, sha or self.sha, "testTask")

    def test_valid_does_not_claim_agents(self):
        result = self.run_task()
        self.assertEqual(result["status"], "COMPLETED")
        self.assertEqual(result["agentsActivated"], [])
        self.assertFalse(result["inferenceExecuted"])
        self.assertEqual(len(result["contractHashes"]), 3)

    def test_wrong_source(self):
        self.assertEqual(self.run_task("0" * 40)["status"], "FAILED")

    def test_dirty_source(self):
        (self.root / task.FILES[0]).write_text("{}")
        self.assertEqual(self.run_task()["status"], "FAILED")

    def test_malformed_committed_contract(self):
        (self.root / task.FILES[0]).write_text("not json")
        self.commit()
        self.assertEqual(self.run_task()["status"], "FAILED")

    def test_no_inferred_release(self):
        path = self.root / task.FILES[2]
        doc = json.loads(path.read_text())
        doc["state"] = "RELEASED"
        path.write_text(json.dumps(doc))
        self.commit()
        self.assertEqual(self.run_task()["status"], "FAILED")

    def test_symlink_escape(self):
        path = self.root / task.FILES[0]
        path.unlink()
        path.symlink_to("/etc/hosts")
        self.commit()
        self.assertEqual(self.run_task()["status"], "FAILED")


if __name__ == "__main__":
    unittest.main()

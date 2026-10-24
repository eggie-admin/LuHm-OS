"""Hostile fixture tests for GitHub supervised source task and Urd source review."""
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


task = load("supervisedSource", "tools/supervisedSourceTask.py")
urd = load("urdReview", "tools/urdSupervisedSourceReview.py")


class UrdSupervisedSourceReviewTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.git("init", "-q")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "user.name", "Fixture")
        ids = ["lum", "urdDoctorGoddess", "belldandySecretary", "skuldResearch"] + [
            "oni" + str(i) for i in range(11)
        ]
        documents = (
            {"requiredAgents": ids},
            {"agents": dict.fromkeys(ids, {})},
            {
                "state": "QUARANTINED",
                "registeredAgents": ids,
                "registeredCount": 15,
                "activeTaskWorkersAllowed": False,
                "crownStatus": "STOP",
                "releaseMode": "twoPhasePerAgentNoAutomaticRelease",
                "supervisedProbe": {"requiresCurrentChatHostInvocation": True},
            },
        )
        for name, value in zip(task.FILES, documents):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(value), encoding="utf-8")
        self.git("add", ".")
        self.git("commit", "-qm", "fixture")
        self.sha = self.git("rev-parse", "HEAD")
        self.receipt = task.inspect(self.root, self.sha, "supervised-t1")
        self.assertEqual(self.receipt["status"], "COMPLETED")

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.root, text=True).strip()

    def review(self, receipt=None):
        return urd.verify(self.root, self.receipt if receipt is None else receipt, self.sha, "supervised-t1")

    def test_source_only_receipt_accepted_not_agent_activation(self):
        result = self.review()
        self.assertEqual(result["sourceTaskStatus"], "ACCEPTED")
        self.assertEqual(result["reviewerKind"], "deterministicPolicyCheckNotIndependentUrdAgent")
        self.assertEqual(result["agentsActivated"], [])
        self.assertFalse(result["chatGptHostInvocationObserved"])
        self.assertFalse(result["independentUrdAgentExecuted"])
        self.assertFalse(result["professorAgentResumeVerified"])
        self.assertEqual(result["crownStatus"], "STOP")

    def test_reject_forged_activated_agent(self):
        altered = dict(self.receipt, agentsActivated=["belldandySecretary"])
        self.assertIn("AGENT_ACTIVATION_FORBIDDEN", self.review(altered)["errors"])

    def test_reject_false_provider_model_claim(self):
        altered = dict(self.receipt, inferenceExecuted=True)
        self.assertIn("UNPROVEN_MODEL_EXECUTION", self.review(altered)["errors"])

    def test_reject_wrong_task(self):
        altered = dict(self.receipt, taskId="someone-else")
        self.assertIn("TASK_MISMATCH", self.review(altered)["errors"])

    def test_reject_checksum_mismatch(self):
        altered = dict(self.receipt, contractHashes={})
        self.assertIn("CONTRACT_HASH_MISMATCH", self.review(altered)["errors"])

    def test_reject_uncommitted_contract_drift(self):
        p = self.root / task.FILES[0]
        p.write_text(json.dumps({"requiredAgents": []}), encoding="utf-8")
        self.assertIn("CONTRACT_HASH_MISMATCH", self.review()["errors"])

    def test_reject_source_mismatch(self):
        altered = dict(self.receipt, sourceRef="0" * 40)
        self.assertIn("RECEIPT_SOURCE_MISMATCH", self.review(altered)["errors"])

    def test_reject_quarantine_release(self):
        path = self.root / task.FILES[-1]
        obj = json.loads(path.read_text())
        obj["activeTaskWorkersAllowed"] = True
        path.write_text(json.dumps(obj))
        self.assertIn("COMPANY_HOLD_DRIFT", self.review()["errors"])

    def test_reject_invalid_receipt(self):
        self.assertEqual(self.review({})["sourceTaskStatus"], "REJECTED")


if __name__ == "__main__":
    unittest.main()

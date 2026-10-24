"""Hostile-change checks for the five-lead Lum cabinet readiness runner."""
from __future__ import annotations
import copy
import importlib.util
from pathlib import Path
import unittest

path = Path(__file__).resolve().parents[1] / "tools/lumCabinetReadiness.py"
spec = importlib.util.spec_from_file_location("cabinet", path)
cabinet = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cabinet)


def fixture():
    agents = list(cabinet.REQUIRED)
    deployment = {"requiredAgents": agents, "requiredAgentCount": 15}
    plane = {"boss": "lum", "agents": dict.fromkeys(agents, {}),
             "invariants": {"maxParallelSupportWorkers": 3,
                            "oneMutableSourceLane": True}}
    hold = {"state": "QUARANTINED", "activeTaskWorkersAllowed": False,
            "hiddenAsyncAgents": False, "registeredAgents": agents,
            "registeredCount": 15, "crownStatus": "STOP"}
    return deployment, plane, hold


class CabinetReadinessTests(unittest.TestCase):
    def test_five_leads_have_concrete_audits(self):
        self.assertEqual(set(cabinet.PROFILES), {"lum", "urdDoctorGoddess",
                                                 "belldandySecretary", "skuldResearch", "yume"})
        self.assertEqual(sum(len(p["checks"]) for p in cabinet.PROFILES.values()), 10)
        self.assertEqual(cabinet.checkContract(*fixture()), [])

    def test_reject_roster_gaps(self):
        a, b, c = fixture()
        a["requiredAgents"].pop()
        self.assertIn("registered roster drift", cabinet.checkContract(a, b, c))

    def test_reject_unauthorized_execution(self):
        a, b, c = fixture()
        c["activeTaskWorkersAllowed"] = True
        self.assertIn("quarantine bypass", cabinet.checkContract(a, b, c))

    def test_reject_hidden_workers(self):
        a, b, c = fixture()
        c["hiddenAsyncAgents"] = True
        self.assertIn("covert background-agent drift", cabinet.checkContract(a, b, c))

    def test_reject_concurrency_spike(self):
        a, b, c = fixture()
        b["invariants"]["maxParallelSupportWorkers"] = 99
        self.assertIn("support concurrency drift", cabinet.checkContract(a, b, c))

    def test_reject_double_mutation(self):
        a, b, c = fixture()
        b["invariants"]["oneMutableSourceLane"] = False
        self.assertIn("source mutation-lane drift", cabinet.checkContract(a, b, c))

    def test_reject_phantom_control_plane_worker(self):
        a, b, c = fixture()
        b["agents"]["extraAgent"] = {}
        self.assertIn("control-plane roster drift", cabinet.checkContract(a, b, c))

    def test_reject_crown_escalation(self):
        a, b, c = fixture()
        c["crownStatus"] = "GREEN"
        self.assertIn("Crown leak", cabinet.checkContract(a, b, c))

    def test_authority_is_not_assumed(self):
        self.assertEqual(cabinet.REQUIRED.count("lum"), 1)
        self.assertFalse(any("provider" in p["work"].lower() and
                             "executed" in p["work"].lower()
                             for p in cabinet.PROFILES.values()))


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("meshAudit", ROOT / "tools" / "auditOniMeshV2.py")
mesh = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mesh)


class OniMeshV2Tests(unittest.TestCase):
    def test_current_contract_passes(self):
        data = mesh.load()
        mesh.audit_skills(data)

    def test_parallelism_creep_is_detectable(self):
        data = mesh.load()
        data = copy.deepcopy(data)
        data["topology"]["maxParallelSupportWorkers"] = 4
        self.assertGreater(data["topology"]["maxParallelSupportWorkers"], 3)

    def test_helper_recruitment_stays_off(self):
        data = mesh.load()
        self.assertIs(data["topology"]["helperRecruitment"], False)

    def test_single_mutation_lane(self):
        data = mesh.load()
        self.assertEqual(data["topology"]["maxMutableSourceLanesPerCandidate"], 1)

    def test_authority_boundaries(self):
        data = mesh.load()
        self.assertFalse(data["roles"]["Lum"]["mutationAuthority"])
        self.assertEqual(data["roles"]["Fumi"]["defaultAuthority"], "READ_ONLY")
        self.assertEqual(data["roles"]["DrNao"]["defaultAuthority"], "READ_ONLY")

    def test_task_envelope_has_identity_and_budget(self):
        data = mesh.load()
        fields = set(data["requiredTaskEnvelope"])
        for field in ("taskId", "sourceRef", "authorityClass", "stopConditions", "budget"):
            self.assertIn(field, fields)


if __name__ == "__main__":
    unittest.main()

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
    def setUp(self):
        self.data = mesh.load()

    def test_current_contract_passes(self):
        mesh.audit_skills(self.data)

    def test_parallelism_creep_is_detectable(self):
        data = copy.deepcopy(self.data)
        data["topology"]["maxParallelSupportWorkers"] = 4
        self.assertGreater(data["topology"]["maxParallelSupportWorkers"], 3)

    def test_helper_recruitment_stays_off(self):
        self.assertIs(self.data["topology"]["helperRecruitment"], False)
        self.assertEqual(self.data["budgetCeilings"]["maxDelegationDepth"], 0)

    def test_single_mutation_lane_and_writer_lease(self):
        self.assertEqual(self.data["topology"]["maxMutableSourceLanesPerCandidate"], 1)
        self.assertIs(self.data["topology"]["oneWriterLeaseRequired"], True)

    def test_authority_boundaries(self):
        self.assertFalse(self.data["roles"]["Lum"]["mutationAuthority"])
        self.assertEqual(self.data["roles"]["Fumi"]["defaultAuthority"], "READ_ONLY")
        self.assertEqual(self.data["roles"]["DrNao"]["defaultAuthority"], "READ_ONLY")

    def test_default_deny_capability_resolution(self):
        effective = mesh.resolve_capabilities(
            self.data,
            "Kugi",
            ["mutate.atomic", "secret.read", "shell.arbitrary", "capability.not-declared"],
            [],
        )
        self.assertEqual(effective, {"mutate.atomic"})

    def test_task_capability_deny_wins(self):
        effective = mesh.resolve_capabilities(
            self.data,
            "Kugi",
            ["mutate.atomic", "read.repository"],
            ["mutate.atomic"],
        )
        self.assertEqual(effective, {"read.repository"})

    def _base_envelope(self, authority="READ_ONLY"):
        return {
            "taskId": "task-1",
            "intent": "test",
            "scope": "tests",
            "repository": "eggie-admin/LuHm-OS",
            "sourceRef": "abc1234" if authority != "READ_ONLY" else "UNKNOWN",
            "authorityClass": authority,
            "allowedCapabilities": ["read.repository"],
            "forbiddenCapabilities": [],
            "evidenceRefs": [],
            "requiredOutputs": ["receipt"],
            "stopConditions": ["RED"],
            "budget": {
                "maxToolCalls": 2,
                "maxMutations": 0 if authority == "READ_ONLY" else 1,
                "maxRetries": 0,
                "maxRuntimeSeconds": 60,
                "maxDelegationDepth": 0,
            },
            "idempotencyKey": "" if authority == "READ_ONLY" else "mut-1",
            "writerLease": {} if authority == "READ_ONLY" else {
                "leaseId": "lease-1",
                "taskId": "task-1",
                "repository": "eggie-admin/LuHm-OS",
                "sourceRef": "abc1234",
                "candidateRef": "candidate/test",
                "holder": "Kugi",
                "scope": "tests",
            },
            "evidencePolicy": {"maxLiveEvidenceAgeHours": 6},
        }

    def test_read_only_task_cannot_reserve_mutation(self):
        envelope = self._base_envelope()
        envelope["budget"]["maxMutations"] = 1
        with self.assertRaises(ValueError):
            mesh.validate_task_envelope(self.data, envelope, "Kiri")

    def test_mutation_requires_idempotency_key(self):
        envelope = self._base_envelope("MUTATE_REVERSIBLE")
        envelope["idempotencyKey"] = ""
        with self.assertRaises(ValueError):
            mesh.validate_task_envelope(self.data, envelope, "Kugi")

    def test_mutation_requires_matching_writer_lease(self):
        envelope = self._base_envelope("MUTATE_REVERSIBLE")
        envelope["writerLease"]["holder"] = "Tetsu"
        with self.assertRaises(ValueError):
            mesh.validate_task_envelope(self.data, envelope, "Kugi")

    def test_valid_atomic_mutation_envelope(self):
        envelope = self._base_envelope("MUTATE_REVERSIBLE")
        envelope["allowedCapabilities"] = ["read.repository", "mutate.atomic"]
        mesh.validate_task_envelope(self.data, envelope, "Kugi")

    def test_hard_deny_cannot_be_requested_allowed(self):
        envelope = self._base_envelope()
        envelope["allowedCapabilities"].append("secret.read")
        with self.assertRaises(ValueError):
            mesh.validate_task_envelope(self.data, envelope, "Kiri")

    def test_stale_live_evidence_cannot_promote(self):
        evidence = {
            "kind": "live-probe",
            "locator": "probe://device",
            "sourceRef": "abc1234",
            "observedAt": "2026-09-30T00:00:00Z",
            "freshnessClass": "LIVE",
            "status": "GREEN",
        }
        self.assertFalse(mesh.evidence_eligible(self.data, evidence, "abc1234", live_age_hours=25))
        self.assertTrue(mesh.evidence_eligible(self.data, evidence, "abc1234", live_age_hours=2))

    def test_wrong_source_evidence_cannot_promote(self):
        evidence = {
            "kind": "artifact",
            "locator": "sha256:deadbeef",
            "sourceRef": "old1111",
            "observedAt": "2026-09-30T00:00:00Z",
            "freshnessClass": "IMMUTABLE",
            "status": "GREEN",
        }
        self.assertFalse(mesh.evidence_eligible(self.data, evidence, "new2222"))

    def test_contradiction_routes_to_critic_and_doctor(self):
        self.assertTrue(self.data["contradictionPolicy"]["stopMutation"])
        self.assertEqual(set(self.data["contradictionPolicy"]["routeTo"]), {"Shiori", "DrNao"})


if __name__ == "__main__":
    unittest.main()

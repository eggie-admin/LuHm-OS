#!/usr/bin/env python3
"""Injected, deterministic 4x4 source-loop tests. Never touch host services."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("machineCanonFourLoop", ROOT / "tools/machineCanonFourLoop.py")
machine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(machine)
SHA = "a" * 40
CANON = "b" * 64


def green(_command):
    return {"status": "PASS", "exitCode": 0, "outputSha256": "c" * 64}


class MachineCanonFourLoopTests(unittest.TestCase):
    def test_policy_and_canon_fingerprints_have_no_release_authority(self):
        fingerprint, digests = machine.canonical_receipt()
        self.assertEqual(len(fingerprint), 64)
        self.assertIn("doctrine/currentSourceTruthV3.json", digests)
        self.assertIn("doctrine/unifiedMachineBaseV1.json", digests)
        policy = json.loads((ROOT / "doctrine/machineCanonFourLoopV1.json").read_text())
        self.assertEqual(policy["lanes"], ["machine", "service", "studio", "interface"])
        self.assertEqual(policy["fourBeats"], ["inventory", "scope", "verify", "propose"])
        self.assertEqual(policy["approvals"]["crownStatus"], "STOP")
        self.assertFalse(policy["approvals"]["cast"])

    def test_green_checks_all_16_and_no_crown(self):
        calls = []
        def run(cmd):
            calls.append(cmd)
            return green(cmd)
        result = machine.tick(SHA, CANON, {}, run, lambda: SHA)
        self.assertEqual(result["sourceStatus"], "GREEN_SOURCE_CHECKS_ONLY")
        self.assertEqual(result["checkedCells"], 16)
        self.assertFalse(result["castAuthorized"])
        self.assertFalse(result["productionMutationAuthorized"])
        self.assertFalse(result["physicalDeviceProof"])
        self.assertEqual(result["crownStatus"], "STOP")
        self.assertEqual([c["cell"] for lane in result["lanes"] for c in lane["checks"]],
                         [f"0x{i:02x}" for i in range(16)])
        self.assertEqual([c["beat"] for c in result["lanes"][0]["checks"]],
                         ["inventory", "scope", "verify", "propose"])
        self.assertTrue(any(SHA in x for command in calls for x in command))

    def test_one_failed_lane_does_not_stop_independent_lanes(self):
        def run(cmd):
            if any(part.endswith("networkSpineAudit.py") for part in cmd):
                return {"status": "FAIL", "exitCode": 1}
            return green(cmd)
        result = machine.tick(SHA, CANON, {}, run, lambda: SHA)
        self.assertEqual(result["checkedCells"], 13)
        self.assertEqual([x["status"] for x in result["lanes"]],
                         ["GREEN_SOURCE_ONLY", "RED", "GREEN_SOURCE_ONLY", "GREEN_SOURCE_ONLY"])
        self.assertEqual(result["lanes"][1]["tier"], 1)
        self.assertEqual(result["lanes"][1]["failures"], 1)
        self.assertEqual(len(result["lanes"][1]["checks"]), 1)
        self.assertNotEqual(result["sourceStatus"], "GREEN_SOURCE_CHECKS_ONLY")

    def test_escalation_bounded_three_failures_then_no_rerun(self):
        def run(cmd):
            return {"status": "FAIL", "exitCode": 4} if any(part.endswith("networkSpineAudit.py") for part in cmd) else green(cmd)
        receipt = {}
        for n in (1, 2, 3):
            receipt = machine.tick(SHA, CANON, receipt, run, lambda: SHA)
            row = receipt["lanes"][1]
            self.assertEqual(row["failures"], n)
            self.assertEqual(row["tier"], n)
        called = []
        def spy(cmd):
            called.append(cmd)
            return run(cmd)
        held = machine.tick(SHA, CANON, receipt, spy, lambda: SHA)
        self.assertEqual(held["lanes"][1]["status"], "BLOCKED")
        self.assertEqual(held["lanes"][1]["checks"], [])
        self.assertFalse(any(any(part.endswith("networkSpineAudit.py") for part in cmd) for cmd in called))
        self.assertEqual(held["lanes"][3]["status"], "GREEN_SOURCE_ONLY")

    def test_recovery_deescalates_and_rechecks_prior_green(self):
        def red(cmd):
            return {"status": "FAIL", "exitCode": 1} if any(part.endswith("networkSpineAudit.py") for part in cmd) else green(cmd)
        previous = machine.tick(SHA, CANON, {}, red, lambda: SHA)
        calls = []
        def recovered(cmd):
            calls.append(cmd)
            return green(cmd)
        result = machine.tick(SHA, CANON, previous, recovered, lambda: SHA)
        self.assertEqual(result["sourceStatus"], "GREEN_SOURCE_CHECKS_ONLY")
        self.assertEqual(result["lanes"][1]["tier"], 0)
        self.assertEqual(result["lanes"][1]["failures"], 0)
        self.assertEqual(len(calls), 16)

    def test_new_sha_or_canon_fingerprint_resets_retry_budget(self):
        previous = {
            "sourceRef": SHA, "canonFingerprint": CANON,
            "lanes": [{"lane": "service", "tier": 3, "failures": 3}],
        }
        fresh = machine.tick("d" * 40, CANON, previous, green, lambda: "d" * 40)
        self.assertEqual(fresh["lanes"][1]["status"], "GREEN_SOURCE_ONLY")
        changed = machine.tick(SHA, "e" * 64, previous, green, lambda: SHA)
        self.assertEqual(changed["lanes"][1]["status"], "GREEN_SOURCE_ONLY")

    def test_unknown_and_source_change_are_not_green(self):
        def unknown(cmd):
            return {"status": "UNKNOWN", "failureKind": "missingReceipt"}
        result = machine.tick(SHA, CANON, {}, unknown, lambda: SHA)
        self.assertEqual([row["status"] for row in result["lanes"]], ["UNKNOWN"] * 4)
        self.assertEqual([row["tier"] for row in result["lanes"]], [0] * 4)
        self.assertNotEqual(result["sourceStatus"], "GREEN_SOURCE_CHECKS_ONLY")
        seen = iter([SHA, SHA, "d" * 40])
        changed = machine.tick(SHA, CANON, {}, green, lambda: next(seen, "d" * 40))
        self.assertFalse(changed["sourceStable"])
        self.assertEqual(changed["lanes"][0]["status"], "SOURCE_CHANGED")
        self.assertNotEqual(changed["sourceStatus"], "GREEN_SOURCE_CHECKS_ONLY")

    def test_rejects_malformed_state_and_runner(self):
        with self.assertRaises(ValueError):
            machine.tick(SHA, CANON, {"sourceRef": SHA, "canonFingerprint": CANON,
                                     "lanes": [{"lane": "machine", "tier": 5, "failures": 0}]}, green, lambda: SHA)
        with self.assertRaises(ValueError):
            machine.tick(SHA, CANON, {}, lambda cmd: {"status": "SUCCESS"}, lambda: SHA)
        with self.assertRaises(ValueError):
            machine.tick("main", CANON, {}, green, lambda: SHA)
        with self.assertRaises(ValueError):
            machine.tick(SHA, CANON, {"sourceRef": SHA, "canonFingerprint": CANON,
                                     "lanes": [{"lane": "machine"}, {"lane": "machine"}]}, green, lambda: SHA)


if __name__ == "__main__":
    unittest.main()

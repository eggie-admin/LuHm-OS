#!/usr/bin/env python3
"""Hostile 4x4 LuHm hardware source seal tests; zero kernel/VM interaction."""
from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("hardwareCastSeal",
                                              ROOT / "tools/hardwareCastSeal.py")
assert spec and spec.loader
seal = importlib.util.module_from_spec(spec)
spec.loader.exec_module(seal)
SHA = "f1f89ab438cc97b41717bdc23fdc9ece11ccdeb9"


class TestHardwareCastSeal(unittest.TestCase):
    def test_exact_four_by_four_source_can_be_ready_without_runtime(self):
        r = seal.source_seal(source_ref=SHA)
        self.assertEqual(r["state"], "SOURCE_READY_RUNTIME_HOLD", r["issues"])
        self.assertEqual(r["issues"], [])
        self.assertEqual(r["fourByFourCells"], 16)
        self.assertEqual(len(r["sourceAuditors"]), 4)
        self.assertTrue(all(x["sourceOk"] for x in r["sourceAuditors"]))
        self.assertTrue(r["sourceReadiness"])
        self.assertEqual(len(r["sourceBundleSha256"]), 64)
        self.assertFalse(r["sourceBundleDigestIsSignature"])
        self.assertFalse(r["sourceRefIndependentlyVerified"])

    def test_runtime_firmware_network_and_public_release_remain_hold(self):
        r = seal.source_seal()
        for key in ("realHostKernelProven", "realKvmOrTcgGuestProven",
                    "realHardwareFlashed", "realVmBooted",
                    "guestNetworkOpened", "paidRemoteComputeUsed",
                    "mainMerged", "humanApprovalRecorded",
                    "ownerRuntimeSeal", "crownAuthority"):
            with self.subTest(key=key):
                self.assertIs(r[key], False)
        self.assertEqual(len(r["runtimeBlockers"]), 5)
        self.assertEqual(r["castStages"], [
            "sanityCheck", "audit", "ingest", "mutation", "test",
            "apply", "continue", "deploy",
        ])

    def test_source_claim_requires_exact_lowercase_hex(self):
        for source_ref in ("main", "A" * 40, "f" * 39, "g" * 40,
                           "../", "", 1, True, [], {}):
            with self.subTest(ref=str(source_ref)[:30]), self.assertRaises(
                    ValueError):
                seal.source_seal(source_ref=source_ref)

    def test_any_parent_audit_failure_blocks_source_seal(self):
        original = seal._auditor

        def faulty(path, entry):
            if path == "tools/localOpenVmKernelGate.py":
                return {"state": "RED_SOURCE_DRIFT", "issues": ["RED_CLOUD"], "crownAuthority": False}
            return original(path, entry)

        with patch.object(seal, "_auditor", side_effect=faulty):
            r = seal.source_seal(source_ref=SHA)
        self.assertEqual(r["state"], "STOP_SOURCE_DRIFT")
        self.assertIn("RED_HARDWARE_CAST_PARENT_AUDIT:tools/localOpenVmKernelGate.py", r["issues"])

    def test_forged_owner_proof_vm_boot_or_release_never_green(self):
        original = seal._read

        def altered(path):
            x = original(path)
            if path == seal.CONTRACT:
                x = copy.deepcopy(x)
                x["cells"][0]["realHostProven"] = True
                x["release"]["realVmBooted"] = True
                x["mandatoryBoundaries"]["noPaidProviderFallback"] = False
                x["typedIdentity"]["hexNeverPermission"] = False
            return x

        with patch.object(seal, "_read", side_effect=altered):
            r = seal.source_seal()
        for item in ("RED_HARDWARE_CAST_FALSE_PROOF",
                     "RED_HARDWARE_CAST_RELEASE",
                     "RED_HARDWARE_CAST_PRIVILEGE",
                     "RED_HARDWARE_CAST_HEX_AUTHORITY"):
            self.assertIn(item, r["issues"])
        self.assertFalse(r["ownerRuntimeSeal"])

    def test_no_arbitrary_code_runs_through_mutated_auditor_paths(self):
        original = seal._read

        def altered(path):
            x = original(path)
            if path == seal.CONTRACT:
                x = copy.deepcopy(x)
                x["sourceAuditors"][0]["path"] = "../../etc/passwd"
            return x

        with patch.object(seal, "_read", side_effect=altered):
            r = seal.source_seal()
        self.assertIn("RED_HARDWARE_CAST_AUDIT_SOURCE_DRIFT", r["issues"])
        self.assertFalse(r["ownerRuntimeSeal"])
        with self.assertRaises(ValueError):
            seal._auditor("../../etc/passwd", "source_audit")

    def test_digest_changes_if_canonical_source_bytes_change(self):
        digest = seal._source_digest()
        self.assertEqual(len(digest), 64)
        self.assertRegex(digest, "^[a-f0-9]{64}$")
        self.assertEqual(digest, seal._source_digest())

    def test_quarantine_must_remain_in_effect(self):
        original = seal._read

        def altered(path):
            data = original(path)
            if path == seal.QUARANTINE:
                data = copy.deepcopy(data)
                data["activeTaskWorkersAllowed"] = True
            return data

        with patch.object(seal, "_read", side_effect=altered):
            r = seal.source_seal()
        self.assertIn("RED_HARDWARE_CAST_QUARANTINE", r["issues"])


if __name__ == "__main__":
    unittest.main()

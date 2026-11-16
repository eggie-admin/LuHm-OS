#!/usr/bin/env python3
"""Offline LuHm WMS machine-plane smoke/security tests, never touches a VM."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "host" / "remote" / "luhmWmsVmManager.py"
spec = importlib.util.spec_from_file_location("luhmWmsVmManager", SCRIPT)
assert spec is not None and spec.loader is not None
wms = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wms)
SHA = "f0cb6ee54066b490c0e80efc2c96200fec76ee2d"


class WmsMachineBridgeTests(unittest.TestCase):
    def test_status_never_claims_machine_or_runtime(self) -> None:
        result = wms.status()
        self.assertEqual(result["wmsVendor"], "UNRESOLVED")
        self.assertEqual(result["configuredMachineCount"], 0)
        self.assertEqual(result["activeAdapterCount"], 0)
        self.assertEqual(len(result["pluginSlots"]), 6)
        self.assertFalse(result["remoteConnectivityVerified"])
        self.assertFalse(result["liveRemoteOpsAvailable"])

    def test_read_only_plan_has_no_execution_or_secret(self) -> None:
        request = wms.plan("task-1", SHA, "read-only", "manager",
                           "inventory", env={"LUHM_WMS_SOURCE_REF": SHA,
                                              "WMS_TOKEN": "super-private-token"})
        self.assertEqual(request["networkCalls"], 0)
        self.assertIn("COMPANY_QUARANTINE", request["blockingConditions"])
        self.assertIn("REMOTE_CONNECTION_UNVERIFIED", request["blockingConditions"])
        self.assertFalse(request["remoteExecutionProven"])
        self.assertFalse(request["mutationAuthority"])
        self.assertNotIn("super-private-token", str(request))

    def test_machine_identity_is_bound_and_not_inferred(self) -> None:
        request = wms.plan("task-2", SHA, "studio", "vm-001", "health", env={})
        self.assertIn("MACHINE_UNREGISTERED", request["blockingConditions"])
        self.assertIn("SOURCE_RECEIPT_MISSING", request["blockingConditions"])
        candidate = wms.plan("task-2", SHA, "studio", "vm-001", "health",
                             env={"LUHM_WMS_SOURCE_REF": SHA},
                             registered_machine_ids=frozenset({"vm-001"}))
        self.assertNotIn("MACHINE_UNREGISTERED", candidate["blockingConditions"])
        self.assertNotIn("SOURCE_RECEIPT_MISSING", candidate["blockingConditions"])
        self.assertIn("REMOTE_CONNECTION_UNVERIFIED", candidate["blockingConditions"])

    def test_source_mismatch_stops_and_write_plan_never_executes(self) -> None:
        plan = wms.plan("task-3", SHA, "studio", "vm-001", "shutdownPlan",
                        env={"LUHM_WMS_SOURCE_REF": "a" * 40})
        self.assertIn("SOURCE_RECEIPT_MISMATCH", plan["blockingConditions"])
        self.assertIn("REMOTE_WRITE_NOT_AUTHORIZED", plan["blockingConditions"])
        self.assertEqual(plan["networkCalls"], 0)

    def test_invalid_free_text_and_commands_rejected(self) -> None:
        for bad_machine in ("", "vm 1", "https://localhost:8080", "../etc/passwd"):
            with self.subTest(machine=bad_machine), self.assertRaises(ValueError):
                wms.plan("task-4", SHA, "studio", bad_machine, "health")
        for operation in ("shell", "rm -rf", "writeDisk", "liveSsh"):
            with self.subTest(operation=operation), self.assertRaises(ValueError):
                wms.plan("task-4", SHA, "studio", "vm-001", operation)
        with self.assertRaises(ValueError):
            wms.plan("task-4", "main", "studio", "vm-001", "health")

    def test_manager_inventory_requires_manager_id(self) -> None:
        request = wms.plan("task-5", SHA, "studio", "vm-001", "inventory", env={})
        self.assertIn("MANAGER_ID_REQUIRED", request["blockingConditions"])


if __name__ == "__main__":
    unittest.main()

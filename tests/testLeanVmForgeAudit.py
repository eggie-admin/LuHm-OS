#!/usr/bin/env python3
"""No-network tests for the actual LuHm VM forge/source-rights alignment."""
from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "leanVmForgeAudit", ROOT / "tools/leanVmForgeAudit.py")
assert spec and spec.loader
audit_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit_module)
SHA = "f0cb6ee54066b490c0e80efc2c96200fec76ee2d"


class TestLeanVmForge(unittest.TestCase):
    def test_actual_render_sql_proxy_netplan_source_alignment(self):
        result = audit_module.audit()
        self.assertEqual(result["status"], "SOURCE_CONSISTENT_NOT_RUNTIME_PROVEN", result)
        self.assertEqual(result["rootLicense"], "GPL-3.0")
        self.assertGreaterEqual(result["sourceFileCount"], 20)
        self.assertEqual(result["providerFreeTierCandidates"], 4)
        self.assertEqual(result["renderCanonicalServiceCount"], 2)
        self.assertEqual(len(result["sourceFileDigestSha256"]), 64)
        self.assertEqual(len(result["verifiedSqliteTables"]), 6)
        self.assertFalse(result["netplanApplied"])
        self.assertFalse(result["proxyReconfigured"])
        self.assertFalse(result["apache2MigrationAuthorized"])
        self.assertFalse(result["cloudAccountsChecked"])
        self.assertFalse(result["greenAuthority"])

    def test_vm_plan_always_fails_closed_without_real_account_and_host(self):
        for provider in ("oracle", "google", "azure", "aws"):
            with self.subTest(provider=provider):
                plan = audit_module.plan_vm(
                    "forgeTask", SHA, "studioScope", "demoVm", provider)
                self.assertEqual(plan["state"], "HOLD_EXTERNAL_VM_ACCOUNT_AND_IDENTITY")
                self.assertFalse(plan["virtualMachineConnected"])
                self.assertFalse(plan["netplanInterfaceObserved"])
                self.assertFalse(plan["sourceRefObservedAsCurrentGitHubHead"])
                self.assertEqual(plan["vmActionsExecuted"], 0)
                self.assertEqual(plan["networkCalls"], 0)
                self.assertFalse(plan["mutationAllowed"])

    def test_bad_input_never_becomes_a_shell_vm_or_proxy_route(self):
        for value in ("", "../etc", "https://example.com", "first vm", "_x"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                audit_module.plan_vm("forgeTask", SHA, "studioScope", value, "oracle")
        with self.assertRaises(ValueError):
            audit_module.plan_vm("forgeTask", "main", "studioScope", "demoVm", "oracle")
        with self.assertRaises(ValueError):
            audit_module.plan_vm("forgeTask", SHA, "studioScope", "demoVm", "unknown")

    def test_duplicate_yaml_keys_and_object_tags_rejected(self):
        with self.assertRaises(ValueError):
            audit_module.parse_yaml("network:\n  version: 2\n  version: 3\n")
        with self.assertRaises(Exception):
            audit_module.parse_yaml("network: !!python/object/apply:os.system ['id']")
        with self.assertRaises(ValueError):
            audit_module.parse_yaml("x: " + "a" * 150001)

    def test_license_relabel_detected_without_editing_actual_license(self):
        original = audit_module._json
        def forged(path):
            row = original(path)
            if path == audit_module.CONTRACT:
                row = copy.deepcopy(row)
                row["actualRootLicense"] = "Apache-2.0"
                row["licenseDecision"] = "AUTO_RELICENSE"
            return row
        with patch.object(audit_module, "_json", side_effect=forged):
            check = audit_module.audit()
        self.assertFalse(check["sourceConsistent"])
        self.assertIn("RED_ROOT_LICENSE_MISCLASSIFIED", check["issues"])
        self.assertIn("RED_AUTO_APACHE_RELICENSE", check["issues"])

    def test_proxy_and_free_gpu_bypass_detected(self):
        original = audit_module._json
        def forged(path):
            row = original(path)
            if path == audit_module.CONTRACT:
                row = copy.deepcopy(row)
                row["proxy"]["forbidPublicSql"] = False
                row["freeVmResearch"]["providers"][0]["gpuFree"] = True
                row["machineProof"]["noAutoDeploy"] = False
            return row
        with patch.object(audit_module, "_json", side_effect=forged):
            check = audit_module.audit()
        self.assertIn("RED_PROXY_PRIVILEGE_OR_CACHE", check["issues"])
        self.assertIn("RED_FREE_TIER_UNVERIFIED_GPU_OR_COST", check["issues"])
        self.assertIn("RED_OWNER_PROMOTION_AUTHORITY", check["issues"])


if __name__ == "__main__":
    unittest.main()

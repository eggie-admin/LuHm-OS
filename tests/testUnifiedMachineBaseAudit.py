#!/usr/bin/env python3
"""Negative controls for minimal cross-language machine source architecture."""
from __future__ import annotations
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("unifiedMachineBaseAudit", ROOT / "tools/unifiedMachineBaseAudit.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
DOC = json.loads((ROOT / "doctrine/unifiedMachineBaseV1.json").read_text(encoding="utf-8"))


class UnifiedMachineBaseTests(unittest.TestCase):
    def test_canonical_source_contract(self):
        self.assertEqual(audit.review(DOC), [])
        self.assertEqual(DOC["logicalCells"]["count"], 16)
        self.assertFalse(DOC["logicalCells"]["physicalRegisters"])

    def test_four_profiles_are_source_only(self):
        for profile in DOC["profiles"]:
            with self.subTest(profile=profile):
                result = audit.run(profile)
                self.assertEqual(result["failures"], [])
                self.assertEqual(result["verdict"], "AMBER_SOURCE_VERIFIED_RUNTIME_PENDING")
                self.assertFalse(result["castAuthorized"])
                self.assertFalse(result["actualBuildProven"])
                self.assertFalse(result["servicesStarted"])
                self.assertFalse(result["realMigrationPerformed"])

    def test_isolated_sqlite_hash_proof(self):
        receipt = audit.in_memory_sqlite_check()
        self.assertTrue(receipt["sha256Matched"])
        self.assertFalse(receipt["databaseFilesCreated"])
        self.assertFalse(receipt["mysqlMariaDbMigrationExecuted"])

    def test_forbid_dangerous_service_as_core(self):
        for component in ("certbot", "gparted", "apache", "mariaDb"):
            with self.subTest(component=component):
                altered = copy.deepcopy(DOC)
                altered["profiles"]["linuxHeadless"]["required"].append(component)
                self.assertTrue(audit.review(altered))

    def test_no_auto_cert_or_disk_write_or_autonomous_bots(self):
        for key in ("productionCertbot", "diskWrites", "firmwareWrites", "autonomousLiveBots",
                    "productionMerge", "publicPublish", "exposedSqlPort"):
            altered = copy.deepcopy(DOC)
            altered["authority"][key] = True
            with self.subTest(key=key):
                self.assertTrue(audit.review(altered))

    def test_migration_compatibility_not_assumed(self):
        for name in ("apacheToNginx", "mysqlToMariaDb"):
            altered = copy.deepcopy(DOC)
            altered["migrationGates"][name]["automaticRewrite"] = True
            self.assertTrue(audit.review(altered))
            altered = copy.deepcopy(DOC)
            altered["migrationGates"][name]["requires"] = []
            self.assertTrue(audit.review(altered))

    def test_android_never_imports_server_or_toolchain_runtime(self):
        for item in ("nginx", "mariaDb", "javaGradle", "sqlite3"):
            altered = copy.deepcopy(DOC)
            altered["profiles"]["androidClient"]["required"].append(item)
            self.assertTrue(audit.review(altered))
        altered = copy.deepcopy(DOC)
        altered["profiles"]["androidClient"]["forbidden"].remove("mariaDb")
        self.assertTrue(audit.review(altered))

    def test_evidence_and_automation_fail_closed(self):
        altered = copy.deepcopy(DOC)
        altered["automationLanes"][-1]["automatic"] = True
        self.assertTrue(audit.review(altered))
        altered = copy.deepcopy(DOC)
        altered["authority"]["crownStatus"] = "GREEN"
        self.assertTrue(audit.review(altered))
        altered = copy.deepcopy(DOC)
        altered["components"]["certbot"]["source"] = "../../etc/shadow"
        self.assertTrue(audit.review(altered))
        self.assertIn("exact source mismatch", audit.run("linuxHeadless", expected="a" * 40)["failures"])


if __name__ == "__main__":
    unittest.main()

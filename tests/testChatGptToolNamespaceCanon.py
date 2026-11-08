#!/usr/bin/env python3
"""Exact alias and hostile-drift tests; no network, builds, or remote writes."""
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from chatGptToolNamespaceCanon import audit, resolve

class ChatGptToolNamespaceCanonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / "doctrine/chatGptToolNamespaceCanonV1.json").read_text())
        cls.naming = json.loads((ROOT / "doctrine/namingNamespaceCanonV1.json").read_text())
        cls.architecture = json.loads((ROOT / "doctrine/luHmOSFourLayerArchitectureV1.json").read_text())
        cls.harness = (ROOT / "host/mcp/luhmHarness.py").read_text()
        cls.sql = (ROOT / "host/api/typedLanesV1.sql").read_text()

    def errors(self, data=None, harness=None, sql=None):
        return audit(
            copy.deepcopy(self.data if data is None else data),
            self.naming, self.architecture,
            self.harness if harness is None else harness,
            self.sql if sql is None else sql,
        )

    def test_current_source_contract_has_no_drift(self):
        self.assertEqual(self.errors(), [])

    def test_all_four_alias_layers_and_external_tool_names_recover_identity(self):
        fields = (
            "machineSqlDragonTail", "repositoryKebabNamespace",
            "vowelRippedStrictCamelHump", "fullHumanCenteredCamelHump",
            "externalWireToolName",
        )
        for row in self.data["bindings"]:
            for field in fields:
                result = resolve(self.data, row[field])
                self.assertEqual(result["canonicalMachineId"], row["fullHumanCenteredCamelHump"])
                self.assertEqual(result["externalWireToolName"], row["externalWireToolName"])
                self.assertEqual(result["authorityEffect"], "none")
                self.assertFalse(result["runtimeVerified"])
        self.assertIsNone(resolve(self.data, "luhmOpenMobileCockpitMaybe"))

    def test_mixed_case_site_tool_is_external_only_not_canonical_id(self):
        match = resolve(self.data, "luhmConnectionStatus")
        self.assertEqual(match["canonicalMachineId"], "connectionStatus")

    def test_snake_case_machine_identity_is_red(self):
        changed = copy.deepcopy(self.data)
        changed["bindings"][1]["fullHumanCenteredCamelHump"] = "open_cockpit"
        self.assertIn("NON_CAMELHUMP_MACHINE_ID", self.errors(changed))

    def test_published_mcp_spelling_cannot_change_silently(self):
        changed = copy.deepcopy(self.data)
        changed["bindings"][1]["externalWireToolName"] = "openCockpit"
        self.assertIn("PUBLISHED_TOOL_NAME_CHANGED:openCockpit", self.errors(changed))

    def test_alias_collision_is_red_even_between_different_layers(self):
        changed = copy.deepcopy(self.data)
        changed["bindings"][2]["vowelRippedStrictCamelHump"] = "opnCckpt"
        self.assertIn("AMBIGUOUS_ALIAS:opnCckpt", self.errors(changed))

    def test_broken_render_tool_or_ui_resource_is_red(self):
        broken = self.harness.replace('name="luhm_open_mobile_cockpit"', 'name="removed_mobile_tool"')
        self.assertIn("RENDER_TOOL_NOT_DECLARED:openMobileCockpit", self.errors(harness=broken))
        changed = copy.deepcopy(self.data)
        changed["bindings"][2]["resourceUri"] = "ui://unrelated/widget.html"
        self.assertIn("RESOURCE_URI_CHANGED:openMobileCockpit", self.errors(changed))

    def test_sql_machine_table_drift_is_red(self):
        self.assertIn("MISSING_CAMELHUMP_SQL_TABLE:streamEvent",
                      self.errors(sql=self.sql.replace("CREATE TABLE IF NOT EXISTS streamEvent(", "CREATE TABLE IF NOT EXISTS stream_event(")))

    def test_authority_and_remote_proof_are_fail_closed(self):
        changed = copy.deepcopy(self.data)
        changed["authorityBoundary"]["aliasesMayExecute"] = True
        self.assertIn("AUTHORITY_ESCALATION_FORBIDDEN", self.errors(changed))
        changed = copy.deepcopy(self.data)
        changed["remoteProof"]["chatGptAndroidUiMount"] = "GREEN"
        self.assertIn("REMOTE_PROOF_NOT_ESTABLISHED", self.errors(changed))

    def test_unreviewed_tool_binding_cannot_sneak_in(self):
        changed = copy.deepcopy(self.data)
        item = copy.deepcopy(changed["bindings"][1])
        item["fullHumanCenteredCamelHump"] = "runShell"
        item["externalWireToolName"] = "luhm_run_shell"
        changed["bindings"].append(item)
        self.assertIn("UNREVIEWED_MACHINE_ID:runShell", self.errors(changed))


if __name__ == "__main__":
    unittest.main()

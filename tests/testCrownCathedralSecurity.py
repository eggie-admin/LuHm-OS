"""Source-only safety tests. Never contacts Cloudflare or touches credentials."""
from __future__ import annotations
import importlib.util
import os
from pathlib import Path
import sys
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "cloudflareEmailRoutingApply",
    ROOT / "tools" / "cloudflareEmailRoutingApply.py",
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class RoutingSafetyTests(unittest.TestCase):
    def test_expected_address_inventory_is_unique(self):
        self.assertEqual(len(set(mod.ALIASES)), 11)
        self.assertIn("postmaster", mod.ALIASES)
        self.assertIn("abuse", mod.ALIASES)
        self.assertIn("certs", mod.ALIASES)
        self.assertNotIn("noreply", mod.ALIASES)

    def test_exact_matcher_only(self):
        self.assertIsNone(mod.existing_recipient({"matchers": [{"type": "all"}]}))
        self.assertEqual(
            mod.existing_recipient({"matchers": [
                {"type": "literal", "field": "to", "value": "ADMIN@EGGIEBAGELFACE.ART"}
            ]}),
            "admin@eggiebagelface.art",
        )

    def test_missing_destination_blocks_writes(self):
        with mock.patch.dict(os.environ, {
            "CLOUDFLARE_API_TOKEN": "unit-test-token",
            "CLOUDFLARE_ACCOUNT_ID": "unit-test-account",
            "CLOUDFLARE_ZONE_ID": "unit-test-zone",
            "LUHM_MAIL_DESTINATION": "owner@gmail.com",
        }):
            with mock.patch.object(sys, "argv", ["tool", "--apply-rules"]):
                with mock.patch.object(mod, "audit_state", return_value=(True, False, [])):
                    with mock.patch.object(mod, "api") as api:
                        with self.assertRaises(mod.RoutingError):
                            mod.main()
                        api.assert_not_called()

    def test_existing_conflicting_alias_blocks_every_create(self):
        conflicting = {
            "matchers": [{"type": "literal", "field": "to", "value": "security@eggiebagelface.art"}],
            "actions": [{"type": "forward", "value": ["not-owner@example.com"]}],
            "enabled": True,
        }
        with mock.patch.dict(os.environ, {
            "CLOUDFLARE_API_TOKEN": "unit-test-token",
            "CLOUDFLARE_ACCOUNT_ID": "unit-test-account",
            "CLOUDFLARE_ZONE_ID": "unit-test-zone",
            "LUHM_MAIL_DESTINATION": "owner@gmail.com",
        }):
            with mock.patch.object(sys, "argv", ["tool", "--apply-rules"]):
                with mock.patch.object(mod, "audit_state", return_value=(True, True, [conflicting])):
                    with mock.patch.object(mod, "check_mx"):
                        with mock.patch.object(mod, "api") as api:
                            with self.assertRaises(mod.RoutingError):
                                mod.main()
                            api.assert_not_called()

    def test_no_writes_default_audit(self):
        with mock.patch.dict(os.environ, {
            "CLOUDFLARE_API_TOKEN": "unit-test-token",
            "CLOUDFLARE_ACCOUNT_ID": "unit-test-account",
            "CLOUDFLARE_ZONE_ID": "unit-test-zone",
            "LUHM_MAIL_DESTINATION": "owner@gmail.com",
        }):
            with mock.patch.object(sys, "argv", ["tool"]):
                with mock.patch.object(mod, "audit_state", return_value=(True, True, [])):
                    with mock.patch.object(mod, "api") as api:
                        self.assertEqual(mod.main(), 0)
                        api.assert_not_called()


if __name__ == "__main__":
    unittest.main()

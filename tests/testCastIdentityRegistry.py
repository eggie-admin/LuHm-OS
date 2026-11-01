#!/usr/bin/env python3
"""Python/JS shared CAST alias registry and 4x4 identity proof."""
from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sp = importlib.util.spec_from_file_location("luhmIdentityRegistry", ROOT / "host/api/luhmIdentityRegistry.py")
assert sp and sp.loader
ident = importlib.util.module_from_spec(sp)
sp.loader.exec_module(ident)


class TestIdentityRegistry(unittest.TestCase):
    def test_python_resolves_every_registered_level_and_shared_source(self):
        r = ident.verified_registry()
        self.assertEqual(len(r["byCanonical"]), 25)
        for name, row in r["byCanonical"].items():
            with self.subTest(name=name):
                self.assertEqual(ident.encode(name), row["utf8Hex"])
                self.assertEqual(ident.decode(row["utf8Hex"]), name)
                for alias in (name, row["vowelRipped"], row["shorthand"], row["utf8Hex"]):
                    self.assertEqual(ident.resolve(alias)["canonical"], name)
                    self.assertFalse(ident.resolve(alias)["authority"])

    def test_help_aliases_legacy_and_exact_hex(self):
        self.assertEqual(ident.resolve("bs")["canonical"], "belldandySecretary")
        self.assertEqual(ident.resolve("blldndyScrtry")["canonical"], "belldandySecretary")
        self.assertEqual(ident.resolve("62656c6c64616e6479536563726574617279")["canonical"],
                         "belldandySecretary")
        self.assertEqual(ident.resolve("mgcCdngRlplay")["canonical"], "codingRoleplay")
        self.assertEqual(ident.resolve("lm")["canonical"], "lum")
        self.assertEqual(ident.resolve("lmesh")["canonical"], "lumMesh")

    def test_4x4_typed_lanes_remain_source_only(self):
        r = ident.cast_projection()
        self.assertEqual(len(r["matrix4x4"]), 16)
        self.assertEqual(len(r["bindings"]), 6)
        self.assertEqual(len(r["registrySha256"]), 64)
        self.assertFalse(r["npmPublished"])
        self.assertFalse(r["greenAuthority"])
        self.assertFalse(r["osVariablesChanged"])
        for cell in r["matrix4x4"]:
            self.assertFalse(cell["authority"])

    def test_no_guesses_and_malformed_utf8_hex(self):
        for query in ("BS", "lm ", "0x6c6d", "__proto__", "admn", "", [], None):
            self.assertEqual(ident.resolve(query)["status"], "VERIFY")
        for bad in ("abc", "GG", "ff", "00", "6c6d00", "41", 1, None):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                ident.decode(bad)
        with self.assertRaises(ValueError):
            ident.encode("../../secrets")

    def test_registry_rejects_same_alias_two_owners(self):
        base = ident._load
        def forged(path):
            x = base(path)
            if path == ident.REGISTRY:
                x = copy.deepcopy(x)
                next(row for row in x["bindings"] if row["canonical"] == "professorLum")["shorthand"] = "bs"
            return x
        with patch.object(ident, "_load", side_effect=forged):
            with self.assertRaisesRegex(ValueError, "RED_IDENTITY_ALIAS_COLLISION"):
                ident.verified_registry()

    def test_exact_help_and_system_variable_source_drift_rejected(self):
        base = ident._load
        def forged(path):
            x = base(path)
            if path == ident.REGISTRY:
                x = copy.deepcopy(x)
                x["systemVariableRegistry"]["bindings"][0]["name"] = "LD_PRELOAD"
            return x
        with patch.object(ident, "_load", side_effect=forged):
            with self.assertRaisesRegex(ValueError, "RED_ENV_REGISTRY_DRIFT"):
                ident.verified_registry()

    def test_fake_permission_from_alias_is_rejected(self):
        base = ident._load
        def forged(path):
            x = base(path)
            if path == ident.REGISTRY:
                x = copy.deepcopy(x)
                x["identityPolicy"]["aliasMayGrantAuthority"] = True
            return x
        with patch.object(ident, "_load", side_effect=forged):
            with self.assertRaisesRegex(ValueError, "RED_IDENTITY_REGISTRY_AUTHORITY"):
                ident.verified_registry()


if __name__ == "__main__":
    unittest.main()

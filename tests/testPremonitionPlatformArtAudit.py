#!/usr/bin/env python3
"""LuHm Project Premonition 4x4 mobile/vector/3D/SQL separation regression."""
from __future__ import annotations

import copy
import importlib.util
import json
import struct
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
s = importlib.util.spec_from_file_location(
    "premonitionPlatformArtAudit", ROOT / "tools/premonitionPlatformArtAudit.py")
assert s and s.loader
module = importlib.util.module_from_spec(s)
s.loader.exec_module(module)
SHA = "f0cb6ee54066b490c0e80efc2c96200fec76ee2d"
BASE = {"asset_id": "logoOne", "task_id": "studioTask", "source_ref": SHA,
        "scope_id": "privateStudio", "kind": "svg", "pointer": "private:logoOne"}
SVG = b'<svg xmlns="http://www.w3.org/2000/svg"><title>LuHm</title><path d="M0 0 L1 1"/></svg>'


class PlatformArtAuditTests(unittest.TestCase):
    def test_16_cells_and_real_source_art_and_sql(self):
        r = module.audit_source()
        self.assertEqual(r["status"], "SOURCE_CONSISTENT_ONLY", r["issues"])
        self.assertEqual(r["candidateMatrixCells"], 16)
        self.assertEqual(len(r["sqliteMetadataTables"]), 2)
        self.assertFalse(r["privateArtImported"])
        self.assertFalse(r["iosBuildSigned"])
        self.assertFalse(r["greenAuthority"])

    def test_safe_vector_to_python_to_strict_sql_metadata(self):
        proposal = module.plan_asset(**BASE, payload=SVG)
        self.assertEqual(proposal["assetClass"], "vectorBrand")
        self.assertEqual(proposal["byteCount"], len(SVG))
        self.assertNotIn("svgContent", proposal)
        checked = module.receipt_in_memory(proposal)
        self.assertEqual(checked["state"], "OFFLINE_SQLITE_METADATA_INSERT_VERIFIED")
        self.assertEqual(checked["sha256Hex"], proposal["sha256Hex"])
        self.assertFalse(checked["rawAssetPersisted"])
        self.assertFalse(checked["publicationAllowed"])

    def test_3d_glb_candidate_is_not_rig_proof(self):
        scene = json.dumps({"asset": {"version": "2.0"}, "meshes": []},
                           separators=(",", ":")).encode()
        scene += b" " * (-len(scene) % 4)
        blob = (b"glTF" + struct.pack("<II", 2, 20 + len(scene)) +
                struct.pack("<I", len(scene)) + b"JSON" + scene)
        props = module.plan_asset(**{**BASE, "asset_id": "modelOne",
                                      "kind": "glb", "pointer": "private:modelOne"},
                                  payload=blob)
        self.assertEqual(props["assetClass"], "threeD")
        self.assertFalse(props["actualTargetDeviceVerified"])
        self.assertEqual(props["rightsState"], "PRIVATE_REVIEW")
        self.assertFalse(props["greenAuthority"])
        self.assertFalse(module.classify_content(blob[:-1], "glb"))

    def test_svg_scripts_external_resource_and_xml_entities_blocked(self):
        dangerous = [
            b'<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>',
            b'<svg xmlns="http://www.w3.org/2000/svg" onload="alert(1)"/>',
            b'<svg xmlns="http://www.w3.org/2000/svg"><image href="https://bad/"/></svg>',
            b'<!DOCTYPE svg [<!ENTITY a SYSTEM "file:///etc/passwd">]><svg xmlns="http://www.w3.org/2000/svg">&a;</svg>',
            b'<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg"/>',
        ]
        for raw in dangerous:
            with self.subTest(raw=raw[:36]):
                self.assertFalse(module.classify_content(raw, "svg"))
                with self.assertRaises(ValueError):
                    module.plan_asset(**BASE, payload=raw)

    def test_gltf_external_uris_and_invalid_binary_are_blocked(self):
        pure = b'{"asset":{"version":"2.0"},"meshes":[]}'
        self.assertTrue(module.classify_content(pure, "gltf"))
        external = b'{"asset":{"version":"2.0"},"buffers":[{"uri":"https://bad/x.bin"}]}'
        self.assertFalse(module.classify_content(external, "gltf"))
        self.assertFalse(module.classify_content(b"BLENDERbad", "glb"))
        self.assertFalse(module.classify_content(b"abc", "unknown"))
        self.assertFalse(module.classify_content(b"\x89PNG\r\n\x1a\n", "svg"))

    def test_no_sql_or_rights_bypass_and_no_path_traversal(self):
        with self.assertRaises(ValueError):
            module.plan_asset(**{**BASE, "rights_state": "RIGHTS_CLEARED"}, payload=SVG)
        with self.assertRaises(ValueError):
            module.plan_asset(**{**BASE, "pointer": "../../secrets"}, payload=SVG)
        with self.assertRaises(ValueError):
            module.plan_asset(**{**BASE, "source_ref": "main"}, payload=SVG)
        with self.assertRaises(ValueError):
            module.plan_asset(**{**BASE, "asset_id": "a); DROP TABLE"}, payload=SVG)
        with self.assertRaises(ValueError):
            module.receipt_in_memory({"status": "READY"})

    def test_canon_kernel_and_brand_tampering_fail_closed(self):
        original = module._load
        def forged(path):
            value = original(path)
            if path == module.POLICY:
                value = copy.deepcopy(value)
                value["matrix"][0]["cells"][0]["vendorKernelMutationAllowed"] = True
                value["product"]["name"] = "Samsung Official"
                value["assetRouting"]["binaryNeverStoredInSql"] = False
            return value
        with patch.object(module, "_load", side_effect=forged):
            result = module.audit_source()
        self.assertIn("RED_4X4_AUTHORITY", result["issues"])
        self.assertIn("RED_PRODUCT_BRAND", result["issues"])
        self.assertIn("RED_SQL_BINARY_BOUNDARY", result["issues"])


if __name__ == "__main__":
    unittest.main()

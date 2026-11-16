#!/usr/bin/env python3
"""Creative Forge: 4×4 source checks, safe RSS and community rights holds."""
from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sp=importlib.util.spec_from_file_location("creativeCommunityAudit",ROOT/"tools/creativeCommunityAudit.py")
assert sp and sp.loader
gate=importlib.util.module_from_spec(sp)
sp.loader.exec_module(gate)
SHA="f0cb6ee54066b490c0e80efc2c96200fec76ee2d"

RSS=b"""<?xml version="1.0"?>
<rss version="2.0"><channel><title>Open Projects</title>
<item><title>Release Notes</title><link>https://github.com/example/project/releases</link></item>
</channel></rss>"""
ATOM=b"""<feed xmlns="http://www.w3.org/2005/Atom"><title>Art</title>
<entry><title>New Demo</title><link href="https://github.com/example/studio"/></entry></feed>"""


class TestCreativeCommunityForge(unittest.TestCase):
    def test_four_by_four_and_no_live_workers(self):
        x=gate.audit()
        self.assertEqual(x["state"],"SOURCE_CANDIDATE_ONLY",x["issues"])
        self.assertEqual(x["cells"],16)
        self.assertEqual(x["referenceSources"],9)
        self.assertEqual(x["nexusRequests"],0)
        self.assertEqual(x["romsProcessed"],0)
        self.assertEqual(x["live2dConversions"],0)
        self.assertFalse(x["greenAuthority"])

    def test_rss_atom_offline_and_provenance_unknown(self):
        for payload,expected in ((RSS,"rss2"),(ATOM,"atom")):
            with self.subTest(expected=expected):
                out=gate.parse_feed(payload)
                self.assertEqual(out["format"],expected)
                self.assertEqual(len(out["entries"]),1)
                self.assertFalse(out["publisherIdentityVerified"])
                self.assertEqual(out["networkRequests"],0)
                self.assertFalse(out["entries"][0]["rightsVerified"])
                self.assertEqual(len(out["feedDigest"]),64)

    def test_xml_entities_external_files_links_and_bomb_denied(self):
        bad=[
            b"",
            b"<!DOCTYPE foo [<!ENTITY xxe SYSTEM 'file:///etc/passwd'>]><rss/>",
            b"<rss><!-- hidden --><channel/></rss>",
            b"<rss><channel><item><title>T</title><link>file:///etc/passwd</link></item></channel></rss>",
            b"<rss><channel><item><title>T</title><link>http://localhost/</link></item></channel></rss>",
            b"<rss><channel><item><title>T</title><link>https://127.0.0.1/private</link></item></channel></rss>",
            b"<rss><channel><item><title>T</title><link>https://user:password@example.org/</link></item></channel></rss>",
            b"<rss><channel><item><title>T</title><link>javascript:alert(1)</link></item></channel></rss>",
            b"<rss><channel><item><title>T</title><link>https://example.org/</link></item></channel>",
            b"<html><body>Not a feed</body></html>",
            RSS+b" "*65536
        ]
        for value in bad:
            with self.subTest(value=value[:40]),self.assertRaises(ValueError):
                gate.parse_feed(value)

    def test_user_submitted_source_is_a_claim_not_a_permission(self):
        for reference,claimed in (("foundryDnd5e","MIT"),("dazToBlender","Apache-2.0"),
                                  ("nexus","proprietary"),("live2d","unknown"),
                                  ("srd521","CC-BY-4.0")):
            with self.subTest(reference=reference):
                out=gate.candidate(task_id="creativeTask",source_ref=SHA,
                                   scope_id="privateStudio",reference_id=reference,
                                   asset_license=claimed)
                self.assertEqual(out["status"],"HOLD_PER_FILE_RIGHTS_AND_CURRENT_RELEASE_PROOF")
                self.assertFalse(out["permissionVerified"])
                self.assertFalse(out["binaryImported"])
                self.assertFalse(out["gitForkCreated"])
                self.assertFalse(out["pluginInstalled"])
        for invalid in (dict(reference_id="unknown"),dict(task_id="../"),
                        dict(source_ref="main"),dict(asset_license="../../secret")):
            params=dict(task_id="creativeTask",source_ref=SHA,
                        scope_id="privateStudio",reference_id="nexus",asset_license="unknown")
            params.update(invalid)
            with self.assertRaises(ValueError):
                gate.candidate(**params)

    def test_live2d_daz_only_manual_rigged_authorized_target(self):
        for source in ("PSD_LAYERS","ORIGINAL_SVG","OWNED_DAZ_REFERENCE"):
            out=gate.avatar_retarget_plan(source_format=source,
                target_format="BLENDER_RIG_PLAN",rights="homebrewOwned")
            self.assertFalse(out["auto3dMeshGenerated"])
            self.assertFalse(out["blenderExecuted"])
            self.assertFalse(out["live2dCoreLoaded"])
            self.assertFalse(out["commandExecuted"])
        for source,right in (("piratedCubism","homebrewOwned"),
                             ("PSD_LAYERS","unknown"),
                             ("LIVE2D_PROPRIETARY_MODEL","homebrewOwned")):
            with self.assertRaises(ValueError):
                gate.avatar_retarget_plan(source_format=source,target_format="GODOT_GLTF_PLAN",rights=right)

    def test_no_auto_github_fork_rights_or_rss_read_in_contract(self):
        original=gate._read
        def fake(path):
            obj=original(path)
            if path==gate.CONTRACT:
                obj=copy.deepcopy(obj)
                obj["automation"]["githubAutoFork"]=True
                obj["avatars"]["autoConvertLive2dTo3d"]=True
                obj["matrix4x4"][0]["cells"][0]["rightsApproved"]=True
            return obj
        with patch.object(gate,"_read",side_effect=fake):
            x=gate.audit()
        self.assertIn("RED_CREATIVE_UNAPPROVED_AUTOMATION",x["issues"])
        self.assertIn("RED_CREATIVE_FAKE_EVIDENCE",x["issues"])
        self.assertIn("RED_CREATIVE_RIGHTS",x["issues"])


if __name__=="__main__":
    unittest.main()

#!/usr/bin/env python3
"""Brand + VM seal adversarial parser and MCP Apps view source tests."""
from __future__ import annotations
import copy
import importlib.util
import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
def imp(path:str):
    s=importlib.util.spec_from_file_location(path.replace("/","_"),ROOT/path)
    assert s and s.loader
    obj=importlib.util.module_from_spec(s)
    s.loader.exec_module(obj)
    return obj
m=imp("tools/brandVmSealAudit.py")
mcp=imp("host/mcp/luhmBrandVmSealTools.py")


class DummyServer:
    def __init__(self):
        self.resources={}
        self.tools={}
        self.resource_meta={}
        self.tool_meta={}
    def resource(self,uri,**args):
        def take(fn):
            self.resources[uri]=fn
            self.resource_meta[uri]=args
            return fn
        return take
    def tool(self,**args):
        def take(fn):
            self.tools[args["name"]]=fn
            self.tool_meta[args["name"]]=args
            return fn
        return take


class TestBrandVmSeal(unittest.TestCase):
    def test_16_cells_vector_provenance_and_not_fake_guest(self):
        r=m.audit()
        self.assertEqual(r["status"],"SOURCE_SEALED_CANDIDATE_ONLY",r["issues"])
        self.assertEqual(r["cells"],16)
        self.assertEqual(r["hexNamespaces"],7)
        self.assertTrue(r["brandVectorSafe"])
        self.assertFalse(r["vmBooted"])
        self.assertFalse(r["historicalWebServiceEqualsVM"])
        self.assertFalse(r["installedPluginUpdatedToThisSource"])
        self.assertFalse(r["sourceProductionGreen"])

    def test_hex_normalizes_fixed_width_same_kind_no_guessing(self):
        a=m.fixed_hex("pciVendorId","a")
        self.assertEqual((a["hex"],a["sortKey"]),("000a","pciVendorId:000a"))
        b=m.fixed_hex("pciVendorId",16)
        self.assertTrue(a["sortKey"]<b["sortKey"])
        self.assertEqual(m.fixed_hex("cpuidLeaf",15)["hex"],"0000000f")
        self.assertEqual(m.fixed_hex("sourceRef","a"*40)["bits"],160)
        for kind,val in (("unknown","abcd"),("pciVendorId","0xabcd"),
                         ("pciVendorId","ABCD"),("pciVendorId",True),
                         ("sourceRef","abcd"),("artifactSha256","ff"),
                         ("ipsOffset",-1),("pciVendorId",65536)):
            with self.subTest(kind=kind,val=val),self.assertRaises(ValueError):
                m.fixed_hex(kind,val)

    def test_owned_ppm_bitmap_to_safe_vector_rect_runs(self):
        # Explicit 4x2 pixel bitmap using 2 registered colors.
        p=b"P3\n4 2\n255\n" + b"23 19 31 "*2+b"159 122 234 "*2+b"23 19 31 "*4
        r=m.bitmap_to_vector(p,rights="originalOwned")
        self.assertEqual(r["width"],4)
        self.assertEqual(r["height"],2)
        self.assertEqual(r["rectangleCount"],3)
        self.assertEqual(len(r["vectorSha256"]),64)
        self.assertFalse(r["outputPublicApproved"])
        self.assertFalse(r["networkUsed"])
        root=ET.fromstring(r["svg"])
        self.assertEqual(len(root),3)
        self.assertNotIn("script",r["svg"])
        self.assertEqual([x.attrib["width"] for x in root],["2","2","4"])

    def test_hostile_ppm_and_lax_rights_fail_closed(self):
        okay=b"P3 1 1 255 23 19 31"
        for payload in (b"",b"P6 1 1 255 "+bytes(3),
                        b"P3 1 1 255 256 19 31",
                        b"P3 1 1 255 1 2 3",
                        b"P3 1 1 255 23 19 31 #!danger",
                        b"P3 999 999 255",
                        b"P3 1 1 255 23 19 31 "+b"9"*9000,
                        b"P3 1 1 255 23 19"):
            with self.subTest(payload=payload[:20]),self.assertRaises(ValueError):
                m.bitmap_to_vector(payload)
        with self.assertRaises(ValueError):
            m.bitmap_to_vector(okay,rights="thirdPartyMod")
        with self.assertRaises(ValueError):
            m.bitmap_to_vector(okay,rights="unknown")

    def test_static_svg_forbids_script_external_embeds(self):
        self.assertTrue(m._check_svg(m.VEC))
        original=m.VEC
        with patch.object(m,"VEC",ROOT/"publicationSite/index.html"):
            self.assertFalse(m._check_svg(ROOT/"publicationSite/index.html"))
        self.assertEqual(original.name,"brandSealCandidate.svg")

    def test_mcp_widget_is_new_resource_and_no_vm_started(self):
        server=DummyServer()
        mcp.register_brand_vm_seal(server,root=ROOT,annotations={"readOnlyHint":True})
        self.assertIn(mcp.RESOURCE,server.resources)
        content=server.resources[mcp.RESOURCE]()
        self.assertIn("SIMULATED BOOT",content)
        self.assertIn("data:image/svg+xml;base64,",content)
        self.assertNotIn('src="brandSealCandidate.svg"',content)
        self.assertNotIn("<iframe src=",content)
        data=server.tools["luhm_open_brand_vm_seal"]()
        self.assertEqual(data["surface"],"mcp-app")
        self.assertFalse(data["liveGuestRunning"])
        self.assertFalse(data["candidatePluginInstalled"])
        self.assertFalse(data["publicationAuthorized"])
        self.assertEqual(
            server.tool_meta["luhm_open_brand_vm_seal"]["meta"]["ui"]["resourceUri"],
            mcp.RESOURCE)

    def test_tamper_false_runtime_claims_refused(self):
        original=m._json
        def forged(path):
            d=original(path)
            if path==m.POLICY:
                d=copy.deepcopy(d)
                d["host"]["runtimeVMProven"]=True
                d["release"]["noAutoMerge"]=False
                d["matrix4x4"][0]["cells"][0]["hostVerified"]=True
            return d
        with patch.object(m,"_json",side_effect=forged):
            r=m.audit()
        for flag in ("RED_SEAL_HOST_CLAIM","RED_SEAL_RELEASE","RED_SEAL_IMPLIED_GREEN"):
            self.assertIn(flag,r["issues"])


if __name__=="__main__":
    unittest.main()

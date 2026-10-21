#!/usr/bin/env python3
"""Check that Rebel is an independent, local-only ChatGPT Studio project."""
from __future__ import annotations
import copy
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/"doctrine/rebelInChatStudioV1.json"
WIDGET=ROOT/"host/harness/widget.html"
HARNESS=ROOT/"host/mcp/luhmHarness.py"
INTO_THE_WARP=ROOT/"doctrine/artistStudioPluginV1.json"

def validate(contract: dict) -> list[str]:
    issues=[]
    def check(ok:bool,reason:str)->None:
        if not ok: issues.append(reason)
    check(contract.get("schema")=="luhmOs.rebelInChatStudio.v1","Rebel source schema")
    check(contract.get("status")=="SOURCE_CONFIGURED_PRIVATE_DRAFT","No unproved project status")
    check(contract.get("tool")=="luhm_open_cockpit","Existing ChatGPT plugin tool")
    check(contract.get("resourceUri")=="ui://luhm-os/cockpit-v2.html","In-chat resource URI")
    project=contract.get("project",{})
    check(project.get("id")=="rebel" and project.get("shotUnitSeconds")==8 and project.get("maxDraftShots")==12,"Eight-second project format")
    check(project.get("audioSourceStatus")=="PENDING_EXACT_RECORDING","Unknown song recording must be explicit")
    boundary=contract.get("stateBoundary",{})
    for key in ("serverWrites","driveWrites","githubMutations","publication","externalAssetUploads"):
        check(boundary.get(key) is False,"Forbidden write: "+key)
    for key in ("clientMemoryOnly","userInitiatedChatHandoffOnly","privateMediaExcluded"):
        check(boundary.get(key) is True,"User-control requirement: "+key)
    preservation=contract.get("preservation",{})
    for key in ("rawDictationVerbatim","sourceAndEditedSeparate","originalAssetsUntouched","intoTheWarpSeparateProject","rightsBeforePublicDerivatives"):
        check(preservation.get(key) is True,"Preservation: "+key)
    check(contract.get("crownStatus")=="STOP","No release authority")
    return issues

class RebelStudioSafety(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract=json.loads(CONTRACT.read_text(encoding="utf-8"))
        cls.widget=WIDGET.read_text(encoding="utf-8")
        cls.harness=HARNESS.read_text(encoding="utf-8")
        cls.other=json.loads(INTO_THE_WARP.read_text(encoding="utf-8"))

    def test_rebel_is_private_source_candidate(self):
        self.assertEqual(validate(self.contract),[])
        self.assertEqual(self.other["project"]["id"],"into-the-warp")
        self.assertEqual([x["id"] for x in self.other["project"]["shots"]],["100","200","300","401","402","403","500"])

    def test_no_unreviewed_auto_promotion(self):
        for path,value in [
            (("stateBoundary","serverWrites"),True),
            (("stateBoundary","driveWrites"),True),
            (("stateBoundary","publication"),True),
            (("stateBoundary","clientMemoryOnly"),False),
            (("stateBoundary","userInitiatedChatHandoffOnly"),False),
            (("preservation","intoTheWarpSeparateProject"),False),
            (("crownStatus",),"GREEN"),
            (("project","audioSourceStatus"),"LICENSED_AND_READY")
        ]:
            mutated=copy.deepcopy(self.contract)
            node=mutated
            for name in path[:-1]:node=node[name]
            node[path[-1]]=value
            with self.subTest(path=path):
                self.assertTrue(validate(mutated))

    def test_existing_tool_payload_exposes_rebel_without_power(self):
        self.assertIn('rebelStudio": rebel_studio',self.harness)
        self.assertIn('RED_REBEL_CHAT_STUDIO_CONTRACT',self.harness)
        self.assertIn('stateBoundary", {}).get("serverWrites") is not False',self.harness)

    def test_widget_has_separate_chat_only_controls(self):
        page=self.widget
        for needle in (
            'data-luhm-rebel-project','id="rebelRaw"','id="rebelStart"',
            'id="rebelShots"','id="rebelSeconds"','id="rebelVisual"',
            'function rebelWire()','rebelInitialize(payload?.rebelStudio)',
            'rebelWire();studioWire()', 'shots:rebelState.shots.map',
            'await sendFollowUp(prompt)',
            'data-luhm-studio','function studioValid(v)'
        ):
            with self.subTest(needle=needle):self.assertIn(needle,page)
        self.assertNotIn("setOpenInAppUrl",page)
        self.assertNotIn("localStorage.setItem",page)
        self.assertNotIn("sessionStorage.setItem",page)
        self.assertNotIn("fetch(",page.split("/* Separate Rebel music-video draft")[1].split("/* In-chat artist studio")[0])
        self.assertNotIn("innerHTML",page.split("/* Separate Rebel music-video draft")[1].split("/* In-chat artist studio")[0])

if __name__=="__main__":unittest.main()

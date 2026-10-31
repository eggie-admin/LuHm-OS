"""Fail-closed R1-R4 release ladder with WebGL2 candidacy, no fictitious Samsung proof."""
import copy
import json
import unittest
from tools.r1r4ReleaseGate import POLICY, verify, ladder
class R1R4Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.doc=json.loads(POLICY.read_text(encoding="utf-8"))
    def corrupt(self,part,key,value,tag):
        doc=copy.deepcopy(self.doc);doc[part][key]=value
        self.assertIn(tag,verify(doc))
    def test_rungs_consistent(self):
        self.assertEqual(verify(self.doc),[])
        r=ladder(self.doc,source_green=True)
        self.assertEqual([x["id"] for x in r["rungs"]],["R1","R2","R3","R4"])
        self.assertEqual(r["rungs"][0]["status"],"SOURCE_CHECKED")
        self.assertFalse(any(x["promoted"] for x in r["rungs"]))
        self.assertFalse(r["publicReleaseAuthorized"])
    def test_r1_failed_blocks_r2(self):
        r=ladder(self.doc,source_green=False)
        self.assertEqual(r["rungs"][0]["status"],"BLOCKED_SOURCE")
        self.assertEqual(r["rungs"][1]["status"],"BLOCKED_R1")
    def test_no_fake_device_status(self):
        doc=copy.deepcopy(self.doc);doc["independentProof"]["SamsungWebGl2Observed"]=True
        self.assertIn("RUNG_FAKE_EXTERNAL_PROOF",verify(doc))
    def test_no_fake_rig(self):self.corrupt("render","riggedAsset",True,"RUNG_FAKE_RENDER_riggedAsset")
    def test_native_apk_not_claimed(self):self.corrupt("render","nativeAPKShipped",True,"RUNG_FAKE_RENDER_nativeAPKShipped")
    def test_public_release_forbidden(self):self.corrupt("release","publicDeploymentAllowed",True,"RUNG_RELEASE_publicDeploymentAllowed")
    def test_protected_main_guard(self):self.corrupt("release","protectedMainMayBeMergedAutomatically",True,"RUNG_RELEASE_protectedMainMayBeMergedAutomatically")
    def test_3d_fallback_required(self):self.corrupt("render","SVG2dFallback",False,"RENDER_BUDGET")
    def test_new_external_renderer_rejected(self):self.corrupt("render","externalRendererDependencies",1,"RENDER_BUDGET")
    def test_source_missing_rejected(self):
        d=copy.deepcopy(self.doc);d["source"][0]["path"]="frontEnd/rootlessCockpit/missing-houdini.mjs"
        self.assertIn("RUNG_SOURCE_ARTIFACTS",verify(d))
if __name__=="__main__":unittest.main()

"""Sinister spider: actual in-repo static references and human-need transitions."""
from __future__ import annotations
import copy
import json
import tempfile
import unittest
from pathlib import Path
from tools.sinisterSpider import POLICY,ROOT,validate,route,spider,_canonical,references

class SpiderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.doc=json.loads(POLICY.read_text(encoding="utf-8"))
    def test_policy(self):
        self.assertEqual(validate(self.doc),[])
        self.assertEqual(self.doc["matrices"]["eightByEight"]["count"],64)
    def test_local_source_graph_has_real_references(self):
        report=spider(ROOT,self.doc)
        self.assertEqual(report["status"],"PASS_LOCAL_SOURCE_ONLY",report["errors"])
        self.assertGreaterEqual(report["nodesVisited"],12)
        self.assertGreaterEqual(report["edgesChecked"],12)
        self.assertEqual(report["networkRequests"],0)
        self.assertEqual(report["codeImportsExecuted"],0)
        self.assertEqual(report["matrixEvidenceCellsExecuted"],0)
    def test_digest_is_deterministic(self):
        a=spider(ROOT,self.doc)
        b=spider(ROOT,self.doc)
        self.assertEqual(a["digestSha256"],b["digestSha256"])
    def test_zero_touch_close(self):
        r=route(0,3)
        self.assertEqual(r["humanNeed"],0)
        self.assertEqual(r["decision"],"ZERO_TOUCH_READONLY_CLOSE")
        self.assertFalse(r["machineMayWriteProtectedMain"])
    def test_draft_repair_is_only_proposal(self):
        r=route(1,3,repeatable=True)
        self.assertEqual(r["humanNeed"],0)
        self.assertTrue(r["machineMayPrepareDraftFix"])
        self.assertFalse(r["machineMayDeployOrSign"])
    def test_nondeterminism_escalates_to_human(self):
        self.assertEqual(route(1,0,repeatable=True)["humanNeed"],1)
    def test_independent_device_proof_deescalates(self):
        self.assertEqual(route(2,2,independent_proof=False)["humanNeed"],2)
        self.assertEqual(route(2,2,independent_proof=True)["humanNeed"],1)
    def test_privileged_action_stays_manual(self):
        for impact in range(4):
            self.assertEqual(route(impact,3,privileged=True)["humanNeed"],3)
        self.assertEqual(route(3,3)["humanNeed"],3)
    def test_invalid_auto_input(self):
        for impact,confidence in ((-1,0),(4,1),(True,1),(0,False)):
            with self.assertRaises(ValueError):route(impact,confidence)
        with self.assertRaises(ValueError):route(0,3,privileged=1)
    def test_2by2_4by4_8by8_cannot_shrink(self):
        for shape in ("twoByTwo","fourByFour","eightByEight"):
            d=copy.deepcopy(self.doc);d["matrices"][shape]["rows"].pop()
            self.assertIn("MATRIX_"+shape,validate(d))
    def test_no_automatic_release_or_merge(self):
        for field in ("autoMerge","autoSign","autoDeploy","autoCallAI","autoNetworkCrawl","autoGrub"):
            d=copy.deepcopy(self.doc);d["permissions"][field]=True
            self.assertIn("AUTHORITY_"+field,validate(d))
    def test_fixture_link_spider_and_missing_import(self):
        with tempfile.TemporaryDirectory() as t:
            r=Path(t);(r/"tools").mkdir()
            (r/"tools/main.py").write_text("from tools.helper import foo\n",encoding="utf-8")
            (r/"tools/helper.py").write_text("def foo():return 1\n",encoding="utf-8")
            a=spider(r,self.doc,roots=["tools/main.py"])
            self.assertEqual(a["nodesVisited"],2)
            self.assertEqual(a["edgesChecked"],1)
            self.assertEqual(a["status"],"PASS_LOCAL_SOURCE_ONLY")
            (r/"tools/helper.py").unlink()
            b=spider(r,self.doc,roots=["tools/main.py"])
            self.assertIn("MISSING_LOCAL_SOURCE:tools/helper.py",b["errors"])
    def test_reject_outside_and_symlinks(self):
        with tempfile.TemporaryDirectory() as t:
            r=Path(t);(r/"a.py").write_text("pass\n")
            with self.assertRaises(ValueError):_canonical(r,"../outside.py",200)
            (r/"link.py").symlink_to(r/"a.py")
            with self.assertRaises(ValueError):_canonical(r,"link.py",200)
    def test_html_asset_traversal_and_external_script(self):
        refs=list(references("frontEnd/rootlessCockpit/index.html",b'<script src="/app.js"></script><link rel="stylesheet" href="/app.css">'))
        self.assertIn("frontEnd/rootlessCockpit/app.js",refs)
        with self.assertRaises(ValueError):list(references("frontEnd/rootlessCockpit/index.html",b'<script src="https://example.org/x.js"></script>'))
    def test_javascript_module_reference(self):
        refs=list(references("frontEnd/rootlessCockpit/app.js",b'import {x} from "./avatar3d.mjs";'))
        self.assertEqual(refs,["frontEnd/rootlessCockpit/avatar3d.mjs"])
    def test_opaque_unknown_evidence_never_gives_crown(self):
        for impact in range(4):
            for confidence in range(4):
                r=route(impact,confidence)
                self.assertEqual(r["crown"],"STOP")
                self.assertFalse(r["machineMayWriteProtectedMain"])
if __name__=="__main__":unittest.main()

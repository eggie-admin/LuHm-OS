"""Bounded HTML5 + native custom-element + inert AI JSON projection tests."""
import json
import re
import subprocess
import unittest
from pathlib import Path
from html.parser import HTMLParser

ROOT=Path(__file__).resolve().parents[1]
HTML=(ROOT/"host/harness/index.html").read_text(encoding="utf-8")
JS=(ROOT/"host/harness/cockpit.js").read_text(encoding="utf-8")
YAML_PATH=ROOT/"doctrine/webShellInteropV1.yaml"

class DocumentProbe(HTMLParser):
    def __init__(self):
        super().__init__()
        self.head=False
        self.body=False
        self.metadata=set()
        self.scriptSrc=[]
        self.customBody=False
        self.inertJson=False
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if tag=="head":self.head=True
        if tag=="body":self.body=True
        if tag=="meta" and self.head:
            self.metadata.add(d.get("name",d.get("charset","")))
        if tag=="script" and d.get("src"):
            self.scriptSrc.append(d["src"])
        if tag=="luhm-runtime-badge" and self.body:
            self.customBody=True
        if tag=="script" and d.get("id")=="luhmUiProjection" and d.get("type")=="application/json" and self.body:
            self.inertJson=True
    def handle_endtag(self,tag):
        if tag=="head":self.head=False

class WebShellInteropTests(unittest.TestCase):
    def test_standards_head_and_same_origin_static_assets(self):
        self.assertTrue(HTML.lstrip().lower().startswith("<!doctype html>"))
        doc=DocumentProbe();doc.feed(HTML)
        self.assertTrue({"utf-8","viewport","description","application-name","theme-color"}.issubset(doc.metadata))
        self.assertTrue(doc.customBody and doc.inertJson)
        self.assertTrue(doc.scriptSrc)
        self.assertTrue(all(src.startswith("/harness/assets/") for src in doc.scriptSrc))
        self.assertIn('href="/harness/assets/luhmSigil.svg"',HTML)

    def test_ai_json_is_not_an_authority_command(self):
        match=re.search(r'<script type="application/json" id="luhmUiProjection">(.*?)</script>',HTML,re.S)
        self.assertIsNotNone(match)
        projection=json.loads(match.group(1))
        self.assertEqual(projection,{"schema":"luhmOs.uiProjection.v1","authority":"displayOnly","state":"SOURCE_CANDIDATE"})
        self.assertNotIn("webhookSecret",match.group(1))

    def test_registered_custom_element_validates_projection(self):
        self.assertIn('customElements.define("luhm-runtime-badge"', JS)
        trailer=JS.split("// LuHm original HTML custom element; JSON is an untrusted display projection.")[1]
        runner="""
"use strict";
const text=process.argv[1];
const projection=JSON.parse(process.argv[2]);
const registry={};
const customElements={get:n=>registry[n],define:(n,c)=>registry[n]=c};
class HTMLElement{constructor(){this.textContent="initial";}}
const document={getElementById:id=>({textContent:JSON.stringify(projection)})};
new Function("customElements","HTMLElement","document",text)(customElements,HTMLElement,document);
const Widget=registry["luhm-runtime-badge"];
if(!Widget)throw Error("component missing");
const x=new Widget();x.connectedCallback();process.stdout.write(x.textContent);
"""
        def output(item):
            run=subprocess.run(["node","-e",runner,trailer,json.dumps(item)],capture_output=True,text=True,timeout=10)
            self.assertEqual(run.returncode,0,run.stderr)
            return run.stdout
        self.assertEqual(output({"schema":"luhmOs.uiProjection.v1","authority":"displayOnly","state":"SOURCE_CANDIDATE"}),"◈ source candidate")
        self.assertEqual(output({"schema":"luhmOs.uiProjection.v1","authority":"crown","state":"GREEN"}),"◈ state unavailable")

    def test_yaml_policy_and_webhook_off_switch(self):
        import yaml
        d=yaml.safe_load(YAML_PATH.read_text(encoding="utf-8"))
        self.assertEqual(d["schema"],"luhmOs.webShellInterop.v1")
        self.assertEqual(d["crownStatus"],"STOP")
        self.assertFalse(d["webhooks"]["enabled"])
        self.assertFalse(d["webhooks"]["publicEndpointInstalled"])
        self.assertEqual(d["operationalState"],"existingApprovedSqlFirst")
        self.assertFalse(d["html"]["javascript"]["externalCdnRuntimeScripts"])
        self.assertFalse(d["aiJsonPipeline"]["browserCanApproveMutations"])

    def test_legacy_luhm_cockpit_controls_not_deleted(self):
        for t in ('id="crownLaunchGlass"','id="petDock"','id="crownViewportSlot"','id="dropZone"','id="edgeBadge"'):
            self.assertIn(t,HTML)
        for dep in ("jquery-3.7.1.min.js","jquery-ui-1.14.2.min.js","cockpit.js"):
            self.assertIn(dep,HTML)

if __name__=="__main__":unittest.main()

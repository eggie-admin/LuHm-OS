#!/usr/bin/env python3
"""Exact seven-plane studio source gate. Static proof only, not a deployed Vue/3D claim."""
import json
from html.parser import HTMLParser
from pathlib import Path

root=Path(__file__).resolve().parents[1]
class Inspect(HTMLParser):
    def __init__(self):
        super().__init__();self.planes=[];self.ids=set();self.duplicate=False
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if "id" in a:
            self.duplicate=self.duplicate or a["id"] in self.ids
            self.ids.add(a["id"])
        if "data-stage-plane" in a:self.planes.append((a["data-stage-plane"],a.get("data-depth")))
def verify(html,css,js,canon):
    errors=[]
    def need(ok,msg):
        if not ok:errors.append(msg)
    scan=Inspect();scan.feed(html)
    expected=[(row["id"],str(row["depth"])) for row in canon["planes"]]
    need(not scan.duplicate,"duplicateHtmlId")
    need(len(scan.planes)==7 and sorted(scan.planes)==sorted(expected),"sevenPlaneNamesAndDepths")
    need(all(x in scan.ids for x in ["studioSevenLayerStage","studioCharacter","studioStageBlink","studioStageWave","studioStageExpression","studioStageMotion","studioStageStatus"]),"liveControls")
    need("aria-label" in html and 'role="status"' in html,"accessibility")
    need("data-seven-layer-stage" in html and 'data-stage-plane="glassWidgetDock"' in html,"interactiveGlass")
    need("data-stage-plane=\"foregroundAtmosphere\"".replace("\\","") in html or "foregroundAtmosphere" in html,"foreground")
    need("[data-stage-plane=\"foregroundAtmosphere\"]" in css,"pointerBypassStyle")
    need("pointer-events:none" in css,"pointerBypass")
    need("@media(prefers-reduced-motion:reduce)" in css,"motionSafetyCss")
    need("function depthOffsets(" in js and "function initializeSevenLayerStage(" in js,"depthController")
    need('addEventListener("scroll",queue,{passive:true})' in js and 'addEventListener("pagehide",cleanup' in js,"cleanup")
    need("Number.isFinite(Number(scrollY))" in js and "Math.min(1200" in js,"boundedScroll")
    need(all(x not in html for x in ["https://drive.google.com/","<script src=","<iframe src="]),"noExposedPrivateOrAutoload")
    need(canon.get("implementation",{}).get("vue3Runtime")=="SOURCE_ONLY_NOT_BUNDLED","noFalseVueClaim")
    need(canon.get("guards",{}).get("privateMediaNotPublic") is True and canon.get("crownStatus")=="STOP","rightsAndCrown")
    return errors
def main():
    html=(root/"host/harness/studioDeck.html").read_text()
    css=(root/"host/harness/studioDeck.css").read_text()
    js=(root/"host/harness/studioDeck.js").read_text()
    canon=json.loads((root/"doctrine/layeredStageCanonV1.json").read_text())
    assert not verify(html,css,js,canon),verify(html,css,js,canon)
    mutated=html.replace('data-stage-plane="liveCharacter"','data-stage-plane="wrongCharacter"')
    assert verify(mutated,css,js,canon),"negative plane mutation escaped"
    mutated=css.replace("@media(prefers-reduced-motion:reduce)","@media(min-width:1px)")
    assert verify(html,mutated,js,canon),"negative CSS motion mutation escaped"
    mutated=js.replace("Math.min(1200","Math.min(99999")
    assert verify(html,css,mutated,canon),"negative scroll bound mutation escaped"
    print("GREEN_SEVEN_LAYER_STUDIO_SOURCE_ONLY_AND_THREE_NEGATIVE_CONTROLS")
if __name__=="__main__":main()

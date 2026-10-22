#!/usr/bin/env python3
"""Canonical 7-plane main-source integrity: source proof never means Vue/3D/host deployment."""
from html.parser import HTMLParser
import copy
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class Scan(HTMLParser):
    def __init__(self):
        super().__init__();self.planes=[];self.ids=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if "data-stage-plane" in a:self.planes.append(a["data-stage-plane"])
        if "id" in a:self.ids.append(a["id"])
def assess(stage,truth,html,css,script):
    red=[]
    def need(value,label):
        if not value:red.append(label)
    expected=[x["id"] for x in stage.get("planes",[])]
    scan=Scan();scan.feed(html)
    need(stage.get("schema")=="luhmOs.layeredStageCanon.v1","schema")
    need(len(expected)==7 and sorted(scan.planes)==sorted(expected),"sevenPlaneSourceDrift")
    need(len(scan.ids)==len(set(scan.ids)),"duplicateId")
    need(stage.get("currentSource",{}).get("primaryRepository")=="eggie-admin/LuHm-OS","repository")
    need(stage.get("currentSource",{}).get("mergedPullRequest")==371,"prIdentity")
    need(stage.get("currentSource",{}).get("mergedMainSourceRef") is None,"noDuplicatedSourceAlias")
    need(stage.get("currentSource",{}).get("vue3Runtime")=="NOT_BUNDLED_IN_CURRENT_PRODUCTION","vueTruth")
    need(stage.get("currentSource",{}).get("liveChatGptUiMount")=="UNVERIFIED","hostTruth")
    need(stage.get("currentSource",{}).get("productionPromotion") is False,"noPromotion")
    need(truth.get("layeredStage",{}).get("contract")=="doctrine/layeredStageCanonV1.json","truthPointer")
    need(truth.get("layeredStage",{}).get("mergedPullRequest")==371,"truthMainPr")
    need(truth.get("activeCompatibilityOrder",{}).get("first")=="chatGptOpenAi" and truth.get("activeCompatibilityOrder",{}).get("second")=="github","compatibilityOrder")
    need(truth.get("canonicalRepository")=="eggie-admin/LuHm-OS" and truth.get("crownStatus")=="STOP","authority")
    need(all(x in scan.ids for x in ["lum2dStage","lum2dBlink","lum2dSmile","lum2dWave","lum2dPause","pocketmascot","studioBackdropFrame"]),"interactiveSource")
    need('id="studioBackdropFrame"' in html and 'src="https' not in html,"noAutoloadOfMedia")
    need("pointer-events:none" in css and "@media(prefers-reduced-motion:reduce)" in css,"cssReducedMotion")
    need("function initLumLive2d()" in script and "function mountDepth(" in script and "requestAnimationFrame" in script,"sharedInteraction")
    need("serverWrites" not in stage.get("currentSource",{}),"noUnexpectedAuthority")
    return red
def main():
    paths=["doctrine/layeredStageCanonV1.json","doctrine/currentSourceTruthV3.json"]
    stage,truth=[json.loads((ROOT/path).read_text()) for path in paths]
    html=(ROOT/"host/harness/studioDeck.html").read_text()
    css=(ROOT/"host/harness/studioDeck.css").read_text()
    script=(ROOT/"host/harness/studioDeck.js").read_text()
    errors=assess(stage,truth,html,css,script)
    assert not errors,errors
    wrong=html.replace('data-stage-plane="liveCharacter"','data-stage-plane="fakeCharacter"')
    assert assess(stage,truth,wrong,css,script),"wrongPlaneNotCaught"
    copied=copy.deepcopy(stage);copied["currentSource"]["vue3Runtime"]="PRODUCTION"
    assert assess(copied,truth,html,css,script),"fakeVueNotCaught"
    copied=copy.deepcopy(truth);copied["activeCompatibilityOrder"]["second"]="drive"
    assert assess(stage,copied,html,css,script),"fakeGithubNotCaught"
    print("GREEN_SEVEN_LAYER_SOURCE_CURRENT_MAIN_PROVEN_WITH_THREE_NEGATIVE_CONTROLS")
    print("LIVE_CHATGPT_VUE3_PRIVATE_GLB_RUNTIME=UNVERIFIED")
if __name__=="__main__":main()

#!/usr/bin/env python3
"""Exact source-only WebGL Crown Cathedral audit; zero network, zero writes."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
def read(path: str)->str:
    return (ROOT/path).read_text(encoding="utf-8")

def verify(contract, quarantine, layout, renderer, html, main, css):
    problems=[]
    def need(value, reason):
        if not value: problems.append(reason)
    need(contract.get("schema")=="luhmOs.crownCathedralWebglCast.v1","schema")
    need(contract.get("status")=="SOURCE_CANDIDATE_UNDEPLOYED","stage")
    need(contract.get("authority")=="Professor","authority")
    need(contract.get("source",{}).get("repository")=="eggie-admin/LuHm-OS","source")
    need(len(contract.get("fourLayers",[]))==4,"fourLayers")
    need(contract.get("fourByFour",{}).get("current")=="sourceReviewed","noFakeDeviceGreen")
    need(contract.get("gates",{}).get("publicCrown")=="STOP","crownStop")
    need(contract.get("gates",{}).get("samsungTouchGpu")=="NOT_PROVEN","noFakeSamsung")
    need(contract.get("gates",{}).get("deployExactHead")=="NOT_PROVEN","noFakeDeployment")
    need(contract.get("world",{}).get("geometryMaxPerPreset")==128,"geometryBudget")
    need(contract.get("world",{}).get("live2dActualModelMounted") is False,"live2dUnproven")
    need(quarantine.get("state")=="QUARANTINED" and quarantine.get("activeTaskWorkersAllowed") is False,"workerQuarantine")
    need('export function buildCrownLayout' in layout and 'parts.length>128' in layout,"strictLayout")
    need('const allowed = new Set(["box","sphere","cylinder","torus"])' in layout,"typeAllowlist")
    need('NOT the approved rigged/Live2D Canon Lum asset' in layout,"honestArtProxy")
    need(not re.search(r'\b(?:fetch|XMLHttpRequest|WebSocket|Worker|eval)\s*\(',layout),"noCodeNetworkInLayout")
    need(not re.search(r'https?://|<script|javascript:',layout,re.I),"noUrlInLayout")
    need('import { buildCrownLayout }' in renderer and 'setEnvironment("cathedral")' in renderer,"worldHook")
    need('clearEnvironment()' in renderer and 'material.dispose()' in renderer and 'mesh.dispose()' in renderer,"gpuCleanup")
    need('new Engine(canvas' in renderer and 'engine.setHardwareScalingLevel' in renderer,"singleBabylonAndMobileScale")
    need('if (!document.hidden) scene.render()' in renderer,"hiddenTabRendering")
    need(not re.search(r'new Worker\s*\(|fetch\s*\(',renderer),"noUntrustedWorkerOrFetch")
    for mode in ("cathedral","riverwalk","workshop"):
        need('data-world-mode="'+mode+'"' in html,"button-"+mode)
    need('world.setEnvironment(button.dataset.worldMode)' in main,"typedSceneSwitch")
    need('id="world-proof"' in html and 'aria-live="polite"' in html,"visualReceipt")
    need('prefers-reduced-motion' in css and 'min-height:44px' in css,"mobileAccessibility")
    need(not re.search(r'<script[^>]+src=.https?://',html,re.I),"noCdn")
    return problems

def main()->int:
    try:
        contract=json.loads(read("doctrine/crownCathedralWebglCastV1.json"))
        quarantine=json.loads(read("doctrine/companyWideOperationalQuarantineV1.json"))
        layout=read("frontEnd/prototypes/glassWorld/src/crown-cathedral-layout.mjs")
        renderer=read("frontEnd/prototypes/glassWorld/src/babylon-world.js")
        html=read("frontEnd/prototypes/glassWorld/index.html")
        main=read("frontEnd/prototypes/glassWorld/src/main.js")
        css=read("frontEnd/prototypes/glassWorld/style.css")
        args=(contract,quarantine,layout,renderer,html,main,css)
        errors=verify(*args)
        negative={
            "forbiddenCrownGreen":lambda: verify({**contract,"gates":{**contract["gates"],"publicCrown":"GREEN"}},*args[1:]),
            "remoteLayoutUrl":lambda: verify(contract,quarantine,layout+'https://bad.example',renderer,html,main,css),
            "lostDisposal":lambda: verify(contract,quarantine,layout,renderer.replace("material.dispose()","material.wipe()"),html,main,css),
            "missingUiControl":lambda: verify(contract,quarantine,layout,renderer,html.replace('data-world-mode="riverwalk"',"data-world-type=\"riverwalk\""),main,css),
            "lostQuarantine":lambda: verify(contract,{**quarantine,"state":"ACTIVE"},layout,renderer,html,main,css)
        }
        bad_controls=[name for name,probe in negative.items() if not probe()]
        if bad_controls:errors.append("NEGATIVE_CONTROLS_ACCEPTED:"+",".join(bad_controls))
        print(json.dumps({"sourceVerdict":"CROWN_WEBGL_SOURCE_GREEN" if not errors else "CROWN_WEBGL_SOURCE_RED",
          "errors":errors,"negativeControlsRejected":len(negative)-len(bad_controls),
          "webglBrowserProof":"NOT_TESTED","physicalSamsungProof":"NOT_TESTED",
          "installedLive2d":"NOT_PROVEN","publicCrown":"STOP"},sort_keys=True))
        return 0 if not errors else 1
    except (ValueError,TypeError,KeyError,OSError) as ex:
        print(json.dumps({"sourceVerdict":"CROWN_WEBGL_SOURCE_RED","errorType":type(ex).__name__,"publicCrown":"STOP"}))
        return 1
if __name__=="__main__":
    sys.exit(main())

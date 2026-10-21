#!/usr/bin/env python3
"""Read-only source audit of public Pocket Art Studio; not browser/device proof."""
from pathlib import Path
from html.parser import HTMLParser
import json
ROOT=Path(__file__).resolve().parents[1]
page=(ROOT/"publicationSite/pocketLab.html").read_text()
home=(ROOT/"publicationSite/index.html").read_text()
manifest=json.loads((ROOT/"plugins/luhm-os/assets/pocketArtPackV1.json").read_text())
checks=[]
def check(name,good):checks.append((name,bool(good)))
class Scanner(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags=[]
        self.attrs={}
    def handle_starttag(self,tag,attrs):
        self.tags.append(tag)
        for k,v in attrs:
            if k=="id":self.attrs[v]=tag
scan=Scanner();scan.feed(page)
check("doctype",page.lower().lstrip().startswith("<!doctype html>"))
check("viewport",'<meta name="viewport"' in page)
check("publicHomepageLink",'/pocketLab.html' in home)
check("privateSourceNotExposed",'/Google Drive/' not in page and "LuHmOS_Rebel_PrivateProduction" not in page)
check("interactiveSvg","svg" in scan.tags)
check("heartButton",scan.attrs.get("bond")=="button")
check("blinkButton",scan.attrs.get("blink")=="button")
check("castButton",scan.attrs.get("cast")=="button")
check("pauseButton",scan.attrs.get("pause")=="button")
check("paletteSelector",scan.attrs.get("palette")=="select")
check("sceneSelector",scan.attrs.get("scene")=="select")
check("statusRegion",scan.attrs.get("expression")=="p")
check("petSvgNamed",scan.attrs.get("mascot")=="svg")
check("heartsLayer",scan.attrs.get("bondHearts")=="div")
check("reducedMotion",'prefers-reduced-motion' in page)
check("pauseMotion",'.classList.toggle("reduced")' in page)
check("sixSceneStates",all(s in page for s in ['cathedral','city','lab','stars','portal','forest']))
check("paletteModes",all(s in page for s in ['cyan','pink','purple']))
check("toneSynth",'AudioContext' in page)
check("noNetworkRequests",all(w not in page for w in ['fetch(', 'XMLHttpRequest', 'WebSocket(', 'EventSource(', 'navigator.sendBeacon']))
check("noLogin",'<form' not in page and 'password' not in page)
check("noAnalytics",all(w not in page for w in ['googletag','analytics.js','gtag(']))
check("noLocalStorage",all(w not in page for w in ['localStorage','sessionStorage','document.cookie']))
check("noRawHtmlInjection",'innerHTML' not in page and 'document.write' not in page)
check("noExternalJs",'<script src=' not in page)
check("noExternalCss",'<link rel="stylesheet"' not in page)
check("honestAgentStatus","not an autonomous AI agent" in page)
check("godotProofQualified","Godot/Blender rig" in page)
check("noCredentialsInSource",'sk-proj-' not in page and '-----BEGIN PRIVATE KEY-----' not in page)
check("sourceCatalogShape",manifest["schema"]=="luhmOs.pocketArtAssetPack.v1")
check("countKnown",manifest["assetCount"]==110)
check("sumCategories",sum(manifest["counts"].values())==110)
check("zipHash",len(manifest["sourcePackSha256"])==64)
check("rightsHonesty","not approved public character canon" in manifest["rights"])
check("thirdPartyNotBundled","no downloaded binaries" in manifest["externalAssets"])
check("runtimeUnverified","not yet verified" in manifest["platformProof"])
check("workersNotRunning","No autonomous workers" in manifest["autonomousAgents"])
check("publicReleaseHold",manifest["safety"]["autoRelease"] is False)
check("noPrivateRebelMedia",manifest["safety"]["privateRebelMedia"] is False)
for name,good in checks:print(("PASS" if good else "FAIL")+" "+name)
print(f"POCKET_LAB_SOURCE={sum(x[1] for x in checks)}/{len(checks)}")
if len(checks)<30 or not all(x[1] for x in checks):raise SystemExit(1)

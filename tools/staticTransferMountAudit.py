#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
errors=[]

def need(ok,msg):
    if not ok:
        errors.append(msg)

def load(path):
    return json.loads((ROOT/path).read_text(encoding="utf-8"))

seq=load("doctrine/pet-sprite-sequence-v1.json")
mount=load("doctrine/static-transfer-mount-v1.json")
traffic=load("doctrine/cloudflareAirTrafficControllerV1.json")
presentation=load("doctrine/characterPetPresentationV1.json")
sourceSprites=load("doctrine/agentLoadingSpriteManifestV1.json")
runtimeSprites=load("host/harness/agent-loading-sprites.json")
css=(ROOT/"host/harness/cockpit.css").read_text(encoding="utf-8")
server=(ROOT/"host/mcp/luhmHarness.py").read_text(encoding="utf-8")
widget=(ROOT/"host/harness/widget.html").read_text(encoding="utf-8")

need(seq.get("schema")=="luhmOs.petSpriteSequence.v1","sprite sequence schema drift")
fc=seq.get("frameContract",{})
need(fc.get("framesPerSequence")==32,"pet sequence must contain 32 frames")
need(fc.get("sheetColumns")==8 and fc.get("sheetRows")==4,"pet sheet must be 8x4")
need(seq.get("stageContract",{}).get("priority")=="largestPossibleWithoutOccludingEssentialControls","large-stage priority drift")
need(seq.get("stageContract",{}).get("desktopMaxCssPx")>=720,"desktop stage cap too small")
need(seq.get("communityDonorLaw",{}).get("unknownLicense")=="QUARANTINE","unknown community license must quarantine")
need(seq.get("communityDonorLaw",{}).get("donorWorkNeverImpliedAsLuHmAuthorship") is True,"donor authorship law missing")

need(mount.get("schema")=="luhmOs.staticTransferMount.v1","static transfer schema drift")
need(mount.get("states",{}).get("sourceMount")=="PRESENT","source mount should record source presence")
need(mount.get("states",{}).get("cloudflareCdn")=="VERIFY","CDN must remain VERIFY")
need(mount.get("states",{}).get("chatGptPetVisibility")=="VERIFY","ChatGPT pet visibility must remain VERIFY")
need(mount.get("petPresentation",{}).get("targetFramesPerSequence")==32,"mount frame target drift")

lane=traffic.get("lanes",{}).get("staticAssets",{})
need(lane.get("contract")=="doctrine/static-transfer-mount-v1.json","traffic controller not bound to static mount")
need(lane.get("sourceMountState")=="PRESENT_IN_SOURCE","source mount state drift")
need(lane.get("cloudflareCdnState")=="VERIFY","traffic controller must not claim live CDN")

need(presentation.get("petSystem",{}).get("spriteSequenceContract")=="doctrine/pet-sprite-sequence-v1.json","pet presentation sequence contract missing")
need(presentation.get("petSystem",{}).get("animation",{}).get("framesPerSequence")==32,"pet presentation frame count drift")

sourceIds=sourceSprites.get("agentIds",[])
runtimeIds=[x.get("agentId") for x in runtimeSprites.get("sprites",[])]
need(sourceIds==runtimeIds,"source/runtime sprite roster drift")
need("PET_ASSET_IDS" in server and 'parts[0] == "pets"' in server,"strict pet namespace missing")
need('{"sequence.webp", "sequence.png", "sequence.json"}' in server,"pet sequence extension allowlist missing")
need("image-rendering:pixelated" in css and "720px" in css and "94vw" in css,"large crisp pet stage CSS missing")
need('staticMount:staticLane?.sourceMountState||"VERIFY"' in widget,"widget static mount truth missing")
need('staticCdn:staticLane?.cloudflareCdnState||"VERIFY"' in widget,"widget static CDN truth missing")
need('staticAssets:"PRESENT"' not in widget,"widget still hardcodes static asset GREEN")

if errors:
    print("STATIC_TRANSFER_MOUNT_AUDIT=RED")
    for e in errors:
        print(" -",e)
    raise SystemExit(1)

print("STATIC_TRANSFER_MOUNT_AUDIT=GREEN")
print("frames=32")
print("sheet=8x4")
print("sourceMount=PRESENT")
print("runtimeMount=VERIFY")
print("cloudflareCdn=VERIFY")
print("chatGptPetVisibility=VERIFY")
print("crown=STOP")

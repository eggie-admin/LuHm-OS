#!/usr/bin/env python3
"""Source-only audit of a user-supplied mobile browser recording receipt."""
import copy
import json
import re
from pathlib import Path

root=Path(__file__).resolve().parents[1]

def load(path):
    return json.loads((root/path).read_text(encoding="utf-8"))

def validate(receipt,truth):
    issues=[]
    def need(test,message):
        if not test:
            issues.append(message)
    t=truth.get("experienceLayer",{}).get("mobileChromeCanaryVideo",{})
    need(receipt.get("schema")=="luhmOs.chromeCanaryFirstNightBrowserProof.v1","receipt schema drift")
    need(receipt.get("state")=="GREEN_SCOPED_MOBILE_BROWSER_UI","video scope drift")
    need(t.get("contract")=="doctrine/chromeCanaryFirstNightBrowserProofV1.json","missing source truth link")
    need(t.get("videoSha256")==receipt.get("recording",{}).get("sha256"),"source truth/video digest mismatch")
    need(re.fullmatch(r"[0-9a-f]{64}",receipt.get("recording",{}).get("sha256","")) is not None,"bad video digest")
    need(receipt.get("recording",{}).get("rawVideoStoredInPublicRepo") is False,"private video published")
    need(receipt.get("visibleEvidence",{}).get("godotWebExport")=="WEB_EXPORT_PENDING","playable export falsely claimed")
    need(receipt.get("visibleEvidence",{}).get("modeStateSelectionVisiblyWorks") is True,"observed mode selection lost")
    need(receipt.get("sourceOfRecording")=="UNVERIFIED_BY_VIDEO","source SHA inferred without proof")
    for key in ("androidApkInstalled","physicalNativeWebViewRuntime","godotPlayableWebRuntime","chatGptHostPluginInvocation","publicStorePublication"):
        need(receipt.get("limits",{}).get(key) is False,"fabricated platform proof: "+key)
    need(t.get("chatGptHostRuntime")=="UNVERIFIED" and t.get("androidApkInstall")=="UNVERIFIED","browser proof promoted to host/native")
    need(truth.get("androidLayer",{}).get("physicalSamsungProof")=="PENDING","device claim drift")
    need(truth.get("finalFormRelease",{}).get("browserUiVideoEvidence")=="doctrine/chromeCanaryFirstNightBrowserProofV1.json","release gate evidence link drift")
    need(truth.get("finalFormRelease",{}).get("publicReleaseGreen") is False,"video improperly grants release GREEN")
    need(receipt.get("crownStatus")=="STOP","Crown drift")
    return issues

receipt=load("doctrine/chromeCanaryFirstNightBrowserProofV1.json")
truth=load("doctrine/currentSourceTruthV3.json")
issues=validate(receipt,truth)
fake=copy.deepcopy(receipt)
fake["limits"]["androidApkInstalled"]=True
if not validate(fake,truth):
    issues.append("negative control failed: fake APK install")
fake=copy.deepcopy(receipt)
fake["visibleEvidence"]["godotWebExport"]="PLAYABLE"
if not validate(fake,truth):
    issues.append("negative control failed: fake web export")
print(json.dumps({"status":"GREEN_BROWSER_VIDEO_RECEIPT_CONTRACT" if not issues else "RED_BROWSER_VIDEO_RECEIPT","runtimeSource":"USER_SUPPLIED_SCREEN_RECORDING","auditScope":"receipt consistency only; raw MP4 not published or re-decoded by CI","issues":issues,"androidInstall":"UNVERIFIED","godotWebExport":"PENDING","chatGptHost":"UNVERIFIED","crownStatus":"STOP"},indent=2))
raise SystemExit(1 if issues else 0)

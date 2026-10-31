#!/usr/bin/env python3
"""4x4 media/AI/3D/static/web VLC vendor-reduction source audit. Never pings providers or runs codecs."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
POLICY=ROOT/"doctrine/mediaStudioFourByFourV1.json"
PACKAGE=ROOT/"frontEnd/prototypes/glassWorld"
def audit(p):
    e=[]
    def need(ok,code):
        if not ok:e.append(code)
    need(p.get("schema")=="luhmOs.mediaStudioFourByFour.v1" and p.get("status")=="SOURCE_CANDIDATE","POLICY")
    need(p.get("authority")=="Professor" and p.get("crown")=="STOP","CROWN")
    m=p.get("matrix",{});rows=m.get("rows",[]);cols=m.get("columns",[]);cells=m.get("cells",[])
    need(rows==["AI","3D","StaticWeb","Runtime"] and cols==["source","rightsAndSecurity","performance","fallback"],"FOUR_ROWS_COLS")
    need(len(cells)==16 and {(c.get("row"),c.get("column")) for c in cells if isinstance(c,dict)}=={(r,c) for r in rows for c in cols}
         and all(isinstance(c,dict) and c.get("status")=="PROPOSED_SOURCE_ONLY" for c in cells),"FOUR_BY_FOUR_PROOF_SCOPE")
    need(m.get("realHardwareTestsByPolicy")==0,"FAKE_TESTS")
    st=p.get("stack",{})
    need(st.get("events")=="Native CustomEvent" and st.get("python")=="stdlib3+sqlite3" and
         st.get("aiCloudCallsEnabled") is False,"STACK_BOUNDARY")
    v=p.get("vendor",{})
    for key in ("isolatedPrototypeJqueryPackageExpected","thirdPartyJsAdded","rendererAdded"):
        need(v.get(key) is False,"VENDOR_SCOPE_"+key)
    need(v.get("legacyJqueryWorkspaceIntact") is True and v.get("pythonPackagesAdded")==0,"LEGACY_OR_PYTHON_VENDOR")
    media=p.get("media",{})
    need(media.get("browser")=="HTML5_LOCAL_BLOB_ONLY" and
         set(media.get("previewFormats",[]))=={".mp4",".webm",".mp3",".wav",".ogg",".m4a",".webp",".png",".jpg",".jpeg",".avif"},"MEDIA_FORMATS")
    need(media.get("imageMaxBytes")==24*1024*1024 and media.get("avMaxBytes")==700*1024*1024,"MEDIA_BOUNDS")
    for key in ("remoteUrlsAllowed","autoplay","externalAssetUploads","mediaDecodeVerifiedOnSamsung"):
        need(media.get(key) is False,"MEDIA_UNSAFE_"+key)
    need(media.get("blobRevocationRequired") is True and media.get("pngEditableMaskMaster") is True and
         media.get("webpEditableMaster") is False,"IMAGE_MASTER_BOUNDARY")
    vlc=p.get("vlc",{})
    need(vlc.get("nativeLibrary")=="libVLC" and vlc.get("nativeAndroidModule")=="videolan/vlc-android/libvlc"
         and vlc.get("integration")=="OPTIONAL_SEPARATE_NATIVE_AAR_AFTER_OWNER_LICENSE_REVIEW","VLC_NATIVE_PLAN")
    for key in ("browserPluginSupported","npapiEnabled","aarInstalled","androidRuntimeProven",
                "desktopVlcExecutableRequiredOnTablet","serverVlcHttpInterfaceAllowed","secretInBrowserAllowed"):
        need(vlc.get(key) is False,"VLC_FALSE_PROOF_"+key)
    ping=p.get("pings",{})
    need(ping.get("mode")=="existing_loopback_health_only" and
         ping.get("target")=="127.0.0.1:8787/api/health" and
         ping.get("remoteHostScanAllowed") is False and ping.get("socketOrNetworkProbeInCI") is False
         and ping.get("providerApiPingsWithoutAuthorization") is False,"PING_ALLOWLIST")
    need(p.get("asset3d",{}).get("glbImportBuilt") is False and p.get("asset3d",{}).get("mocapHardwareProof") is False,"FAKE_3D")
    return sorted(set(e))
def inspect_sources():
    issues=[]
    package=json.loads((PACKAGE/"package.json").read_text(encoding="utf-8"))
    lock=json.loads((PACKAGE/"package-lock.json").read_text(encoding="utf-8"))
    d=package.get("dependencies",{})
    if (set(d) != {"@babylonjs/core", "vue"}
            or "jquery" in lock.get("packages", {}).get("", {}).get("dependencies", {})
            or "node_modules/jquery" in lock.get("packages", {})):
        issues.append("ISOLATED_JQUERY_NOT_REDUCED")
    if lock.get("packages",{}).get("",{}).get("dependencies")!=d:issues.append("NPM_LOCK_MISMATCH")
    for rel in ("src/jquery-bridge.js","src/media-deck.js"):
        text=(PACKAGE/rel).read_text(encoding="utf-8")
        if re.search(r"\bfrom\s*['\"]jquery['\"]",text):issues.append("UNPRUNED_JQUERY_IMPORT:"+rel)
        if "new CustomEvent(" not in text:issues.append("MISSING_CUSTOM_EVENT:"+rel)
    deck=(PACKAGE/"src/media-deck.js").read_text(encoding="utf-8")
    for value in ('".webp"','".png"','".avif"',"URL.revokeObjectURL","nativeVlcRunning: false"):
        if value not in deck:issues.append("MEDIA_SOURCE_MISSING:"+value)
    html=(PACKAGE/"index.html").read_text(encoding="utf-8")
    if "data-luhm-media-image" not in html or ".webp" not in html:issues.append("WEBP_DOM_MISSING")
    if not (ROOT/"frontEnd/jquery/luhm.cockpit.js").is_file():issues.append("LEGACY_JQUERY_DELETED")
    if not (ROOT/"tools/rootlessCastCockpit.py").is_file():issues.append("ROOTLESS_REMOVED")
    return sorted(set(issues))
def main():
    p=argparse.ArgumentParser();p.add_argument("--source-ref",required=True);p.add_argument("--output",type=Path,required=True);a=p.parse_args()
    if not re.fullmatch(r"[a-f0-9]{40}",a.source_ref):raise SystemExit("EXACT_SHA_REQUIRED")
    head=subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,capture_output=True,text=True)
    if head.returncode or head.stdout.strip()!=a.source_ref:raise SystemExit("EXACT_SOURCE_MISMATCH")
    issues=audit(json.loads(POLICY.read_text(encoding="utf-8")))+inspect_sources()
    receipt={"schema":"luhmOs.mediaStudioReceipt.v1","sourceRef":a.source_ref,"status":"PASS_SOURCE_ONLY_CROWN_STOP" if not issues else "RED_SOURCE",
     "errors":sorted(set(issues)),"matricesPlanned":16,"hardwareTests":0,"vlcAndroidEmbedded":False,"browserWebpDecoded":False,
     "originalSourceJqueryRuntimeDependencyRemoved":True if not issues else False,
     "remotePingsPerformed":0,"providerCalls":0,"crown":"STOP","manifestSha256":hashlib.sha256(POLICY.read_bytes()).hexdigest()}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:receipt[k] for k in ("status","sourceRef","errors","hardwareTests","vlcAndroidEmbedded","crown")},indent=2))
    if issues:raise SystemExit(2)
if __name__=="__main__":main()

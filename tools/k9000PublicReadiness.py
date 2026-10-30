#!/usr/bin/env python3
"""F-Droid release gate. PASS means source preflight only, NOT publication."""
import argparse
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def inspect(root: Path) -> dict:
    def read(path):
        p=root/path
        return p.read_text(encoding="utf-8") if p.is_file() else ""
    def png_dimensions(path):
        p=root/path
        if not p.is_file():
            return None
        data=p.read_bytes()[:24]
        if len(data)!=24 or data[:8]!=b"\x89PNG\r\n\x1a\n" or data[12:16]!=b"IHDR":
            return None
        return struct.unpack(">II",data[16:24])
    license_text=read("LICENSE")
    html=read("frontEnd/k9000.html")
    svg=read("frontEnd/brand/k9000-cathedral-mark.svg")
    kotlin=read("androidWeb3Plugin/plugin/src/main/java/art/eggiebagelface/luhmos/web3/AndroidWeb3CockpitPlugin.kt")
    preset=read("export_presets.cfg")
    short=read("fastlane/metadata/android/en-US/short_description.txt").strip()
    full=read("fastlane/metadata/android/en-US/full_description.txt").strip()
    canon=json.loads(read("doctrine/k9000CrownCathedralReleaseV1.json"))
    section=preset.split('name="Android Crown Cathedral Public Candidate"')
    public=section[1] if len(section)==2 else ""
    source={
        "gpl3License":"GNU GENERAL PUBLIC LICENSE" in license_text and "Version 3" in license_text,
        "originalBrandSvg":"<svg" in svg and "K9000 Crown Cathedral" in svg,
        "cockpitBrand":'brand/k9000-cathedral-mark.svg' in html,
        "publicPackage":'package/unique_name="art.eggiebagelface.luhmos.cathedral"' in public,
        "existingTestPackageUnaffected":'package/unique_name="art.eggiebagelface.luhmos.testing"' in preset,
        "distinctPublicApk":"crown-cathedral-public-candidate.apk" in public,
        "publicOffline":"permissions/internet=false" in public,
        "usbProbeNonprivileged":"requestPermission(" not in kotlin,
        "localWebView":'LOCAL_ORIGIN' in kotlin and 'isAllowedLocalUrl' in kotlin,
        "fastlaneShort":0<len(short)<80 and not short.endswith("."),
        "fastlaneFull":len(full)>100,
        "displayIdentity":canon["displayName"]=="LuHm-OS: Crown Cathedral",
        "noBundledModel":canon["ai"]["fDroidPackagedModel"] is False,
        "noSilentAiDownload":canon["ai"]["modelDownloadsAutomatic"] is False,
        "noKernelFlash":canon["backend"]["rootOrFlash"] is False,
        "noGpartedWebBridge":canon["backend"]["gpartedFromWebView"] is False,
        "nativeGodotBrand":'config/name="LuHm-OS: Crown Cathedral"' in read("project.godot"),
        "launcherMainPng":png_dimensions("frontEnd/brand/k9000-main-192.png")==(192,192),
        "launcherAdaptivePng":png_dimensions("frontEnd/brand/k9000-adaptive-432.png")==(432,432),
        "fdroid512Icon":png_dimensions("fastlane/metadata/android/en-US/images/icon.png")==(512,512)
    }
    gates={
        "allTransitiveLicenses":canon["licensing"]["allTransitiveFoss"]=="VERIFIED",
        "approvedAssetProvenance":canon["licensing"]["artRights"]=="VERIFIED",
        "approvedAssetWhitelist":(root/"doctrine/k9000ApprovedPublicAssetsV1.json").is_file(),
        "androidBuiltFromExactSource":canon["android"]["publicBuild"]=="VERIFIED",
        "samsungInstallAndUpdate":canon["android"]["installUpdate"]=="VERIFIED",
        "reproducibleSourceBuild":canon["gates"]["reproducibleBuild"]=="VERIFIED",
        "ownerSignerProvenance":canon["gates"]["buildSigned"]=="VERIFIED",
        "publicTag":canon["gates"].get("taggedRelease")=="VERIFIED",
        "actualScreenshot":(root/"fastlane/metadata/android/en-US/images/phoneScreenshots/1.png").is_file(),
        "approvedPublicPromotion":canon["gates"]["humanPromotion"] is True
    }
    return {"schema":"luhmOs.k9000PublicReadiness.v1","sourceChecks":len(source),
            "sourcePassed":sum(source.values()),"sourceFailures":[x for x,ok in source.items() if not ok],
            "publicationBlockers":[x for x,ok in gates.items() if not ok],
            "publishReady":all(source.values()) and all(gates.values()),
            "apkBuiltOrUploaded":False,"crownStatus":canon["gates"]["crownStatus"]}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--require-publication",action="store_true")
    a=parser.parse_args()
    result=inspect(ROOT)
    print(json.dumps(result,indent=2))
    if result["sourceFailures"]:
        raise SystemExit("RED_PUBLIC_SOURCE_CHECK")
    if a.require_publication and not result["publishReady"]:
        raise SystemExit("RED_PUBLIC_RELEASE_NOT_AUTHORIZED")
if __name__=="__main__":
    main()

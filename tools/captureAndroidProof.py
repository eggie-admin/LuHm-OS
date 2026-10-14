#!/usr/bin/env python3
"""Local, non-root Android evidence capture. Does not declare native UI proof."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

PACKAGE="art.eggiebagelface.luhmos.testing"
EXACT_DEBUG_SHA="0b0fdfbe25e8937abfe6e647cb23de53838e0189fc545d062aee73f57edd4f0e"
HASH=re.compile(r"^[0-9a-f]{64}$")


def shell(*args):
    out=subprocess.run(["adb","shell",*args],capture_output=True,text=True,timeout=25,check=True)
    return out.stdout.strip()


def parse_package_paths(output):
    paths=[]
    for line in output.splitlines():
        if line.startswith("package:"):
            path=line.partition(":")[2].strip()
            if not path.startswith("/data/app/") or "\n" in path or "\r" in path:
                raise ValueError("unexpected APK location")
            paths.append(path)
    if len(paths)!=1 or not paths[0].endswith("/base.apk"):
        raise ValueError("expected single installed base.apk; split packages require independent verification")
    return paths[0]


def parse_remote_sha(text):
    value=text.split()[0].lower() if text.strip() else ""
    if not HASH.fullmatch(value):
        raise ValueError("device SHA-256 not observed")
    return value


def parse_identity(dumpsys):
    version=re.search(r"\bversionName=([^\s]+)",dumpsys)
    code=re.search(r"\bversionCode=(\d+)",dumpsys)
    if not version or not code:
        raise ValueError("versionName/versionCode unavailable")
    return {"versionName":version.group(1),"versionCode":int(code.group(1))}


def self_test():
    assert parse_package_paths("package:/data/app/~~demo/app.test-1/base.apk") == "/data/app/~~demo/app.test-1/base.apk"
    for bad in ("", "package:/sdcard/rogue.apk", "package:/data/app/a/base.apk\npackage:/data/app/a/split.apk"):
        try:parse_package_paths(bad)
        except ValueError:pass
        else:raise AssertionError("unsafe package path accepted")
    assert parse_remote_sha("a"*64+"  /data/app/app/base.apk")=="a"*64
    assert parse_identity("versionCode=116 minSdk=24 targetSdk=36 versionName=1.0.16-samsunglayout.1")["versionCode"]==116
    print("GREEN_ANDROID_PROOF_CAPTURE_NEGATIVE_TESTS")


def capture(launch=False):
    devices=subprocess.run(["adb","devices"],capture_output=True,text=True,check=True,timeout=12)
    online=[x for x in devices.stdout.splitlines()[1:] if x.strip() and x.split()[-1]=="device"]
    if len(online)!=1:raise ValueError("connect exactly one unlocked and USB-debug-authorized Samsung")
    paths=parse_package_paths(shell("pm","path",PACKAGE))
    installed_sha=parse_remote_sha(shell("sha256sum",paths))
    details=parse_identity(shell("dumpsys","package",PACKAGE))
    os_level=shell("getprop","ro.build.version.sdk").strip()
    exact=installed_sha==EXACT_DEBUG_SHA
    launched=False
    if launch and exact:
        attempt=subprocess.run(["adb","shell","monkey","-p",PACKAGE,"-c","android.intent.category.LAUNCHER","1"],capture_output=True,text=True,timeout=30)
        launched=attempt.returncode==0 and "Events injected: 1" in attempt.stdout
    return {
        "schema":"luhmOs.androidPhysicalArtifactObservation.v1",
        "package":PACKAGE,"artifactSha256":installed_sha,
        "expectedDebugArtifactSha256":EXACT_DEBUG_SHA,"matchesExactDebugArtifact":exact,
        "installedVersion":details,"deviceApi":int(os_level) if os_level.isdigit() else "UNKNOWN",
        "launchCommandAccepted":launched,
        "firstLaunchScreenObserved":False,"nativeGodotInputProven":False,
        "signingCertLineageProven":False,"publicReleaseProven":False,
        "status":"ARTIFACT_MATCH_OBSERVED_LAUNCH_UI_PENDING" if exact else "PACKAGE_FOUND_ARTIFACT_UNBOUND",
        "crownStatus":"STOP",
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--self-test",action="store_true")
    ap.add_argument("--capture",action="store_true")
    ap.add_argument("--launch",action="store_true")
    ap.add_argument("--output",default="build/android/device-proof.json")
    args=ap.parse_args()
    if args.self_test:self_test()
    if not args.capture:return
    try:report=capture(args.launch)
    except (ValueError,subprocess.SubprocessError,FileNotFoundError) as e:
        raise SystemExit("RED_ANDROID_DEVICE_CAPTURE: "+str(e)) from e
    path=Path(args.output)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2))
    raise SystemExit(0 if report["matchesExactDebugArtifact"] else 2)


if __name__=="__main__":
    main()

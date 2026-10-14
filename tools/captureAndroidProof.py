#!/usr/bin/env python3
"""Read-only installed Android artifact observation; never mint device or release GREEN."""
from __future__ import annotations
import argparse
import json
import re
import subprocess
from pathlib import Path

PACKAGE="art.eggiebagelface.luhmos.testing"
HASH=re.compile(r"^[0-9a-f]{64}$")
SOURCE=re.compile(r"^[0-9a-f]{40}$")


def check_expected(source_ref: str, artifact_sha: str) -> None:
    if not SOURCE.fullmatch(source_ref):
        raise ValueError("exact 40-character sourceRef required")
    if not HASH.fullmatch(artifact_sha):
        raise ValueError("exact 64-character expected APK SHA-256 required")


def shell(*args: str) -> str:
    completed=subprocess.run(["adb","shell",*args],capture_output=True,text=True,timeout=25,check=True)
    return completed.stdout.strip()


def parse_package_paths(output: str) -> str:
    paths=[]
    for line in output.splitlines():
        if line.startswith("package:"):
            path=line.partition(":")[2].strip()
            if not path.startswith("/data/app/") or "\r" in path or "\n" in path:
                raise ValueError("unexpected APK location")
            paths.append(path)
    if len(paths)!=1 or not paths[0].endswith("/base.apk"):
        raise ValueError("single installed base APK required; split APK proof uses a separate lane")
    return paths[0]


def parse_remote_sha(output: str) -> str:
    value=output.split()[0].lower() if output.strip() else ""
    if not HASH.fullmatch(value):
        raise ValueError("device APK SHA-256 not observed")
    return value


def parse_identity(dumpsys: str) -> dict:
    version=re.search(r"\bversionName=([^\s]+)",dumpsys)
    code=re.search(r"\bversionCode=(\d+)",dumpsys)
    if not version or not code:
        raise ValueError("package version unavailable")
    return {"versionName":version.group(1),"versionCode":int(code.group(1))}


def capture(source_ref: str, expected_sha: str, request_launch: bool=False) -> dict:
    check_expected(source_ref,expected_sha)
    devices=subprocess.run(["adb","devices"],capture_output=True,text=True,timeout=12,check=True)
    authorized=[line for line in devices.stdout.splitlines()[1:]
                if line.strip() and line.split()[-1]=="device"]
    if len(authorized)!=1:
        raise ValueError("exactly one authorized Android device required")
    path=parse_package_paths(shell("pm","path",PACKAGE))
    installed_sha=parse_remote_sha(shell("sha256sum",path))
    info=parse_identity(shell("dumpsys","package",PACKAGE))
    api=shell("getprop","ro.build.version.sdk").strip()
    matched=(installed_sha==expected_sha)
    launched=False
    if request_launch and matched:
        result=subprocess.run(["adb","shell","monkey","-p",PACKAGE,
                               "-c","android.intent.category.LAUNCHER","1"],
                              capture_output=True,text=True,timeout=30)
        launched=(result.returncode==0 and "Events injected: 1" in result.stdout)
    return {
        "schema":"luhmOs.androidPhysicalArtifactObservation.v2",
        "expectedSourceRef":source_ref,"sourceRefVerifiedByDevice":False,
        "expectedArtifactSha256":expected_sha,
        "installedArtifactSha256":installed_sha,"exactInstalledArtifactMatched":matched,
        "package":PACKAGE,"installedVersion":info,
        "deviceApi":int(api) if api.isdigit() else "UNKNOWN",
        "launchCommandAccepted":launched,
        "nativeScreenObserved":False,"nativeGodotInputProven":False,
        "signingCertLineageProven":False,"publicReleaseProven":False,
        "status":"EXACT_ARTIFACT_MATCHED_SCREEN_PROOF_PENDING" if matched else "RED_INSTALLED_ARTIFACT_MISMATCH",
        "crownStatus":"STOP"}


def self_test() -> None:
    check_expected("a"*40,"b"*64)
    for sha,binary in (("main","b"*64),("a"*40,"old"),("a"*40,"c"*63)):
        try:check_expected(sha,binary)
        except ValueError:pass
        else:raise AssertionError("stale or invalid proof identity accepted")
    assert parse_package_paths("package:/data/app/~~app/demo/base.apk").endswith("/base.apk")
    for data in ("","package:/sdcard/untrusted.apk",
                 "package:/data/app/one/base.apk\npackage:/data/app/two/base.apk"):
        try:parse_package_paths(data)
        except ValueError:pass
        else:raise AssertionError("invalid package path accepted")
    assert parse_remote_sha("f"*64+"  /data/app/test/base.apk")=="f"*64
    assert parse_identity("versionCode=116 minSdk=24 targetSdk=36 versionName=1.0.16-samsunglayout.1")["versionCode"]==116
    print("GREEN_ANDROID_EXACT_BUILD_PROOF_NEGATIVE_CONTROLS")


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--self-test",action="store_true")
    parser.add_argument("--capture",action="store_true")
    parser.add_argument("--launch",action="store_true")
    parser.add_argument("--source-ref")
    parser.add_argument("--expected-sha256")
    parser.add_argument("--output",default="build/android/device-proof.json")
    args=parser.parse_args()
    if args.self_test:self_test()
    if not args.capture:return
    if not args.source_ref or not args.expected_sha256:
        raise SystemExit("RED_CAPTURE: --source-ref and --expected-sha256 are mandatory")
    try:
        result=capture(args.source_ref,args.expected_sha256,args.launch)
    except (ValueError,FileNotFoundError,subprocess.SubprocessError) as exc:
        raise SystemExit("RED_ANDROID_DEVICE_CAPTURE: "+str(exc)) from exc
    target=Path(args.output)
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if result["exactInstalledArtifactMatched"] else 2)


if __name__=="__main__":
    main()

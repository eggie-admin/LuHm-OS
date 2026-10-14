#!/usr/bin/env python3
"""Samsung Tab S10 Lite (SM-X400) first-public-preview preflight.

Source checks run without an APK. Installation needs a local exact APK, Android
SDK command-line tools and one explicitly authorized USB-debugged tablet.
No root, uninstall, data clear, app-private files, screenshot or network upload.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "art.eggiebagelface.luhmos.testing"
MODEL = "SM-X400"
SOURCE = re.compile(r"^[0-9a-f]{40}$")
DIGEST = re.compile(r"^[0-9a-f]{64}$")

def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError(reason)

def run(command: list[str], timeout: int = 30) -> str:
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                            timeout=timeout, check=True)
    return result.stdout

def check_source() -> dict:
    preset = (ROOT / "export_presets.cfg").read_text(encoding="utf-8")
    contract = json.loads((ROOT / "doctrine/androidCandidate.json").read_text(encoding="utf-8"))
    tablet = json.loads((ROOT / "doctrine/smX400RootedAndroid16TargetV1.json").read_text(encoding="utf-8"))
    checks = (
        ('package/unique_name="' + PACKAGE + '"', "test package"),
        ("architectures/arm64-v8a=true", "ARM64 ABI"),
        ("gradle_build/target_sdk=\"36\"", "target SDK 36"),
        ("screen/support_large=true", "tablet layout"),
        ("screen/support_xlarge=true", "XL tablet layout"),
        ("permissions/internet=false", "offline proof scope"),
    )
    for token, meaning in checks:
        require(token in preset, "source Android preset drift: " + meaning)
    require(contract.get("package") == PACKAGE, "Android package contract drift")
    require(contract.get("targetSdk") == 36, "Android target SDK contract drift")
    require(tablet.get("target", {}).get("model") == MODEL, "Samsung tablet target drift")
    return {"status": "PASS", "model": MODEL, "expectedAndroidSdk": 36,
            "expectedAbi": "arm64-v8a", "package": PACKAGE, "rootRequired": False}

def exact_source(value: str) -> str:
    require(SOURCE.fullmatch(value) is not None, "require exact 40-character lowercase source SHA")
    actual = run(["git", "rev-parse", "HEAD"]).strip()
    require(value == actual, "source checkout does not match source SHA")
    return actual

def verify_apk(path: Path, expected: str) -> dict:
    require(path.is_file(), "APK file missing")
    require(DIGEST.fullmatch(expected) is not None, "require exact lowercase 64-character APK SHA-256")
    h = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(1024 * 1024):
            h.update(block)
    require(h.hexdigest() == expected, "APK SHA-256 mismatch")
    with zipfile.ZipFile(path) as package:
        require(package.testzip() is None, "APK archive CRC failure")
        require("AndroidManifest.xml" in package.namelist(), "APK missing Android manifest")
        require(any(name.startswith("lib/arm64-v8a/") and name.endswith(".so")
                    for name in package.namelist()), "APK has no ARM64 native library")
    badging = run(["aapt", "dump", "badging", str(path.resolve())])
    require("package: name='" + PACKAGE + "'" in badging, "APK package mismatch")
    require("targetSdkVersion:'36'" in badging, "APK target SDK mismatch")
    require("native-code: 'arm64-v8a'" in badging, "APK native ABI mismatch")
    require("application-debuggable" in badging, "expected build-only debug preview")
    require(re.search(r"(?m)^uses-permission", badging) is None,
            "unexpected permission in offline preview")
    signature = run(["apksigner", "verify", "--verbose", "--print-certs", str(path.resolve())])
    cert = re.search(r"Signer #1 certificate SHA-256 digest: ([0-9a-fA-F]{64})", signature)
    require(cert is not None, "APK signing certificate not observed")
    return {"apkSha256": h.hexdigest(), "signerSha256": cert.group(1).lower(),
            "status": "PASS_DEBUG_SIGNED_ONLY", "canGuaranteeFutureUpdate": False}

def adb_identity() -> dict:
    output = run(["adb", "devices"])
    authorized = [line.split()[0] for line in output.splitlines()[1:]
                  if len(line.split()) == 2 and line.split()[1] == "device"]
    require(len(authorized) == 1, "exactly one authorized ADB device required")
    def prop(key: str) -> str:
        return run(["adb", "-s", authorized[0], "shell", "getprop", key]).strip()
    model = prop("ro.product.model")
    sdk = prop("ro.build.version.sdk")
    abis = prop("ro.product.cpu.abilist").split(",")
    require(model == MODEL, "wrong Samsung model: " + model)
    require(sdk == "36", "tablet must report Android 16 / API 36")
    require("arm64-v8a" in abis, "tablet does not advertise ARM64")
    return {"serialObserved": True, "model": model, "androidSdk": int(sdk),
            "abis": abis, "rootUsed": False}

def install(apk: Path, source: str, digest: str) -> dict:
    src = exact_source(source)
    check_source()
    signed = verify_apk(apk, digest)
    identity = adb_identity()
    # -r preserves app data when Android allows same-signing-key replacement;
    # a signer mismatch is an explicit error, never auto-uninstall/clear.
    run(["adb", "install", "-r", "-t", str(apk.resolve())], timeout=160)
    from_capture = ROOT / "tools/captureAndroidProof.py"
    import importlib.util
    spec = importlib.util.spec_from_file_location("luhm_android_proof", from_capture)
    require(spec is not None and spec.loader is not None, "APK evidence collector missing")
    collector = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(collector)
    observed = collector.capture(src, digest, request_launch=True)
    require(observed.get("exactInstalledArtifactMatched") is True,
            "installed APK does not match downloaded artifact")
    return {"sourceRef": src, "tablet": identity, "apk": signed,
            "installedArtifactMatched": True,
            "launchCommandAccepted": observed.get("launchCommandAccepted") is True,
            "onscreenProof": False, "touchProof": False, "stableBetaSigner": False,
            "status": "AMBER_INSTALLED_DEBUG_PREVIEW_SCREEN_PENDING"}

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-ref")
    parser.add_argument("--apk", type=Path)
    parser.add_argument("--expected-sha256")
    parser.add_argument("--tablet", action="store_true", help="read-only ADB model/SDK/ABI probe")
    parser.add_argument("--install", action="store_true", help="opt-in verified APK install and launch")
    parser.add_argument("--output", default="build/samsung-lite-beta/receipt.json")
    args = parser.parse_args()
    if args.install and (not args.apk or not args.source_ref or not args.expected_sha256):
        parser.error("install requires --apk, --source-ref, --expected-sha256")
    if args.apk and not args.expected_sha256:
        parser.error("APK requires --expected-sha256")
    try:
        receipt = {"schema": "luhmOs.samsungLiteBetaPreflight.v1",
                   "source": check_source(), "status": "GREEN_SOURCE_SCOPE_ONLY",
                   "fullPublicReleaseProven": False, "crownStatus": "STOP"}
        if args.source_ref:
            receipt["sourceRef"] = exact_source(args.source_ref)
        if args.apk:
            receipt["apk"] = verify_apk(args.apk, args.expected_sha256)
            receipt["status"] = "AMBER_DEBUG_BINARY_DEVICE_PENDING"
        if args.tablet and not args.install:
            receipt["tablet"] = adb_identity()
            receipt["status"] = "AMBER_TABLET_IDENTIFIED_INSTALL_PENDING"
        if args.install:
            receipt["install"] = install(args.apk, args.source_ref, args.expected_sha256)
            receipt["status"] = receipt["install"]["status"]
    except (ValueError, OSError, subprocess.SubprocessError, zipfile.BadZipFile) as exc:
        print("RED_SAMSUNG_LITE_BETA=" + str(exc), file=sys.stderr)
        return 2
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

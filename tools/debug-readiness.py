#!/usr/bin/env python3
"""One-command LuHm source/debug readiness; evidence, not a release claim."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXACT_SOURCE = re.compile(r"^[0-9a-f]{40}$")
EXACT_APK = re.compile(r"^[0-9a-f]{64}$")
CHECKS = (
    ("godot-android-source", (sys.executable, "tools/candidateGate.py")),
    ("android-webview-boundary", (sys.executable, "tools/androidWeb3CockpitAudit.py")),
    ("android-delivery-lanes", (sys.executable, "tools/androidDeliveryLanesAudit.py", "--self-test")),
    ("cross-layer-release-boundary", (sys.executable, "tools/finalGoalHardeningAudit.py", "--self-test")),
    ("device-collector-negative-tests", (sys.executable, "tools/captureAndroidProof.py", "--self-test")),
    ("plugin-first-install", (sys.executable, "tools/manualPluginVirginInstallAudit.py")),
    ("vendor-debug-boundary", (sys.executable, "tools/vendorAiDebugAudit.py")),
    ("godot-smoke-parser-tests", (sys.executable, "tests/testSmokeRunner.py")),
    ("jquery-cockpit-contract", ("node", "frontEnd/tools/check.mjs")),
)

def require_exact_source(value: str) -> str:
    if not EXACT_SOURCE.fullmatch(value):
        raise ValueError("a full lowercase 40-character source commit SHA is required")
    return value

def require_exact_apk(value: str) -> str:
    if not EXACT_APK.fullmatch(value):
        raise ValueError("a full lowercase 64-character APK SHA-256 is required")
    return value

def observed_head() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True,
        text=True, capture_output=True, timeout=10,
    )
    return require_exact_source(result.stdout.strip())

def failure_kind(output: str, returncode: int) -> str:
    if returncode == 0:
        return "none"
    if "Traceback (most recent call last)" in output:
        return "python-exception"
    if "AssertionError" in output:
        return "assertion-failure"
    if "SyntaxError" in output or "Parse Error:" in output:
        return "parse-failure"
    if "No such file or directory" in output or "not found" in output.lower():
        return "missing-dependency-or-file"
    return "audit-rejected"

def run_check(name: str, command: tuple[str, ...], timeout: int = 120) -> dict:
    started = time.monotonic()
    try:
        proc = subprocess.run(
            command, cwd=ROOT, text=True, capture_output=True, timeout=timeout,
            check=False,
        )
        combined = proc.stdout + "\n" + proc.stderr
        return {
            "id": name,
            "status": "PASS" if proc.returncode == 0 else "FAIL",
            "exitCode": proc.returncode,
            "failureKind": failure_kind(combined, proc.returncode),
            "outputSha256": hashlib.sha256(combined.encode("utf-8")).hexdigest(),
            "elapsedSeconds": round(time.monotonic() - started, 2),
        }
    except subprocess.TimeoutExpired:
        return {"id": name, "status": "FAIL", "failureKind": "timeout",
                "elapsedSeconds": round(time.monotonic() - started, 2)}
    except FileNotFoundError:
        return {"id": name, "status": "FAIL", "failureKind": "missing-executable",
                "elapsedSeconds": round(time.monotonic() - started, 2)}

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-ref", help="expected full exact checkout SHA")
    parser.add_argument("--device", action="store_true", help="observe one authorized Samsung through ADB")
    parser.add_argument("--expected-apk-sha", help="exact SHA-256 from the same CI debug APK")
    parser.add_argument("--launch", action="store_true", help="request launch only after installed APK matches")
    parser.add_argument("--output", default="build/debug-readiness/receipt.json")
    args = parser.parse_args()

    if args.launch and not args.device:
        parser.error("--launch requires --device")
    if args.device and (not args.source_ref or not args.expected_apk_sha):
        parser.error("--device requires --source-ref and --expected-apk-sha")
    if args.expected_apk_sha and not args.device:
        parser.error("--expected-apk-sha requires --device")

    try:
        head = observed_head()
        expected = require_exact_source(args.source_ref) if args.source_ref else head
        if expected != head:
            raise ValueError("source checkout does not match requested exact commit")
        if args.device:
            require_exact_apk(args.expected_apk_sha)
    except (ValueError, subprocess.SubprocessError, OSError) as exc:
        parser.error(str(exc))

    results = [run_check(name, command) for name, command in CHECKS]
    source_ready = all(row["status"] == "PASS" for row in results)
    device = {"status": "PENDING_PHYSICAL_INSTALL", "artifactMatched": False,
              "screenProven": False, "touchProven": False}
    if args.device:
        device_path = Path(args.output).parent / "device-proof.json"
        command = [
            sys.executable, "tools/captureAndroidProof.py", "--capture",
            "--source-ref", head, "--expected-sha256", args.expected_apk_sha,
            "--output", str(device_path),
        ]
        if args.launch:
            command.append("--launch")
        check = run_check("exact-samsung-artifact", tuple(command))
        results.append(check)
        if device_path.exists():
            receipt = json.loads(device_path.read_text(encoding="utf-8"))
            device = {
                "status": receipt.get("status", "RED_DEVICE_PROOF"),
                "artifactMatched": receipt.get("exactInstalledArtifactMatched") is True,
                "screenProven": False,
                "touchProven": False,
                "launchCommandAccepted": receipt.get("launchCommandAccepted") is True,
            }
        else:
            device["status"] = "RED_DEVICE_PROOF_NOT_COLLECTED"

    failed = [row["id"] for row in results if row["status"] != "PASS"]
    receipt = {
        "schema": "luhmOs.debugReadiness.v1",
        "sourceRef": head,
        "status": ("RED_DEBUG_READINESS" if failed else
                   "AMBER_SOURCE_READY_DEVICE_PENDING" if not args.device else
                   "AMBER_DEVICE_ARTIFACT_MATCHED_SCREEN_PENDING"),
        "sourceChecksPassed": source_ready,
        "failedChecks": failed,
        "checks": results,
        "device": device,
        "productionSignerProven": False,
        "publicReleaseProven": False,
        "chatGptHostInvocationProven": False,
        "crownStatus": "STOP",
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    temp = output.with_suffix(output.suffix + ".tmp")
    temp.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    temp.replace(output)
    print(json.dumps(receipt, indent=2))
    return 2 if failed else 0

if __name__ == "__main__":
    raise SystemExit(main())

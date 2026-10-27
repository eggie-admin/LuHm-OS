#!/usr/bin/env python3
"""Opt-in, read-only ADB inventory for KAI9000 Samsung graphics compatibility.

Without --probe, prints the plan only. Never executes shell writes, flashes,
installs, reads accounts/files/serial numbers, contacts servers, or changes a
driver. Output includes no raw build fingerprint or device identifiers.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from typing import Callable

PROPERTIES = (
    "ro.product.model",
    "ro.product.device",
    "ro.build.version.release",
    "ro.build.version.sdk",
    "ro.hardware",
    "ro.soc.model",
    "ro.board.platform",
    "ro.opengles.version",
    "ro.build.fingerprint",
)
ALLOWED = tuple(("shell", "getprop", key) for key in PROPERTIES) + (
    ("shell", "pm", "list", "features"),
    ("shell", "dumpsys", "webviewupdate"),
)
MAX_OUTPUT_CHARS = 30000


def run_command(parts: tuple[str, ...]) -> str:
    if parts not in ALLOWED:
        raise ValueError("RED_ADB_COMMAND_OUTSIDE_READ_ONLY_ALLOWLIST")
    try:
        result = subprocess.run(
            ["adb", *parts], capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=8, check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise RuntimeError("RED_ADB_READ_FAILED") from exc
    if result.returncode != 0:
        raise RuntimeError("RED_ADB_COMMAND_UNAVAILABLE")
    return result.stdout[:MAX_OUTPUT_CHARS].strip()


def _safe_value(value: str) -> str:
    # Only a small set of human-readable hardware model/token characters.
    return re.sub(r"[^A-Za-z0-9 ._+()/:-]", "", value)[:100]


def collect(run: Callable[[tuple[str, ...]], str] = run_command) -> dict:
    result: dict = {
        "schema": "luhmOs.kai9000GraphicsInventory.v1",
        "action": "READ_ONLY_ADB",
        "probeResult": "DIAGNOSTIC_NOT_DRIVER_APPROVAL",
        "driverModified": False,
        "buildOrInstallPerformed": False,
        "fingerprintHashOnly": True,
        "properties": {},
        "declaredGraphicsFeatures": [],
        "webViewProvider": "NOT_DETECTED",
        "limitations": [
            "System property values are hints, not a GPU capability or driver-quality benchmark",
            "No native GLES/Vulkan renderer strings queried",
            "Perfetto/Android Performance Analyzer profiling requires a separate opt-in run",
            "Secure Folder app-install and Samsung DeX presentation not tested",
        ],
    }
    for prop in PROPERTIES:
        raw = run(("shell", "getprop", prop))
        if prop == "ro.build.fingerprint":
            result["properties"]["buildFingerprintSha256"] = hashlib.sha256(raw.encode("utf-8")).hexdigest() if raw else "NOT_AVAILABLE"
        else:
            result["properties"][prop] = _safe_value(raw) if raw else "NOT_AVAILABLE"
    features = run(("shell", "pm", "list", "features"))
    result["declaredGraphicsFeatures"] = sorted(set(
        line.strip()[:160]
        for line in features.splitlines()
        if re.fullmatch(r"feature:android\.hardware\.(?:vulkan\.[A-Za-z0-9._]+|opengles\.[A-Za-z0-9._]+)", line.strip())
    ))[:40]
    webview = run(("shell", "dumpsys", "webviewupdate"))
    for line in webview.splitlines():
        if "Current WebView package" in line:
            # The complete dumpsys output is not preserved.
            provider = line.split(":", 1)[-1].strip()
            result["webViewProvider"] = _safe_value(provider) or "NOT_DETECTED"
            break
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="LuHm KAI9000 zero-mutation graphics inventory")
    parser.add_argument("--probe", action="store_true", help="Opt in to whitelisted ADB reads on a connected device")
    args = parser.parse_args()
    if not args.probe:
        print(json.dumps({
            "schema": "luhmOs.kai9000GraphicsInventory.v1",
            "probeResult": "NOT_RUN",
            "adbAccess": "REQUIRES_EXPLICIT_--probe",
            "allowedReads": ["getprop selected graphics/build keys", "pm list features", "dumpsys webviewupdate"],
            "noDriverChange": True, "noFirmwareChange": True, "noNetworkCalls": True,
        }, sort_keys=True, indent=2))
        return 0
    try:
        report = collect()
    except (RuntimeError, ValueError) as exc:
        print(json.dumps({"probeResult": str(exc), "deviceModified": False}))
        return 2
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

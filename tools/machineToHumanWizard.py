#!/usr/bin/env python3
"""LuHm-OS read-only machine-to-human wizard; never modifies a disk or Android system."""
from __future__ import annotations
import argparse
import json
import os
import platform
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "doctrine/machineToHumanWizardV1.json"

def _safeCommand(args: list[str], timeout: int = 3) -> str | None:
    """Only fixed, allowlisted read-only probes; no shell or user arguments."""
    allowed = {"getprop", "lsblk"}
    if not args or args[0] not in allowed:
        raise ValueError("Non-read-only command prohibited")
    if args[0] == "getprop":
        keys = {
            "ro.product.model", "ro.product.cpu.abi", "ro.board.platform",
            "ro.build.version.sdk", "ro.boot.verifiedbootstate", "ro.boot.flash.locked"
        }
        if len(args) != 2 or args[1] not in keys:
            raise ValueError("Unsupported Android property probe")
    if args[0] == "lsblk" and args != ["lsblk", "--json", "-o", "NAME,SIZE,TYPE,RO"]:
        raise ValueError("Only redacted block inventory permitted")
    if not shutil.which(args[0]):
        return None
    try:
        run = subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=False)
        return run.stdout.strip()[:16384] if run.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None

def observe(includeDisks: bool = False) -> dict:
    android = bool(os.environ.get("ANDROID_ROOT")) or Path("/system/build.prop").exists()
    props = {}
    if android:
        for key, name in [
            ("ro.product.model","model"), ("ro.product.cpu.abi","abi"),
            ("ro.board.platform","board"),("ro.build.version.sdk","sdk"),
            ("ro.boot.verifiedbootstate","verifiedBoot"),
            ("ro.boot.flash.locked","bootloaderLocked")
        ]:
            props[name] = _safeCommand(["getprop", key]) or None
    system = platform.system()
    result = {
        "system": "Android" if android else system,
        "machine": platform.machine(),
        "kernel": platform.release(),
        "cpuCount": os.cpu_count(),
        "pageSize": os.sysconf("SC_PAGE_SIZE") if hasattr(os,"sysconf") else None,
        "vendor": props, "diskInventory": None
    }
    if includeDisks and not android and system == "Linux":
        raw = _safeCommand(["lsblk", "--json", "-o", "NAME,SIZE,TYPE,RO"])
        if raw:
            try:
                result["diskInventory"] = json.loads(raw).get("blockdevices",[])
            except json.JSONDecodeError:
                result["diskInventory"] = None
    return result

def evaluate(facts: dict, *, synthetic: bool = False) -> dict:
    config = json.loads(CONTRACT.read_text(encoding="utf-8"))
    system = facts.get("system")
    vendor = facts.get("vendor") or {}
    model = str(vendor.get("model") or "")
    if system == "Android":
        profile = "androidSamsung" if model.upper().startswith(("SM-", "SAMSUNG")) else "androidGeneric"
    elif system == "Linux":
        profile = "linuxHost"
    elif system == "Windows":
        profile = "windowsHost"
    elif system == "Darwin":
        profile = "macHost"
    else:
        profile = "unknownHost"
    hostSupported = profile in config["hostProfiles"]
    boot = vendor.get("verifiedBoot") if system == "Android" else None
    locked = vendor.get("bootloaderLocked") if system == "Android" else None
    propsUnverified = bool(system == "Android" and (boot is None or locked is None))
    if profile == "androidSamsung":
        nextAction = "Preserve Samsung Android/Knox; use userland apps and signed APK delivery"
    elif profile == "androidGeneric":
        nextAction = "Preserve vendor Android/AVB; use userland and verify device-specific capability"
    elif profile == "linuxHost":
        nextAction = "Inventory distro packages before choosing headless or creative-studio profile"
    elif profile == "windowsHost":
        nextAction = "Use verified Windows host inventory; Rufus only as a separate approved USB recovery task"
    elif profile == "macHost":
        nextAction = "Verify Apple platform and signing capabilities before macOS app packaging"
    else:
        nextAction = "Unknown host; collect nonprivileged hardware facts first"
    return {
        "schema":"luhmOs.machineToHumanWizardReceipt.v1",
        "identity":"LuHm-OS: Project Premonition",
        "sourceOnly":True,"physicalDeviceVerified":False,
        "syntheticFixture":synthetic,
        "hostProfile":profile,"hostSupported":hostSupported,
        "phases":[x["id"] for x in config["phases"]],
        "hardwareFacts":facts,
        "bootProtectionUndetermined":propsUnverified,
        "gpartedEligibleHost":profile == "linuxHost",
        "rufusEligibleHost":profile == "windowsHost",
        "diskWritesPerformed":False,"bootloaderChanged":False,
        "packagesInstalled":False,"networkListenerStarted":False,
        "nextAction":nextAction,
        "escalation":"NO_AUTOMATIC_ESCALATION",
        "crownStatus":"STOP"
    }

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture",type=Path,default=None,
                        help="Read a synthetic JSON hardware fixture (NOT actual-device proof)")
    parser.add_argument("--include-disks",action="store_true",
                        help="Read-only lsblk inventory on Linux hosts, excluding serial/UUID")
    parser.add_argument("--json",action="store_true",help="Print JSON receipt")
    args=parser.parse_args()
    if args.fixture is not None:
        facts=json.loads(args.fixture.read_text(encoding="utf-8"))
        if not isinstance(facts,dict):
            parser.error("Fixture must be a JSON object")
    else:
        facts=observe(args.include_disks)
    receipt=evaluate(facts,synthetic=args.fixture is not None)
    print(json.dumps(receipt,indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())

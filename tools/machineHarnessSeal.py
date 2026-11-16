#!/usr/bin/env python3
"""LuHm machine harness: source-bound, minimal, privacy-redacted inventory only."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "doctrine/machineHarnessSealV1.json"
SHA40 = re.compile(r"[0-9a-f]{40}\Z")
ALLOWED_FACTS = {"system", "boardModel", "machine", "androidBrand", "networkInterfaces", "bluetoothPresent"}
ALLOWED_ANDROID = {"samsung", "pixel", "unknown", None}
PROFILE_NAMES = {"picoW", "piZeroW", "piZero2W", "pi3ModelB", "androidSamsung", "androidPixel"}


def source_ref():
    raw = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, timeout=10, text=True).strip()
    if not SHA40.fullmatch(raw):
        raise ValueError("RED_SOURCE_REF")
    return raw


def observed_facts():
    """No identifiers, MAC addresses, serial numbers, disks, keys, or network changes."""
    model_path = Path("/proc/device-tree/model")
    model = ""
    if model_path.is_file():
        model = model_path.read_bytes()[:256].decode("utf-8", "replace").strip("\x00").strip()
    net = Path("/sys/class/net")
    interfaces = sorted(p.name for p in net.iterdir()) if net.is_dir() else []
    # Exclude arbitrary interface names; keep only safe capability classes.
    classes = sorted(set(x for n in interfaces for x in
        (["usb"] if re.fullmatch(r"usb[0-9]{1,2}", n) else []) +
        (["ethernetUsbCandidate"] if re.fullmatch(r"enx[0-9a-fA-F]{12}", n) else [])))
    bluetooth = Path("/sys/class/bluetooth")
    return {"system": platform.system(), "boardModel": model[:128],
            "machine": platform.machine()[:48], "androidBrand": "unknown",
            "networkInterfaces": classes,
            "bluetoothPresent": bool(bluetooth.is_dir() and any(bluetooth.iterdir()))}


def profile_for(facts):
    os_name = facts["system"]
    name = facts["boardModel"].lower()
    if os_name == "Android":
        return {"samsung": "androidSamsung", "pixel": "androidPixel"}.get(facts["androidBrand"])
    if "pico" in name and ("rp2040" in name or "rp2350" in name or "pico" in name):
        return "picoW"  # Pico family needs exact Pico/Pico 2 marking before firmware choice
    if "raspberry pi zero 2 w" in name:
        return "piZero2W"
    if "raspberry pi zero w" in name:
        return "piZeroW"
    if "raspberry pi 3 model b" in name:
        return "pi3ModelB"
    return None


def evaluate(facts, exact_source, fixture=False):
    if type(facts) is not dict or set(facts) != ALLOWED_FACTS:
        raise ValueError("RED_UNEXPECTED_HARDWARE_FIELD")
    if any(type(facts[k]) is not str or len(facts[k]) > 128
           for k in ("system", "boardModel", "machine")):
        raise ValueError("RED_HARDWARE_STRING")
    if facts["androidBrand"] not in ALLOWED_ANDROID:
        raise ValueError("RED_ANDROID_BRAND")
    if type(facts["bluetoothPresent"]) is not bool or type(facts["networkInterfaces"]) is not list:
        raise ValueError("RED_INTERFACE_TYPES")
    if len(facts["networkInterfaces"]) > 8 or any(i not in ("usb", "ethernetUsbCandidate") for i in facts["networkInterfaces"]):
        raise ValueError("RED_INTERFACE_IDENTIFIER_OR_COUNT")
    if not SHA40.fullmatch(exact_source):
        raise ValueError("RED_SOURCE_REF")
    policy = json.loads(POLICY.read_text(encoding="utf8"))
    if policy["crownStatus"] != "STOP" or any(policy["authority"].values()):
        raise ValueError("RED_MACHINE_AUTHORITY_DRIFT")
    selected = profile_for(facts)
    if selected is not None and selected not in PROFILE_NAMES:
        raise ValueError("RED_UNKNOWN_PROFILE")
    linux = selected in {"piZeroW", "piZero2W", "pi3ModelB"}
    gadget = selected in {"piZeroW", "piZero2W"}
    pi3 = selected == "pi3ModelB"
    return {
        "schema": "luhmOs.machineHarnessReceipt.v1",
        "sourceRef": exact_source,
        "status": "AMBER_DEVICE_PROOF_REQUIRED",
        "profileId": selected or "unresolvedHardware",
        "humanRole": policy["profiles"].get(selected, {}).get("role", "inventoryExactBoardMarking"),
        "fourPhases": policy["phases"],
        "hostLinuxCandidate": linux,
        "usbGadgetCandidate": gadget,
        "usbHostCandidate": pi3 or gadget,
        "usbHostAndGadgetSimultaneous": False if gadget else None,
        "usbInterfaceHintObserved": bool(facts["networkInterfaces"]),
        "bluetoothAdapterHintObserved": facts["bluetoothPresent"],
        "preferredTransport": "USB_FIRST_CONDITIONAL",
        "fallbackTransport": "BLUETOOTH_THEN_PRIVATE_WIFI",
        "displayPort": "DSI_DISPLAY_REQUIRES_VERIFICATION" if pi3 else
                       "CSI_CAMERA_NOT_DSI_DISPLAY" if gadget else "UNKNOWN_CONTROLLER",
        "ribbonDisplayVerified": False,
        "slimlineSataPowerVerified": False,
        "vendorFirmwareVerified": False,
        "physicalDeviceVerified": False,
        "syntheticFixture": bool(fixture),
        "commandsExecuted": ["git rev-parse HEAD"] if not fixture else [],
        "diskWrites": False,
        "bootChanges": False,
        "firmwareFlashes": False,
        "networkChanges": False,
        "agentWorkersActivated": False,
        "nextAction": "READ_BOARD_MARKING_RIBBON_CONTROLLER_AND_USB_ROLE" if selected is None
                      else "VERIFY_CABLE_AND_CONTROLLER_ON_OWNER_HARDWARE",
        "crownStatus": "STOP"
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--fixture", type=Path)
    p.add_argument("--source-ref", required=True)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    current = source_ref()
    if args.source_ref != current:
        raise ValueError("RED_EXACT_SOURCE_REF_MISMATCH")
    facts = json.loads(args.fixture.read_text(encoding="utf8")) if args.fixture else observed_facts()
    receipt = evaluate(facts, current, fixture=bool(args.fixture))
    if args.output:
        out = args.output.resolve()
        if out == ROOT or ROOT in out.parents:
            raise ValueError("RED_OUTPUT_INSIDE_SOURCE_REPOSITORY")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(receipt, indent=2, sort_keys=True)+"\n", encoding="utf8")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()

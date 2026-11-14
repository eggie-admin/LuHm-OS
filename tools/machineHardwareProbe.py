#!/usr/bin/env python3
"""Read-only capability snapshot: no device access, no firmware reads, no serials."""
from __future__ import annotations
import json
import platform
import shutil

CAPABILITIES={
    "gpuNvidia":"nvidia-smi",
    "gpuVulkan":"vulkaninfo",
    "usbEnumerationTool":"lsusb",
    "pciEnumerationTool":"lspci",
    "udevRules":"udevadm",
    "secureBootInspection":"mokutil",
    "firmwareUpdateTool":"fwupdmgr",
    "cameraPtp":"gphoto2",
    "scanner":"scanimage",
    "printer":"lpstat",
    "wacomX11":"xsetwacom",
    "monitorX11":"xrandr",
    "blender":"blender",
    "godot":"godot",
    "git":"git",
}
def snapshot(which=shutil.which,system=platform.system,machine=platform.machine):
    available={name:bool(which(command)) for name,command in CAPABILITIES.items()}
    return {
      "schema":"luhmOs.hardwareCapabilityProbe.v1",
      "product":"LuHm-OS",
      "hostOsFamily":system(),
      "architecture":machine(),
      "toolAvailabilityOnly":available,
      "deviceIdsRecorded":False,
      "serialNumbersRecorded":False,
      "macAddressesRecorded":False,
      "hardwareFirmwareRead":False,
      "firmwareFlashed":False,
      "kernelModified":False,
      "deviceConnectedProof":False,
      "graphicsRuntimeProof":False,
      "driverCompatibleProof":False,
      "status":"TOOL_DISCOVERY_ONLY",
      "crown":"STOP"
    }
if __name__=="__main__":
    print(json.dumps(snapshot(),indent=2,sort_keys=True))

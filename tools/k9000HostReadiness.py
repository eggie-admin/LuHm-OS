#!/usr/bin/env python3
"""K9000 Linux studio kernel/developer baseline inspector. Never mutates devices."""
import json
import os
import platform
import shutil
import subprocess
from pathlib import Path

PACKAGES = ("python3","git","java","gradle","adb","godot","node","npm",
            "ffmpeg","blender","gimp","gparted","parted","lsblk","xrandr",
            "scanimage","sane-find-scanner","v4l2-ctl","sha256sum")
SYSCTL_KEYS = ("kernel/kptr_restrict","kernel/dmesg_restrict","kernel/yama/ptrace_scope",
               "fs/protected_hardlinks","fs/protected_symlinks","kernel/unprivileged_bpf_disabled")

def inspect() -> dict:
    linux = platform.system() == "Linux"
    controls = {}
    if linux:
        for key in SYSCTL_KEYS:
            path = Path("/proc/sys") / key
            try:
                value = path.read_text(encoding="utf-8").strip()
                controls[key.replace("/",".")] = value if value.isdigit() and len(value) <= 4 else "UNKNOWN"
            except OSError:
                controls[key.replace("/",".")] = "UNKNOWN"
    tools = {name:bool(shutil.which(name)) for name in PACKAGES}
    monitors = "UNVERIFIED"
    if linux and tools["xrandr"] and os.environ.get("DISPLAY"):
        try:
            result = subprocess.run(["xrandr","--listmonitors"],capture_output=True,text=True,
                                    timeout=3,check=False)
            first = (result.stdout or "").splitlines()[0] if result.stdout else ""
            if result.returncode == 0 and first.startswith("Monitors: "):
                suffix = first.removeprefix("Monitors: ").strip()
                monitors = int(suffix) if suffix.isdigit() else "UNVERIFIED"
        except (OSError,subprocess.TimeoutExpired):
            pass
    return {
        "schema":"luhmOs.k9000HostReadiness.v1",
        "system":platform.system(),
        "kernelRelease":platform.release(),
        "kernelSecuritySettings":controls,
        "toolPresence":tools,
        "reportedMonitorCount":monitors,
        "gpartedRole":"operatorOnly",
        "partitionChangesMade":False,
        "kernelChanged":False,
        "softwareInstalled":False,
        "physicalDeviceValidated":False,
        "sourceOnly":False,
        "warning":"Tool presence does not prove versions, licenses, GPU, scanner drivers or kernel hardening."
    }

if __name__ == "__main__":
    print(json.dumps(inspect(),indent=2))

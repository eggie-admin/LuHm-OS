#!/usr/bin/env python3
"""Nonprivileged Linux device discovery for the real studio host.

Outputs only command presence and counts, never serials, MACs or recordings.
Enumerating a device does not mean its audio, camera or scanner works.
"""
import argparse
import json
import platform
import shutil
import subprocess
from pathlib import Path

COMMANDS={
 "usbBus":["lsusb"],
 "audioCapture":["arecord","-l"],
 "pipewire":["wpctl","status"],
 "bluetooth":["bluetoothctl","devices"],
 "uvcCamera":["v4l2-ctl","--list-devices"],
 "scanner":["scanimage","-L"]
}

def run_probe(execute=False):
    linux=platform.system()=="Linux"
    checks={}
    for name,command in COMMANDS.items():
        binary=shutil.which(command[0])
        entry={"toolPresent":bool(binary),"enumeration":"NOT_RUN",
               "deviceOperational":"UNVERIFIED","deviceCount":None}
        if execute and linux and binary:
            try:
                p=subprocess.run([binary,*command[1:]],capture_output=True,text=True,
                                 timeout=5,check=False)
                entry["enumeration"]="COMMAND_SUCCEEDED" if p.returncode==0 else "COMMAND_UNAVAILABLE"
                # No raw output is persisted or returned; a successful command is not a functioning device.
            except (OSError,subprocess.TimeoutExpired):
                entry["enumeration"]="TIMEOUT_OR_OS_ERROR"
        checks[name]=entry
    modules={}
    if linux:
        try:
            text=Path("/proc/modules").read_text(encoding="utf-8")
            loaded={line.split()[0] for line in text.splitlines() if line.split()}
            for module in ("snd_usb_audio","uvcvideo","btusb"):
                modules[module]="PRESENT" if module in loaded else "NOT_OBSERVED"
        except OSError:
            modules={module:"UNAVAILABLE" for module in ("snd_usb_audio","uvcvideo","btusb")}
    return {"schema":"luhmOs.k9000LocalDriverProbe.v1","system":platform.system(),
            "hostOnly":True,"executed":bool(execute and linux),
            "tools":checks,"kernelModules":modules,"driversWorking":"NOT_PROVEN",
            "privacy":"NO_RAW_HARDWARE_IDENTIFIERS","mutations":False}

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inspect",action="store_true",help="run available read-only local inventory commands")
    args=parser.parse_args()
    print(json.dumps(run_probe(args.inspect),indent=2))

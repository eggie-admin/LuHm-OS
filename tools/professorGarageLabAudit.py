#!/usr/bin/env python3
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
errors=[]
def need(ok,msg):
    if not ok: errors.append(msg)
d=json.loads((root/"doctrine/professorGarageLabV1.json").read_text())
h=(root/"hardware/professorGarageLab.yaml").read_text()
p=(root/"tools/hardware/probeProfessorGarageLab.sh").read_text()
need(d.get("schema")=="luhmOs.professorGarageLab.v1","schema drift")
need(d.get("lane")=="privateResearchDevelopment","garage lab must stay private R&D")
need(d.get("workspace",{}).get("canonicalCodingWorkspace")=="GitHub Forge","GitHub Forge workspace drift")
need(d.get("workspace",{}).get("codespacesMayProvePhysicalHardware") is False,"Codespaces physical-proof leak")
need(d.get("ubuntuCore",{}).get("customKernelBeforeInventory") is False,"kernel-before-inventory drift")
need(d.get("samsungCore",{}).get("genericUbuntuKernelMayReplaceSamsungVendorKernel") is False,"Samsung vendor boundary leak")
scanner=d.get("studioHardware",{}).get("scanner",{})
need(scanner.get("vendor")=="Epson" and scanner.get("model")=="Perfection V39 II","scanner identity drift")
need(scanner.get("exactUsbVidPid")=="VERIFY_FROM_PHYSICAL_PROBE","scanner USB identity overclaim")
need("SM-X400" in h,"SM-X400 target missing")
need("UNKNOWN stays UNKNOWN" in h,"hardware inventory truth law missing")
for token in ("uname -a","lsusb","vulkaninfo --summary","v4l2-ctl --list-devices","sane-find-scanner","scanimage -L","termux-camera-info","termux-usb -l"):
    need(token in p,f"probe missing {token}")
need(d.get("promotion") is False and d.get("crownStatus")=="STOP","candidate authority drift")
print(json.dumps({
  "schema":"luhmOs.professorGarageLabAudit.v1",
  "status":"GREEN_SOURCE_CONTRACT" if not errors else "RED_SOURCE_CONTRACT",
  "physicalHardwareProof":False,
  "customKernelBootProof":False,
  "errors":errors
},indent=2))
raise SystemExit(1 if errors else 0)

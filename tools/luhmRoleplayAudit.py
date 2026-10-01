#!/usr/bin/env python3
from __future__ import annotations
import json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXPECTED_MAIN = "f22681b905bd5bc0cf84da5e3d1e865a855b5fc2"
LAW = "AI proposes. Policy authorizes. CI proves. Human promotes."

errors=[]
warnings=[]

def load(rel):
    p=ROOT/rel
    if not p.is_file():
        errors.append(f"missing: {rel}")
        return {}
    try:
        return json.loads(p.read_text())
    except Exception as e:
        errors.append(f"invalid json {rel}: {e}")
        return {}

rp=load("doctrine/CODING_ROLEPLAY_SYSTEM_V3.json")
tw=load("doctrine/TERMUX_OUTSIDE_SECURE_DEV_WORKFLOW_V1.json")

protocol=ROOT/"agents/shared/ONI_PROTOCOL_V2.md"
skill=ROOT/"plugins/luhm-os/skills/luhm-coding-roleplay/SKILL.md"
router=ROOT/"tools/lumTaskRouter.py"
installer=ROOT/"scripts/termux/install-luhm-dev.sh"
control=ROOT/"doctrine/ONI_MESH_CONTROL_PLANE_V2.json"
portable=ROOT/"plugins/luhm-os/skills/luhm-agent-workflow/SKILL.md"

for p in (protocol, skill, router, installer, control, portable):
    if not p.is_file() or p.stat().st_size == 0:
        errors.append(f"missing/empty: {p.relative_to(ROOT)}")

if rp.get("sourceLaw") != LAW or tw.get("sourceLaw") != LAW:
    errors.append("source law drift")
if rp.get("authority") != "Professor" or tw.get("authority") != "Professor":
    errors.append("authority drift")
if rp.get("canonicalBase",{}).get("sourceRef") != EXPECTED_MAIN:
    errors.append("roleplay canonical base drift")
if tw.get("canonicalBase") != EXPECTED_MAIN:
    errors.append("termux workflow canonical base drift")
if rp.get("promotion") is not False or tw.get("promotion") is not False:
    errors.append("unexpected promotion authority")

c=rp.get("constraints",{})
if c.get("maxParallelSupportWorkers") != 3:
    errors.append("support worker limit drift")
if c.get("maxMutableSourceLanesPerCandidate") != 1:
    errors.append("mutable source lane drift")
if c.get("narrativeGrantsAuthority") is not False:
    errors.append("narrative authority creep")

tb=rp.get("termuxBoundary",{})
for k in ("secureFolderAccess","shizukuRequired","rootRequired","providerSecretsInstalled","remoteShellAuthority"):
    if tb.get(k) is not False:
        errors.append(f"termux boundary creep: {k}")

for ref_file in ROOT.glob("agents/*/SKILL.md"):
    text=ref_file.read_text(encoding="utf-8")
    if "agents/shared/ONI_PROTOCOL_V2.md" in text and not protocol.is_file():
        errors.append(f"dangling shared protocol ref in {ref_file.relative_to(ROOT)}")

if portable.is_file() and "agents/shared/ONI_PROTOCOL_V2.md" in portable.read_text(encoding="utf-8") and not protocol.is_file():
    errors.append("portable workflow has dangling shared protocol ref")

status = "GREEN_CODING_ROLEPLAY_CANDIDATE" if not errors else "RED_CODING_ROLEPLAY_CANDIDATE"
report={
  "schema":"luhm-os.coding-roleplay-audit.v1",
  "status":status,
  "canonicalBase":EXPECTED_MAIN,
  "errors":errors,
  "warnings":warnings,
  "promotion":False,
  "publicationAuthority":False,
  "productionSigningAuthority":False,
  "crownStatus":"STOP"
}
print(json.dumps(report, indent=2))
raise SystemExit(1 if errors else 0)

#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCTRINE = ROOT / "doctrine" / "yumeGoddess3dProductionV1.json"
MATRIX = ROOT / "media" / "goddess3d-production-matrix-v1.json"

errors = []

def need(ok, message):
    if not ok:
        errors.append(message)

d = json.loads(DOCTRINE.read_text(encoding="utf-8"))
m = json.loads(MATRIX.read_text(encoding="utf-8"))

need(d.get("schema") == "luhmOs.yumeGoddess3dProduction.v1", "schema drift")
need(d.get("authority") == "Professor", "Professor authority missing")
need(d.get("boss") == "lum", "Lum boss drift")
need(d.get("artDirection") == "yume", "Yume ownership drift")
need(d.get("productionLaw", {}).get("runtimeInterchange") == "glTF 2.0 binary (.glb)", "GLB interchange drift")
need(d.get("productionLaw", {}).get("secondaryMotion", {}).get("engineNativeFirst") == "SpringBoneSimulator3D", "secondary-motion architecture drift")
need(d.get("productionLaw", {}).get("secondaryMotion", {}).get("uncontrolledPhysics") is False, "uncontrolled physics must remain forbidden")
need(d.get("productionLaw", {}).get("topology", {}).get("automaticRetopoIsCandidateOnly") is True, "automatic retopo cannot self-promote")
need(d.get("productionLaw", {}).get("identityFirewall", {}).get("noGenericGothConvergence") is True, "identity firewall missing")
need(d.get("currentTruth", {}).get("lum", {}).get("baseGlbSha256") == "06bdfcc196e147c4cb92c7c5489110a8feb30ee8a8f362fac585802eced33b69", "Lum base GLB hash drift")
need(d.get("currentTruth", {}).get("lum", {}).get("knownRigFacts", {}).get("joints") == 24, "Lum donor joint count drift")
need(d.get("crownStatus") == "STOP", "Crown must remain STOP")
need(d.get("promotion") is False, "candidate must not self-promote")

ids = [x.get("id") for x in m.get("characters", [])]
need(ids == ["lum", "urd", "belldandy", "skuld"], "character work queue drift")
need(m.get("crownStatus") == "STOP", "matrix Crown must remain STOP")

if errors:
    print("YUME_GODDESS_3D_AUDIT=FAIL")
    for e in errors:
        print("ERROR=" + e)
    raise SystemExit(2)

print("YUME_GODDESS_3D_AUDIT=PASS")
print("LUM_3D=PROVEN_CANDIDATE")
print("URD_3D=MISSING_RECONCILED_BODY")
print("BELLDANDY_3D=MISSING_RECONCILED_BODY")
print("SKULD_3D=MISSING_RECONCILED_BODY")
print("CROWN_STATUS=STOP")

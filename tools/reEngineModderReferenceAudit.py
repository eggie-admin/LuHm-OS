#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "media" / "re-engine-nexus-model-reference-registry-v1.json"
DOC = ROOT / "doctrine" / "reEngineModderMutationStudyV1.json"

reg = json.loads(REG.read_text(encoding="utf-8"))
doc = json.loads(DOC.read_text(encoding="utf-8"))
errors = []

def need(ok, message):
    if not ok:
        errors.append(message)

need(reg.get("schema") == "luhmOs.reEngineNexusModelReferenceRegistry.v1", "registry schema drift")
need(reg.get("authority") == "Professor", "Professor authority missing")
need(reg.get("artDirection") == "yume", "Yume owner missing")
need(len(reg.get("nexusSurfaces", [])) == 3, "RE2/RE3/Village surface set drift")
need(len(reg.get("representativeReferenceOnlyMods", [])) >= 8, "reference sample too small")
need(any(x.get("id") == "reFramework" and x.get("license") == "MIT" for x in reg.get("toolSource", [])), "REFramework MIT record missing")
need(any(x.get("id") == "reRsz" and x.get("license") == "MIT" for x in reg.get("toolSource", [])), "RE_RSZ MIT record missing")
need(any(x.get("id") == "reMeshNoesisPlugin" and x.get("lane") == "REFERENCE_ONLY" for x in reg.get("toolSource", [])), "RE MESH plugin quarantine missing")
need(reg.get("rightsFirewall", {}).get("capcomGeometryInRuntime") is False, "Capcom geometry firewall missing")
need(reg.get("rightsFirewall", {}).get("nexusModBinariesAutoDownloaded") is False, "Nexus binary firewall missing")
need(reg.get("crownStatus") == "STOP", "registry Crown must STOP")
need(doc.get("crownStatus") == "STOP", "doctrine Crown must STOP")
need("componentSocketContract" in doc.get("originalRuntimeTargets", []), "component socket target missing")

if errors:
    print("RE_ENGINE_MODDER_REFERENCE_AUDIT=FAIL")
    for error in errors:
        print("ERROR=" + error)
    raise SystemExit(2)

print("RE_ENGINE_MODDER_REFERENCE_AUDIT=PASS")
print("NEXUS_SURFACES=RE2R,RE3R,REVILLAGE")
print("NEXUS_BINARIES=NOT_INGESTED")
print("ORIGINAL_RUNTIME_TARGET=GODOT47")
print("CROWN_STATUS=STOP")

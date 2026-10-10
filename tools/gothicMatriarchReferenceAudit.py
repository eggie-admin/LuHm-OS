#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "media" / "gothic-matriarch-family-reference-study-v1.json"

data = json.loads(PATH.read_text(encoding="utf-8"))
errors = []

def need(ok, message):
    if not ok:
        errors.append(message)

need(data.get("schema") == "luhmOs.gothicMatriarchFamilyReferenceStudy.v1", "schema drift")
need(data.get("status") == "PROTECTED_REFERENCE_ONLY", "protected-reference state drift")
need(data.get("authority") == "Professor", "Professor authority missing")
need(data.get("artDirection") == "yume", "Yume art-direction owner missing")
need(data.get("rightsFirewall", {}).get("capcomCharacterAssetsInRuntime") is False, "Capcom runtime firewall missing")
need(data.get("rightsFirewall", {}).get("fanModelGeometryInRuntime") is False, "fan-model geometry firewall missing")
need(data.get("rightsFirewall", {}).get("directFaceCopy") is False, "face-copy firewall missing")
need(data.get("rightsFirewall", {}).get("highLevelProductionStudyAllowed") is True, "study allowance missing")
need(len(data.get("modelReferenceLadder", [])) >= 6, "reference ladder too small")
need(set(data.get("characterMapping", {}).keys()) == {"lum","urd","belldandy","skuld"}, "four-character translation drift")
need(data.get("crownStatus") == "STOP", "Crown must STOP")

if errors:
    print("GOTHIC_MATRIARCH_REFERENCE_AUDIT=FAIL")
    for error in errors:
        print("ERROR=" + error)
    raise SystemExit(2)

print("GOTHIC_MATRIARCH_REFERENCE_AUDIT=PASS")
print("MODEL_REFERENCES=%d" % len(data["modelReferenceLadder"]))
print("BINARY_INGEST=NO")
print("RUNTIME_GEOMETRY=LUHM_ORIGINAL_ONLY")
print("CROWN_STATUS=STOP")

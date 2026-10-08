#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRESETS = ROOT / "game" / "assets" / "GODDESS_MORPH_PRESETS_V1.json"
CONTROLLER = ROOT / "scripts" / "game" / "characterMorphController.gd"
RUNTIME_SMOKE = ROOT / "tests" / "goddessMorphRuntimeSmoke.gd"
REGISTRY = ROOT / "media" / "fallout-body-mutation-source-registry-v1.json"
STUDY = ROOT / "doctrine" / "falloutBodyMutationStudyV1.json"

errors = []

def need(ok, message):
    if not ok:
        errors.append(message)

presets = json.loads(PRESETS.read_text(encoding="utf-8"))
registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
study = json.loads(STUDY.read_text(encoding="utf-8"))
controller = CONTROLLER.read_text(encoding="utf-8")
smoke = RUNTIME_SMOKE.read_text(encoding="utf-8")

need(presets.get("schema") == "luhmOs.goddessMorphPresets.v1", "preset schema drift")
need(presets.get("authority") == "Professor", "Professor authority missing")
need(presets.get("crownStatus") == "STOP", "preset Crown must STOP")
need(presets.get("runtimeLaw", {}).get("shapeMorphsSeparateFromPhysics") is True, "shape/physics separation missing")
need(presets.get("runtimeLaw", {}).get("automaticPresetDoesNotGrantCanon") is True, "preset self-promotion guard missing")

slider_names = set(presets.get("sliders", {}).keys())
need(len(slider_names) >= 10, "morph vocabulary too small")
need({"lum", "urd", "belldandy", "skuld"} == set(presets.get("presets", {}).keys()), "four-character preset set drift")

for character_id, item in presets.get("presets", {}).items():
    values = item.get("values", {})
    need(set(values.keys()) == slider_names, f"{character_id} slider set drift")
    for name, value in values.items():
        need(0.0 <= float(value) <= 1.0, f"{character_id}:{name} outside normalized range")

for token in ["apply_preset", "apply_values", "set_blend_shape_value", "missingCount", "physicsApplied", "canonPromoted"]:
    need(token in controller, f"controller token missing: {token}")

for token in ['apply_preset("urd")', "get_blend_shape_value", "GODDESS MORPH RUNTIME SMOKE GREEN"]:
    need(token in smoke, f"runtime smoke fixture missing: {token}")

need(registry.get("schema") == "luhmOs.falloutBodyMutationSourceRegistry.v1", "Fallout source registry schema drift")
need(registry.get("crownStatus") == "STOP", "Fallout registry Crown must STOP")
need(any(x.get("id") == "bodySlideOutfitStudio" and x.get("license") == "GPL-3.0" for x in registry.get("openSource", [])), "BodySlide GPL source record missing")
need(any(x.get("id") == "openCbpFo4" and x.get("license") == "GPL-3.0" for x in registry.get("openSource", [])), "OpenCBP GPL source record missing")
need(study.get("rightsFirewall", "").startswith("Reference the mechanics"), "rights firewall missing")
need(study.get("crownStatus") == "STOP", "Fallout study Crown must STOP")

if errors:
    print("GODDESS_MORPH_SOURCE_AUDIT=FAIL")
    for error in errors:
        print("ERROR=" + error)
    raise SystemExit(2)

print("GODDESS_MORPH_SOURCE_AUDIT=PASS")
print("CHARACTERS=lum,urd,belldandy,skuld")
print("BODYSLIDE_PATTERN=STAGED")
print("RUNTIME_CONTROLLER=SOURCE_READY")
print("RUNTIME_EXECUTION=NOT_CLAIMED")
print("CROWN_STATUS=STOP")

#!/usr/bin/env python3
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
errors: list[str] = []

def need(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)

def read(path: str) -> str:
    p = ROOT / path
    need(p.is_file(), f"missing {path}")
    return p.read_text(encoding="utf-8") if p.is_file() else ""

def load_json(path: str) -> dict:
    text = read(path)
    if not text:
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON {path}: {exc}")
        return {}

doctrine = load_json("doctrine/yumeCutsceneFactoryProofV1.json")
shot = load_json("cutscenes/yumeCutsceneFactoryProof.json")
quality = load_json("cutscenes/cinemaQualityV1.json")
scene = read("scenes/YumeCutsceneFactoryProof.tscn")
shot_script = read("scripts/yumeCutsceneShot.gd")
render = read("scripts/render-yume-cutscene-proof.sh")
encode = read("scripts/encode-yume-cutscene-proof.sh")
workflow = read(".github/workflows/yume-cutscene-factory-proof.yml")

need(doctrine.get("milestoneId") == "yumeCutsceneFactoryProof", "milestone drift")
need(doctrine.get("authority") == "Professor", "authority drift")
need(doctrine.get("boundaries", {}).get("crownStatus") == "STOP", "Crown must remain STOP")
for forbidden in ("merge", "publish", "release", "androidApk", "productionSigning", "deploy"):
    need(doctrine.get("boundaries", {}).get(forbidden) is False, f"{forbidden} must remain false")

render_law = doctrine.get("renderLaw", {})
need(render_law.get("godotVersion") == "4.7.2-stable", "Godot version drift")
need(render_law.get("fixedFps") == 30, "fixed FPS drift")
need(render_law.get("width") == 1080 and render_law.get("height") == 1920, "portrait resolution drift")
need(render_law.get("movieRenderRequiresExplicitCast") is True, "render must require CAST")
need(render_law.get("sourceShaMustMatchCheckout") is True, "render must bind source SHA")

need(shot.get("characterAssetState") == "PROXY_ONLY_NO_CANON_MEDIA_COMMITTED", "proof must not claim canon character media")
need(shot.get("environmentAssetState") == "PROXY_ONLY_NO_CANON_MEDIA_COMMITTED", "proof must not claim canon environment media")
need(shot.get("publication") == "FORBIDDEN_FROM_THIS_CANDIDATE", "publication boundary drift")
modes = [x.get("id") for x in shot.get("presentationModes", []) if isinstance(x, dict)]
need(modes == ["dayShift", "afterHours"], "presentation mode contract drift")

need(quality.get("profile") == "cinemaQuality", "cinema profile drift")
need(quality.get("distribution", {}).get("rightsReviewRequired") is True, "rights review must remain required")

for token in ("HeroProxy", "CameraRig", "Camera3D", "WorldEnvironment"):
    need(token in scene, f"scene missing {token}")
for token in ("LUHM_PRESENTATION_MODE", "dayShift", "afterHours", "get_tree().quit"):
    need(token in shot_script, f"shot runner missing {token}")
for token in ("LUHM_CAST", "SOURCE_DRIFT", "--write-movie", "--fixed-fps", "1080x1920"):
    need(token in render, f"render gate missing {token}")
for token in ("libx264", "yuv420p", "+faststart", "shot%08d.png"):
    need(token in encode, f"encoder missing {token}")

need("pull_request:" in workflow and "workflow_dispatch:" in workflow, "proof workflow trigger drift")
need("Godot_v4.7.2-stable_linux.x86_64.zip" in workflow, "workflow must pin Godot 4.7.2 binary")
need("cadd3204e728a35d3f13adb7fd0d7902636b79f6b95c40c265eb73b6c35329e4" in workflow, "workflow Godot checksum drift")
for forbidden in ("actions/upload-artifact", "gh release", "softprops/action-gh-release", "workflow_run:"):
    need(forbidden not in workflow, f"workflow must not contain {forbidden}")

try:
    tracked = subprocess.check_output(["git", "-C", str(ROOT), "ls-files"], text=True).splitlines()
except Exception as exc:
    errors.append(f"git ls-files failed: {exc}")
    tracked = []

raw_ext = {".mp4", ".mov", ".mkv", ".wav"}
for item in tracked:
    if item.startswith(("media/yume-cutscene-factory/", "cutscenes/yumeCutsceneFactoryProof/")):
        if pathlib.Path(item).suffix.lower() in raw_ext:
            errors.append(f"raw generated media committed: {item}")

if errors:
    print("RED_YUME_CUTSCENE_FACTORY_AUDIT")
    for error in errors:
        print(f"- {error}")
    sys.exit(1)

print("GREEN_YUME_CUTSCENE_FACTORY_STATIC")
print(f"sourceRef={doctrine.get('sourceRef')}")
print("renderAuthority=Professor+explicit_CAST")
print("publication=false")

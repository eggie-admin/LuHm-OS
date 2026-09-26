#!/usr/bin/env python3
from pathlib import Path
import json, sys

ROOT=Path(__file__).resolve().parents[1]
errors=[]
passes=[]

def load_json(path):
    return json.loads((ROOT/path).read_text(encoding="utf-8"))

def text(path):
    return (ROOT/path).read_text(encoding="utf-8")

def gate(name, ok, detail):
    passes.append({"name":name,"status":"GREEN" if ok else "RED","detail":detail})
    if not ok:
        errors.append(f"{name}: {detail}")

source=load_json("doctrine/SOURCE_OF_TRUTH.json")
h=load_json("doctrine/crownedCathedralSystemHarness-20260926.json")
p=load_json("agents/luhm-agent-mesh/crownedCathedralForgePipeline.json")
copilot=text(".github/copilot-instructions.md")
skill=text("skills/crowned-cathedral-forge/SKILL.md")

gate("01_authority", source["authority"]=="Professor" and h["authority"]["crown"]=="Professor", "Professor remains human final authority")
gate("02_source_law", h["source"]["source_law"]=="AI proposes. Policy authorizes. CI proves. Human promotes.", "source law exact")
gate("03_mesh", p["boss"]["name"]=="Lum" and p["limits"]["parallelism_max"]==3 and p["limits"]["recursive_recruitment"] is False, "Lum and bounded Oni mesh")
gate("04_copilot", "PAIR_PROGRAMMER_NOT_AUTHORITY" in json.dumps(p) and "Never describe a scope as GREEN" in copilot, "Copilot is helper, never approver")
gate("05_android_boundary", h["architecture"]["godot_world_owner"]=="Godot 4" and h["architecture"]["android_to_termux_exec"] is False, "Godot owns world and KAI boundary holds")
gate("06_webglass", h["architecture"]["webview_network"]=="dark" and h["architecture"]["generic_shell_bridge"] is False, "caged local WebGlass")
gate("07_shizuku", h["samsung"]["shizuku"]["detect_only_baseline"] is True and h["samsung"]["shizuku"]["generic_shell"] is False, "detect-only capability baseline")
gate("08_kai_boundary", h["kai9000"]["apk_lifecycle_authority"] is False, "KAI stays external")
gate("09_green_semantics", h["green_law"]["unknown_is_not_green"] is True, "unknown and pending cannot become GREEN")
gate("10_promotion", h["promotion"] is False and "Human promotes." in skill, "candidate cannot self-promote")

out=ROOT/"build"/"crowned-cathedral-forge"
out.mkdir(parents=True,exist_ok=True)
receipt={
  "schema":"luhm.crowned-cathedral-forge-audit.v1",
  "status":"GREEN" if not errors else "RED",
  "passes":passes,
  "errors":errors
}
(out/"receipt.json").write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
print(json.dumps(receipt,indent=2))
sys.exit(1 if errors else 0)

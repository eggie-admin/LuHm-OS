#!/usr/bin/env python3
import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_json(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))

catalog = load_json("assets/community/catalog.json")
selection = load_json("assets/community/selected-assets.json")
layout = load_json("assets/community/final-form-layout.json")
nexus = load_json("assets/community/nexus-private-donor-manifest.json")
final_doctrine = load_json("doctrine/finalFormCoffeehouseMutation-20260927.json")

assert catalog["policy"] == "CURATED_CC0_FIRST_NO_BLIND_VENDOR_INGEST"
assert catalog["provenance_required"] is True
assert len(catalog["sources"]) >= 6
for source_entry in catalog["sources"]:
    assert source_entry["url"].startswith("https://github.com/")
licenses = " ".join(str(s["license"]) for s in catalog["sources"])
assert "unknown" not in licenses.lower()

source = selection["source"]
assert source["repository"] == "shorepine/kenney"
assert source["license"] == "CC0"
assert source["runtime_network"] is False
assert source["build_time_fetch_only"] is True
assert re.fullmatch(r"[0-9a-f]{40}", source["commit"])

assets = []
selected_set = set()
furniture = set()
for kit, names in selection["groups"].items():
    assert kit in {"city-industrial", "factory", "furniture"}
    for name in names:
        assert name.endswith(".glb")
        assert "/" not in name and "\\" not in name
        key = f"{kit}/{name}"
        assets.append(key)
        selected_set.add(key)
        if kit == "furniture":
            furniture.add(name)

assert len(assets) == len(set(assets))
assert len(assets) == 77
assert len(assets) <= int(selection["budget"]["max_assets"])
assert int(selection["budget"]["max_total_bytes"]) <= 8 * 1024 * 1024

scene = layout["scene"]
assert scene["renderer"] == "GL Compatibility"
assert scene["runtime_network"] is False
assert len(scene["player_spawn"]) == 3
assert len(scene["lum_position"]) == 3
assert float(scene["camera_focus_distance"]) == 3.2

hero_keys = set()
hero_furniture = set()
for spec in layout["hero_placements"]:
    key = f"{spec['group']}/{spec['name']}"
    assert key in selected_set, key
    assert len(spec["pos"]) == 3
    assert float(spec["scale"]) > 0.0
    hero_keys.add(key)
    if spec["group"] == "furniture":
        hero_furniture.add(spec["name"])

assert furniture == hero_furniture, "every selected furniture model must have an intentional coffee-house hero placement"
assert layout["auto_dress"]["rule"].startswith("instantiate every immutable selected asset")

assert final_doctrine["status"] == "CANDIDATE_MUTATION_EXACT_HEAD_CI_REQUIRED"
assert final_doctrine["source_truth"]["community_asset_count"] == len(assets)
assert final_doctrine["source_truth"]["runtime_downloads"] is False
assert final_doctrine["source_truth"]["git_binary_vendor"] is False
assert len(final_doctrine["passes"]) == 10
assert final_doctrine["promotion"]["merge_to_main"] is False
assert final_doctrine["promotion"]["production_signing"] is False
assert final_doctrine["promotion"]["public_publish"] is False

rules = nexus["rules"]
assert rules["repository_binary_vendor"] is False
assert rules["ci_artifact_vendor"] is False
assert rules["apk_inclusion_default"] is False
assert rules["runtime_network"] is False
assert rules["wholesale_dump"] is False
assert rules["private_reference_allowed"] is True
accepted = set(rules["accepted_permission_evidence"])
assert accepted == {"open_license", "explicit_author_permission", "user_created_or_owned"}
allowed_scopes = set(rules["use_scopes"])

for entry in nexus["entries"]:
    assert entry["use_scope"] in allowed_scopes
    assert str(entry["page_url"]).startswith("https://www.nexusmods.com/")
    assert str(entry["author"]).strip()
    assert re.fullmatch(r"[0-9a-f]{64}", str(entry["sha256"]))
    assert entry["permission_evidence"] in accepted
    if entry["use_scope"] == "redistributable_build":
        assert entry["conversion_permission"] is True
        assert entry["redistribution_permission"] is True
        assert str(entry["attribution"]).strip()

required_files = [
    "tools/stageCommunityAssets.py",
    "scripts/game/communitySetDress.gd",
    "scripts/game/finalFormWorld.gd",
    "tests/communityAssetSmoke.gd",
    "blender/finalFormCoffeehouse.py",
]
for path in required_files:
    assert (ROOT / path).is_file(), path

stager = (ROOT / "tools/stageCommunityAssets.py").read_text(encoding="utf-8")
assert "raw.githubusercontent.com" in stager
assert "runtime_network" in stager
assert "PROVENANCE.json" in stager
assert "http://" not in stager

setdress = (ROOT / "scripts/game/communitySetDress.gd").read_text(encoding="utf-8")
assert "selected-assets.json" in setdress
assert "final-form-layout.json" in setdress
assert "ResourceLoader.exists" in setdress
assert "http://" not in setdress and "https://" not in setdress

world = (ROOT / "scripts/game/finalFormWorld.gd").read_text(encoding="utf-8")
assert 'extends "res://scripts/game/neonWorld.gd"' in world
assert "CoffeeHouseShell" in world
assert "final-form-layout.json" in world
assert "http://" not in world and "https://" not in world

main = (ROOT / "scripts/main.gd").read_text(encoding="utf-8")
assert 'preload("res://scripts/game/finalFormWorld.gd")' in main

blender_path = ROOT / "blender/finalFormCoffeehouse.py"
blender_source = blender_path.read_text(encoding="utf-8")
ast.parse(blender_source, filename=str(blender_path))
assert "selected-assets.json" in blender_source
assert "final-form-layout.json" in blender_source
assert "LuHmFinalFormCoffeehouse.blend" in blender_source
assert "LuHmFinalFormCoffeehouse.glb" in blender_source
assert "nexus-private-donor-manifest.json" in blender_source
assert "redistributable_build" in blender_source

print("COMMUNITY_ASSET_CATALOG=PASS")
print("CURATED_ASSET_COUNT=" + str(len(assets)))
print("IMMUTABLE_SOURCE_COMMIT=" + source["commit"])
print("FINAL_FORM_LAYOUT=PASS hero=%d furniture=%d" % (len(hero_keys), len(hero_furniture)))
print("NEXUS_PRIVATE_DONOR_GATE=PASS entries=%d" % len(nexus["entries"]))
print("BLENDER_FINAL_FORM_GENERATOR=PASS")
print("FINAL_FORM_10_PASS_CONTRACT=PASS")

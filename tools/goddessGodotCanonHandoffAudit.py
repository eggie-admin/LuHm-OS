#!/usr/bin/env python3
"""Source-only, fail-closed canonical Goddess Godot audit."""
import json
from pathlib import Path
root = Path(__file__).resolve().parents[1]
def read(path):
    return json.loads((root / path).read_text(encoding="utf-8"))
canon = read("game/canon/CHARACTER_CANON_V1.json")
assets = read("game/assets/ASSET_MANIFEST_V1.json")
plan = read("doctrine/goddessGodotCanonHandoffV1.json")
ids = ["lum", "urd", "belldandy", "skuld"]
assert plan["characterIds"] == ids
assert list(canon["characters"]) == ids
assert assets["characters"] == ids
assert all(canon["characters"][k]["design"] and canon["characters"][k]["motions"] for k in ids)
assert all(canon["characters"][k].get("adult", False) or canon["characters"][k].get("minimumAge", 0) >= 25 for k in ids)
assert canon["characters"]["skuld"]["minimumAge"] >= 25
roster = (root / "scripts/game/characterRoster.gd").read_text(encoding="utf-8")
assert "CHARACTER_CANON_V1.json" in roster and "set_active_character" in roster
assert plan["evidence"]["fourCharactersPlayable"] == "NOT_PROVED"
assert plan["evidence"]["chatGptPlayer"] == "NOT_PROVED"
print("GODDESS_GODOT_SOURCE_AUDIT_GREEN")

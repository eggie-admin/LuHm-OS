#!/usr/bin/env python3
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
doctrine = json.loads((root / "doctrine/finalCoffeeHouseMutation-20260927.json").read_text(encoding="utf-8"))

assert doctrine["authority"]["crown"] == "Professor"
assert doctrine["authority"]["auto_promote"] is False
assert doctrine["scene"]["world_owner"] == "Godot 4"
assert doctrine["scene"]["lum_idle_contract"] == "preserve existing AnimationTree idle resolver"
assert doctrine["assets"]["community_selected_count"] == 77
assert doctrine["assets"]["nexus"]["policy"] == "local permission-gated sidecar"
assert doctrine["assets"]["nexus"]["runtime_network"] is False
assert doctrine["assets"]["nexus"]["payload_claim"] == "NONE_OBSERVED_IN_REPO_OR_DRIVE"
assert doctrine["blender"]["authority"] == "reproducible generator; .blend is output, not source of truth"

required = [
    "scripts/game/finalCoffeeHouseOverlay.gd",
    "scripts/game/coffeeHouseSetDress.gd",
    "scripts/game/privateNexusSetDress.gd",
    "tests/finalCoffeeHouseSmoke.gd",
    "tools/stageNexusAssets.py",
    "tools/nexusAssetAudit.py",
    "tools/blender/buildCoffeeHouse.py",
    "assets/nexus/README.md",
    "assets/nexus/manifest.example.json",
]
for rel in required:
    assert (root / rel).is_file(), rel

main = (root / "scenes/Main.tscn").read_text(encoding="utf-8")
assert "FinalCoffeeHouseMutation" in main
overlay = (root / "scripts/game/finalCoffeeHouseOverlay.gd").read_text(encoding="utf-8")
assert "LumAvatarSocket" in overlay and "PrivateNexusSetDress" in overlay
assert "http://" not in overlay and "https://" not in overlay

print("FINAL_MUTATION_STATIC_AUDIT=PASS")

#!/usr/bin/env python3
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
catalog=json.loads((root/"game/demo/modInspirationCatalogV1.json").read_text())
profiles=json.loads((root/"game/demo/originalCompanionProfilesV1.json").read_text())
assert catalog["schema"]=="luhmOs.modInspirationCatalog.v1"
assert catalog["gameEngine"]=="Godot 4" and catalog["crown"]=="STOP"
assert catalog["noExternalDownloads"] and not catalog["copyAssets"]
assert len(catalog["sources"])>=8
for item in catalog["sources"]:
    assert item["url"].startswith("https://www.nexusmods.com/")
    assert item["fileReuse"] is False and item["rights"].startswith("REFERENCE_ONLY")
assert len(profiles["companions"])==3 and profiles["crown"]=="STOP"
for p in profiles["companions"]:
    assert p["adult"] is True
    assert set(p["dialogue"])=={"talk","help","explore","flirtElsewhere"}
assert "companion_studio_requested.emit()" in (root/"scripts/game/gameHud.gd").read_text()
assert "companion_studio_requested.connect(_enter_companion_lab)" in (root/"scripts/main.gd").read_text()
print("MOD_INSPIRATION_SOURCE_GREEN crown=STOP")

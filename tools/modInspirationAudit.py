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
rules=json.loads((root/"game/demo/relationshipRulesV2.json").read_text())
assert rules["schema"]=="luhmOs.relationshipRules.v2" and rules["crown"]=="STOP"
assert len(rules["events"])==7 and rules["safety"]["noGambling"] and rules["safety"]["localStateOnly"]
assert len(rules["tiers"])==4 and len(rules["rewards"])==3
assert rules["initial"]=={"trust":25,"affection":15,"jealousy":0}
for person in profiles["companions"]:
    assert set(person["dialogue"])==set(rules["events"])
index=json.loads((root/"game/demo/destinyChildReferenceIntakeV1.json").read_text())
assert index["publicExportAllowed"] is False and index["archiveCopiesIntoRepo"] is False
assert index["thirdPartyReferenceGroups"] >= 3 and index["crown"]=="STOP"
for path in ("frontEnd/prototypes/companionAtelier/index.html","frontEnd/prototypes/companionAtelier/app.mjs","frontEnd/prototypes/companionAtelier/live2dAdapter.mjs"):
    assert (root/path).exists()
print("MOD_INSPIRATION_SOURCE_GREEN crown=STOP relationship=v2 web=prototype")

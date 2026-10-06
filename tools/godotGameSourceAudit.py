#!/usr/bin/env python3
import json, pathlib, sys
root=pathlib.Path(__file__).resolve().parents[1]
required=[
 "project.godot","scenes/Main.tscn","scripts/main.gd",
 "scripts/game/characterRoster.gd","scripts/game/titan7Milestone.gd",
 "game/canon/CHARACTER_CANON_V1.json","game/assets/ASSET_MANIFEST_V1.json",
 "doctrine/GODOT4_GAME_SOURCE_V1.json"
]
missing=[p for p in required if not (root/p).is_file()]
errors=[]
for p in ["game/canon/CHARACTER_CANON_V1.json","game/assets/ASSET_MANIFEST_V1.json","doctrine/GODOT4_GAME_SOURCE_V1.json"]:
 try: json.loads((root/p).read_text())
 except Exception as e: errors.append(f"{p}: {e}")
canon=json.loads((root/"game/canon/CHARACTER_CANON_V1.json").read_text())
if canon["characters"]["skuld"].get("minimumAge",0)<25: errors.append("Skuld adult age gate failed")
if "celebrity likeness" not in canon["characters"]["skuld"].get("prohibited",[]): errors.append("identity firewall missing")
doctrine=json.loads((root/"doctrine/GODOT4_GAME_SOURCE_V1.json").read_text())
if doctrine.get("castRequiredForBuild") is not True: errors.append("CAST gate missing")
if missing or errors:
 print(json.dumps({"status":"RED","missing":missing,"errors":errors},indent=2)); sys.exit(1)
print(json.dumps({"status":"GREEN_SOURCE_STATIC_ONLY","required":required,"characters":list(canon["characters"]),"buildAuthorized":False},indent=2))

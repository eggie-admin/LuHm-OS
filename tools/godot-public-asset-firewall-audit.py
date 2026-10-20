#!/usr/bin/env python3
"""Fail closed if the public Godot Web build can package private donor GLBs."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
builder = (root / "tools/buildGodotWebHarness.sh").read_text(encoding="utf-8")
render = (root / "render.yaml").read_text(encoding="utf-8")
asset_root = root / "assets/lum"

for marker in (
    "DRIVE_ID=",
    "BUNDLE_SHA=",
    "download_drive",
    "drive.usercontent.google.com",
    "drive.google.com/uc",
    "Meshy_AI_Lum_Midnight_1996_biped",
):
    if marker in builder:
        raise SystemExit(f"RED_PUBLIC_GODOT_ASSET_FIREWALL: donor build marker present: {marker}")

for filename in ("luhm.glb", "luhmRunning.glb"):
    if (asset_root / filename).exists():
        raise SystemExit(f"RED_PUBLIC_GODOT_ASSET_FIREWALL: public source contains {filename}")

if not asset_root.is_dir():
    raise SystemExit("RED_PUBLIC_GODOT_ASSET_FIREWALL: stable Lum fallback socket missing")

if "python3 tools/godot-public-asset-firewall-audit.py" not in builder:
    raise SystemExit("RED_PUBLIC_GODOT_ASSET_FIREWALL: build audit is not invoked")

if "res://tools/godot-public-asset-firewall-smoke.gd" not in builder:
    raise SystemExit("RED_PUBLIC_GODOT_ASSET_FIREWALL: runtime smoke is not invoked")

if "tools/buildGodotWebHarness.sh" not in render:
    raise SystemExit("RED_PUBLIC_GODOT_ASSET_FIREWALL: Render no longer uses audited builder")

print("GREEN_PUBLIC_GODOT_ASSET_FIREWALL")

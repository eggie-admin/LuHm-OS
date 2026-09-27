#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SELECTED = ROOT / "assets/community/selected-assets.json"
COMMUNITY = ROOT / "scripts/game/communitySetDress.gd"
OVERLAY = ROOT / "scripts/game/finalCoffeeHouseOverlay.gd"
CROWN = ROOT / "scripts/game/crownCathedralSetDress.gd"


def fail(message: str) -> None:
    raise SystemExit("RED_CROWN_CATHEDRAL_AUDIT: " + message)


def main() -> int:
    manifest = json.loads(SELECTED.read_text(encoding="utf-8"))
    selected: list[str] = []
    for names in manifest["groups"].values():
        selected.extend(names)

    if len(selected) != 77:
        fail(f"selected asset count drift: {len(selected)}")
    if len(set(selected)) != 77:
        fail("selected asset list contains duplicates")
    if manifest["source"]["license"] != "CC0":
        fail("community license drift")
    if manifest["source"]["runtime_network"] is not False:
        fail("runtime network drift")

    community_text = COMMUNITY.read_text(encoding="utf-8")
    referenced = set(re.findall(r'"([A-Za-z0-9_-]+\.glb)"', community_text))
    missing = sorted(set(selected) - referenced)
    extras = sorted(referenced - set(selected))
    if missing:
        fail("selected assets not instantiated by runtime script: " + ", ".join(missing))
    if extras:
        fail("runtime script references non-selected community assets: " + ", ".join(extras))
    if "expected=77" not in community_text:
        fail("77-asset runtime receipt marker missing")

    overlay = OVERLAY.read_text(encoding="utf-8")
    required_overlay = [
        "TARGET_LUM_HEIGHT := 1.90",
        "CrownCathedralSetDressScript",
        "LumFocus.apply(player, lum)",
        "_measure_visual_height",
    ]
    for token in required_overlay:
        if token not in overlay:
            fail(f"overlay contract missing: {token}")

    crown = CROWN.read_text(encoding="utf-8")
    for token in ["CrownCathedralSign", "CrownGateTop", "RoofRidge", "LUHM // ONI CATHEDRAL"]:
        if token not in crown:
            fail(f"Crown Cathedral authored focal marker missing: {token}")

    receipt = {
        "schema": "luhm-os.crown-cathedral-static-audit.v1",
        "status": "PASS",
        "community_selected": len(selected),
        "community_runtime_referenced": len(referenced),
        "community_license": "CC0",
        "lum_target_height_m": 1.90,
        "cathedral_camera_authored": True,
        "crown_facade_present": True,
        "private_nexus_payload_required": False,
    }
    out = ROOT / "build/crown-cathedral/static-audit.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("CROWN_CATHEDRAL_STATIC_AUDIT=PASS assets=77")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

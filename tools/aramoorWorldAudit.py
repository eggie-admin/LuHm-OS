#!/usr/bin/env python3
"""Fail-closed source audit for Yume's private, module-attributed Godot world."""
from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "game/world/aramoorArchipelagoV1.json"
BUILDER = ROOT / "scripts/world/aramoorArchipelagoBuilder.gd"
PREVIEW = ROOT / "scenes/AramoorWorldPreview.tscn"
SMOKE = ROOT / "tests/aramoorWorldSmoke.gd"


def inspect(data: dict) -> list[str]:
    errors: list[str] = []
    def need(condition: bool, name: str) -> None:
        if not condition:
            errors.append(name)
    need(data.get("schema") == "luhmOs.aramoorArchipelago.v1", "schema")
    need(data.get("status") == "PRIVATE_SOURCE_CANDIDATE", "private_state")
    source = data.get("source", {})
    need(source.get("title") == "The Ghosts of Aramoor (system agnostic)", "module_identity")
    need(source.get("creator") == "JunkyardTornado", "attribution")
    need(source.get("adventureLicense") == "CC BY-SA 4.0", "share_alike_license")
    need(source.get("derivativeNarrativeShareAlike") is True, "share_alike_required")
    need(source.get("modulePdfInspected") is False, "unread_pdf_honesty")
    need(source.get("artworkLicenseSeparate") is True, "asset_rights_firewall")
    policy = data.get("artPolicy", {})
    need(policy.get("publicAllowed") is False, "private_only")
    need(policy.get("assetImportRequiresProvenance") is True, "import_provenance")
    need(policy.get("canonCharacterIds") == ["lum", "urd", "belldandy", "skuld"], "canon_ids")
    need(data.get("worlds") == ["livingTide", "ghostTide"], "tide_states")
    budget = data.get("zoneBudget", {})
    need(budget.get("maxShadowCasters") == 1, "shadow_budget")
    need(budget.get("maxDecorPerZone") == 7, "decoration_budget")
    need(data.get("gates", {}).get("crown") == "STOP", "crown_stop")
    need(data.get("gates", {}).get("automaticCanonPromotion") is False, "no_auto_promote")
    need(data.get("gates", {}).get("autonomousAgents") is False, "worker_quarantine")
    zones = data.get("zones")
    links = data.get("links")
    if not isinstance(zones, list) or not isinstance(links, list):
        return errors + ["zones_or_links_missing"]
    need(len(zones) == 9, "nine_regions")
    need(len(links) == 12, "twelve_bridges")
    ids: set[str] = set()
    grids: set[tuple[int, int]] = set()
    for z in zones:
        if not isinstance(z, dict):
            errors.append("bad_zone_record")
            continue
        zid = z.get("id")
        if not isinstance(zid, str) or not zid.isidentifier() or zid in ids:
            errors.append("duplicate_or_invalid_zone_id")
        else:
            ids.add(zid)
        grid = z.get("grid")
        if not isinstance(grid, list) or len(grid) != 2 or any(type(v) is not int or v < 0 or v > 2 for v in grid):
            errors.append("invalid_grid")
        else:
            t = tuple(grid)
            if t in grids:
                errors.append("overlapping_zones")
            grids.add(t)
        for key in ("name", "biome", "beat", "prop"):
            if not isinstance(z.get(key), str) or not z[key]:
                errors.append("missing_" + key)
        if z.get("npc") not in ("lum", "urd", "belldandy", "skuld"):
            errors.append("wrong_character")
        for key in ("color", "accent"):
            value = z.get(key, "")
            if not isinstance(value, str) or len(value) != 7 or value[0] != "#":
                errors.append("invalid_color")
            else:
                try:
                    int(value[1:], 16)
                except ValueError:
                    errors.append("invalid_color_hex")
    need(len(grids) == 9, "nine_unique_coordinates")
    adjacency = {k: set() for k in ids}
    seen: set[tuple[str, str]] = set()
    for edge in links:
        if not isinstance(edge, list) or len(edge) != 2:
            errors.append("invalid_edge")
            continue
        a, b = edge
        if not isinstance(a, str) or not isinstance(b, str) or a not in ids or b not in ids or a == b:
            errors.append("unknown_edge")
            continue
        pair = tuple(sorted((a, b)))
        if pair in seen:
            errors.append("duplicate_edge")
        seen.add(pair)
        adjacency[a].add(b)
        adjacency[b].add(a)
    visited = set()
    pending = ["aramoorHarbor"] if "aramoorHarbor" in ids else []
    while pending:
        node = pending.pop()
        if node in visited:
            continue
        visited.add(node)
        pending.extend(adjacency[node] - visited)
    need(visited == ids, "all_regions_reachable")
    need("ghostShipCavern" in ids, "ghost_ship_location")
    return errors


def main() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf8"))
    failures = inspect(data)
    if failures:
        raise SystemExit("RED_ARAMOOR_SOURCE: " + ",".join(failures))
    for name, mutate in (
        ("unlicensed", lambda d: d["source"].update(adventureLicense="UNKNOWN")),
        ("published", lambda d: d["artPolicy"].update(publicAllowed=True)),
        ("unread_pdf_faked", lambda d: d["source"].update(modulePdfInspected=True)),
        ("missing_region", lambda d: d["zones"].pop()),
        ("broken_bridge", lambda d: d["links"][0].__setitem__(1, "nonexistent")),
        ("quarantine_lift", lambda d: d["gates"].update(autonomousAgents=True)),
    ):
        changed = copy.deepcopy(data)
        mutate(changed)
        assert inspect(changed), "RED_NEGATIVE_CONTROL_MISSED:" + name
    source = BUILDER.read_text(encoding="utf8")
    preview = PREVIEW.read_text(encoding="utf8")
    smoke = SMOKE.read_text(encoding="utf8")
    for token in ("extends Node3D", "set_tide", "set_seed", "world_summary",
                  "DirectionalLight3D.new()", "StaticBody3D.new()", "CanonArtSocket"):
        assert token in source, "RED_BUILDER_CONTRACT:" + token
    for prohibited in ("HTTPRequest", "HTTPClient", "OS.execute", "load_external_asset", "FileAccess.WRITE"):
        assert prohibited not in source, "RED_REMOTE_OR_MUTATION_PRIMITIVE:" + prohibited
    assert "AramoorWorldPreview" in preview and "aramoorArchipelagoBuilder.gd" in preview
    assert "ARAMOOR_WORLD_GODOT_SMOKE_GREEN" in smoke
    print("GREEN_ARAMOOR_SOURCE_AUDIT")
    print("NEGATIVE_CONTROLS=6")
    print("REGIONS=9 BRIDGES=12 TIDES=2")
    print("RIGHTS=CC_BY_SA_4_ATTRIBUTION_PRIVATE_ONLY")
    print("GODOT_EXECUTION=REQUIRES_HEADLESS_CI")
    print("CROWN=STOP")


if __name__ == "__main__":
    main()

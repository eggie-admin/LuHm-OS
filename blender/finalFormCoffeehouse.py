#!/usr/bin/env python3
"""Build the LuHm final-form coffee-house Blender authoring project.

Run after the same assets used by the Godot candidate have been staged:

    python3 tools/stageCommunityAssets.py
    # stage the hash-pinned Lum GLB per doctrine/drive3dAssetMutation-20260925.json
    blender --background --python blender/finalFormCoffeehouse.py

The script intentionally does not download assets. Nexus donors are optional and are
only imported when the manifest marks them redistributable_build with conversion and
redistribution permission, and a local --nexus-dir file matches the recorded SHA-256.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
SELECTION = ROOT / "assets/community/selected-assets.json"
LAYOUT = ROOT / "assets/community/final-form-layout.json"
NEXUS = ROOT / "assets/community/nexus-private-donor-manifest.json"
RUNTIME = ROOT / "assets/community/runtime"
LUM = ROOT / "assets/lum/luhm.glb"
DEFAULT_BLEND = ROOT / "build/blender/LuHmFinalFormCoffeehouse.blend"
DEFAULT_GLB = ROOT / "build/blender/LuHmFinalFormCoffeehouse.glb"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1 :]
    else:
        argv = []
    parser = argparse.ArgumentParser()
    parser.add_argument("--blend-out", type=Path, default=DEFAULT_BLEND)
    parser.add_argument("--glb-out", type=Path, default=DEFAULT_GLB)
    parser.add_argument("--nexus-dir", type=Path)
    return parser.parse_args(argv)


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)


def godot_to_blender(value: list[float]) -> tuple[float, float, float]:
    return float(value[0]), -float(value[2]), float(value[1])


def imported_roots(before_names: set[str]) -> list[bpy.types.Object]:
    created = [obj for obj in bpy.context.scene.objects if obj.name not in before_names]
    created_names = {obj.name for obj in created}
    roots = [obj for obj in created if obj.parent is None or obj.parent.name not in created_names]
    return roots if roots else created


def import_glb(path: Path, label: str, position: list[float], rot_y: float, scale: float) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"{label}: staged GLB missing: {path}")
    before = {obj.name for obj in bpy.context.scene.objects}
    bpy.ops.import_scene.gltf(filepath=str(path))
    roots = imported_roots(before)
    if not roots:
        raise RuntimeError(f"{label}: Blender imported no objects")
    location = godot_to_blender(position)
    for root in roots:
        root.location.x += location[0]
        root.location.y += location[1]
        root.location.z += location[2]
        root.rotation_euler.z += math.radians(-float(rot_y))
        root.scale *= float(scale)
        root["luhm_source"] = label


def auto_spec(group: str, slot: int) -> dict:
    if group == "city-industrial":
        side = -1.0 if slot % 2 == 0 else 1.0
        lane = float(slot % 4)
        row = slot // 2
        return {"pos": [side * (19.0 + lane * 2.6), 0.0, 19.0 - float(row) * 3.4], "rot_y": 16.0 * side, "scale": 2.1}
    if group == "factory":
        column = slot % 8
        row = slot // 8
        return {"pos": [-10.5 + float(column) * 3.0, 0.0, 23.0 + float(row) * 3.0], "rot_y": -18.0 + float((slot * 23) % 37), "scale": 1.15}
    column = slot % 5
    row = slot // 5
    return {"pos": [-4.8 + float(column) * 2.4, 0.0, 10.4 + float(row) * 2.4], "rot_y": float((slot * 29) % 360), "scale": 1.15}


def add_material(name: str, base: tuple[float, float, float, float], emission: tuple[float, float, float, float] | None = None, strength: float = 0.0) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = base
    bsdf.inputs["Roughness"].default_value = 0.58
    if emission is not None and "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = emission
        bsdf.inputs["Emission Strength"].default_value = strength
    return material


def add_box(name: str, godot_pos: list[float], godot_size: list[float], material: bpy.types.Material) -> None:
    location = godot_to_blender(godot_pos)
    dimensions = (float(godot_size[0]), float(godot_size[2]), float(godot_size[1]))
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)


def build_shell() -> None:
    dark_wood = add_material("LuHm Dark Wood", (0.10, 0.045, 0.025, 1.0))
    warm_wood = add_material("LuHm Warm Wood", (0.28, 0.12, 0.055, 1.0))
    paper = add_material("LuHm Shoji", (0.82, 0.68, 0.48, 1.0), (1.0, 0.62, 0.28, 1.0), 0.35)
    neon = add_material("LuHm Neon", (0.10, 0.02, 0.08, 1.0), (1.0, 0.08, 0.42, 1.0), 2.8)
    add_box("CoffeeRearWall", [0.0, 2.15, 20.2], [13.0, 4.3, 0.28], dark_wood)
    add_box("CoffeeLeftWall", [-6.5, 2.15, 15.0], [0.28, 4.3, 10.6], dark_wood)
    add_box("CoffeeRightWall", [6.5, 2.15, 15.0], [0.28, 4.3, 10.6], dark_wood)
    add_box("CoffeeThreshold", [0.0, 0.09, 9.7], [13.0, 0.18, 0.34], warm_wood)
    for x in (-5.8, -2.9, 0.0, 2.9, 5.8):
        add_box(f"CoffeePost_{x:+.1f}", [x, 2.15, 19.98], [0.18, 4.3, 0.18], warm_wood)
    for x in (-4.35, -1.45, 1.45, 4.35):
        add_box(f"Shoji_{x:+.2f}", [x, 2.15, 20.02], [2.55, 3.55, 0.06], paper)
    for z in (10.0, 12.6, 15.2, 17.8, 20.0):
        add_box(f"CeilingRib_{z:.1f}", [0.0, 4.15, z], [13.0, 0.16, 0.22], warm_wood)
    add_box("CoffeeSign", [0.0, 3.45, 9.82], [3.6, 0.54, 0.10], neon)


def stage_community(selection: dict, layout: dict) -> int:
    hero = {(spec["group"], spec["name"]): spec for spec in layout["hero_placements"]}
    group_slots: dict[str, int] = {}
    count = 0
    for group, names in selection["groups"].items():
        for name in names:
            slot = group_slots.get(group, 0)
            group_slots[group] = slot + 1
            spec = hero.get((group, name), auto_spec(group, slot))
            import_glb(RUNTIME / group / name, f"community/{group}/{name}", spec["pos"], float(spec.get("rot_y", 0.0)), float(spec.get("scale", 1.0)))
            count += 1
    return count


def stage_lum(layout: dict) -> None:
    scene = layout["scene"]
    import_glb(LUM, "lum/luhm.glb", scene["lum_position"], 0.0, 1.0)
    for obj in bpy.context.scene.objects:
        if obj.get("luhm_source") == "lum/luhm.glb":
            obj["luhm_runtime_animation_authority"] = "Godot AnimationTree"


def stage_permitted_nexus(nexus: dict, nexus_dir: Path | None) -> int:
    permitted = [entry for entry in nexus["entries"] if entry.get("use_scope") == "redistributable_build" and entry.get("conversion_permission") is True and entry.get("redistribution_permission") is True]
    if not permitted:
        return 0
    if nexus_dir is None:
        print("NEXUS: permitted entries exist but --nexus-dir was not supplied; skipping local donors")
        return 0
    count = 0
    for index, entry in enumerate(permitted):
        file_name = str(entry.get("file_name", ""))
        if not file_name or "/" in file_name or "\\" in file_name:
            raise RuntimeError("Nexus redistributable_build entry requires safe file_name")
        path = nexus_dir / file_name
        if sha256_file(path) != entry["sha256"]:
            raise RuntimeError(f"Nexus SHA-256 mismatch: {file_name}")
        if path.suffix.lower() not in {".glb", ".gltf"}:
            raise RuntimeError(f"Nexus Blender lane currently accepts GLB/glTF only: {file_name}")
        import_glb(path, f"nexus/{file_name}", [14.0 + index * 3.0, 0.0, 28.0], 0.0, 1.0)
        count += 1
    return count


def main() -> None:
    args = parse_args()
    selection = load_json(SELECTION)
    layout = load_json(LAYOUT)
    nexus = load_json(NEXUS)
    clear_scene()
    build_shell()
    community_count = stage_community(selection, layout)
    if community_count != 77:
        raise RuntimeError(f"community asset count drift: {community_count}")
    stage_lum(layout)
    nexus_count = stage_permitted_nexus(nexus, args.nexus_dir)
    args.blend_out.parent.mkdir(parents=True, exist_ok=True)
    args.glb_out.parent.mkdir(parents=True, exist_ok=True)
    bpy.context.scene["luhm_final_form"] = True
    bpy.context.scene["community_asset_count"] = community_count
    bpy.context.scene["nexus_redistributable_count"] = nexus_count
    bpy.context.scene["godot_renderer"] = "GL Compatibility"
    bpy.ops.wm.save_as_mainfile(filepath=str(args.blend_out))
    bpy.ops.export_scene.gltf(filepath=str(args.glb_out), export_format="GLB", export_animations=True)
    print(f"LUHM_BLENDER_FINAL_FORM=PASS community={community_count} nexus_redistributable={nexus_count} blend={args.blend_out} glb={args.glb_out}")


if __name__ == "__main__":
    main()

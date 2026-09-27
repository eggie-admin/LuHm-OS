#!/usr/bin/env python3
"""Reproducible Blender assembly for the LuHm kissaten scene.

Run with:
  blender --background --python tools/blender/buildCoffeeHouse.py -- \
    --output-blend /path/to/luhm-kissaten.blend \
    --output-glb /path/to/luhm-kissaten.glb

The script uses project-owned procedural architecture plus already-staged GLB
assets. Optional private Nexus sidecar assets are consumed only when they exist
locally; they are never downloaded by this script.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import bpy
except Exception as exc:  # pragma: no cover - Blender runtime only
    raise SystemExit(f"This script must run inside Blender: {exc}")

ROOT = Path(__file__).resolve().parents[2]


def argv_after_double_dash() -> list[str]:
    return sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []


def add_box(name: str, location, scale) -> None:
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)


def import_glb(path: Path, collection_name: str) -> None:
    if not path.is_file():
        return
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    imported = [obj for obj in bpy.data.objects if obj not in before]
    collection = bpy.data.collections.get(collection_name) or bpy.data.collections.new(collection_name)
    if collection not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(collection)
    for obj in imported:
        for owner in list(obj.users_collection):
            owner.objects.unlink(obj)
        collection.objects.link(obj)


def build() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    # Architectural blockout mirrors the Godot procedural kissaten.
    add_box("Floor", (0.0, 0.05, 14.2), (6.9, 0.05, 5.4))
    add_box("BackWall", (0.0, 2.5, 19.2), (6.9, 2.5, 0.12))
    add_box("LeftWall", (-6.8, 2.5, 14.2), (0.12, 2.5, 5.1))
    add_box("RightWall", (6.8, 2.5, 14.2), (0.12, 2.5, 5.1))

    lum = ROOT / "assets/lum/luhm.glb"
    import_glb(lum, "Lum")

    community = ROOT / "assets/community/runtime/furniture"
    for name in [
        "kitchenBar.glb", "kitchenBarEnd.glb", "stoolBar.glb",
        "tableRound.glb", "loungeChair.glb", "pottedPlant.glb",
        "lampSquareFloor.glb", "radio.glb"
    ]:
        import_glb(community / name, "CommunityFurniture")

    receipt = ROOT / "assets/nexus/runtime/PROVENANCE.json"
    if receipt.is_file():
        data = json.loads(receipt.read_text(encoding="utf-8"))
        for asset in data.get("assets", []):
            runtime_path = str(asset.get("runtime_path", ""))
            prefix = "res://"
            if runtime_path.startswith(prefix) and runtime_path.endswith(".glb"):
                import_glb(ROOT / runtime_path[len(prefix):], "PrivateNexus")

    bpy.context.scene.render.engine = "BLENDER_EEVEE_NEXT"
    bpy.context.scene.render.resolution_x = 1080
    bpy.context.scene.render.resolution_y = 1920

    parser = argparse.ArgumentParser()
    parser.add_argument("--output-blend", type=Path)
    parser.add_argument("--output-glb", type=Path)
    args = parser.parse_args(argv_after_double_dash())

    if args.output_blend:
        args.output_blend.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(args.output_blend))
    if args.output_glb:
        args.output_glb.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.export_scene.gltf(filepath=str(args.output_glb), export_format="GLB")


if __name__ == "__main__":
    build()

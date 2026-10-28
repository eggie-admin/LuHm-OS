"""LuHm disposable Blender to Godot GLB handoff.

Only generates two new procedural meshes. Never exports selected user artwork.
Run in Blender with: --python host/blender/blender-godot-handoff.py -- [--output-dir PATH]
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile

import bpy

REPO = Path(__file__).resolve().parents[2]
GLB_NAME = "proof-marker.glb"
MANIFEST_NAME = "proof-manifest.json"


def arguments():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description="Export original procedural handoff marker")
    parser.add_argument("--output-dir", type=Path, help="Out-of-repo disposable output directory")
    return parser.parse_args(argv)


def output_location(specified):
    folder = (specified if specified is not None
              else Path(tempfile.mkdtemp(prefix="luhm-handoff-"))).expanduser().resolve()
    if folder == REPO or REPO in folder.parents:
        raise ValueError("Handoff outputs must remain outside the GitHub source tree")
    if (folder / GLB_NAME).exists() or (folder / MANIFEST_NAME).exists():
        raise FileExistsError("Refusing to overwrite an existing proof artifact")
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def make_marker(folder):
    created = []
    original_selected = tuple(bpy.context.selected_objects)
    original_active = bpy.context.view_layer.objects.active
    target = folder / GLB_NAME
    try:
        bpy.ops.object.select_all(action="DESELECT")
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.8, 0.0, 0.5))
        cube = bpy.context.object
        cube.name = "luhm-proof-cube"
        created.append(cube)

        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.5,
                                               location=(0.8, 0.0, 0.5))
        sphere = bpy.context.object
        sphere.name = "luhm-proof-sphere"
        created.append(sphere)

        bpy.ops.object.select_all(action="DESELECT")
        for item in created:
            item.select_set(True)
        bpy.context.view_layer.objects.active = cube
        result = bpy.ops.export_scene.gltf(
            filepath=str(target),
            export_format="GLB",
            use_selection=True,
            export_animations=False,
            export_cameras=False,
            export_lights=False,
        )
        if "FINISHED" not in result or not target.is_file():
            raise RuntimeError("Blender glTF exporter did not produce the proof marker")
    finally:
        for item in created:
            bpy.data.objects.remove(item, do_unlink=True)
        for item in original_selected:
            if item.name in bpy.data.objects:
                item.select_set(True)
        if original_active is not None and original_active.name in bpy.data.objects:
            bpy.context.view_layer.objects.active = original_active

    digest = hashlib.sha256()
    with target.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    receipt = {
        "schema": "luhm-os.blender-godot-handoff.v1",
        "status": "LOCAL_EXPERIMENT_NOT_CROWN",
        "origin": "new-procedural-marker-only",
        "assetFile": GLB_NAME,
        "sha256": digest.hexdigest(),
        "byteSize": target.stat().st_size,
        "blenderVersion": bpy.app.version_string,
        "privateArtworkIncluded": False,
        "deviceProof": False,
        "releaseAuthorized": False,
    }
    (folder / MANIFEST_NAME).write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print("GREEN_BLENDER_PROCEDURAL_EXPORT_SOURCE_ARTIFACT")
    print("LUHM_HANDOFF_MANIFEST=" + str(folder / MANIFEST_NAME))
    return receipt


def main():
    folder = output_location(arguments().output_dir)
    make_marker(folder)


if __name__ == "__main__":
    main()

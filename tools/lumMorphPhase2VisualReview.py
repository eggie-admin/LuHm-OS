#!/usr/bin/env python3
"""Headless Blender review frames for the exact hash-pinned Lum candidate.

Render-only, no publication or canon promotion. Run from GitHub Actions:
blender -b -t 2 --python tools/lumMorphPhase2VisualReview.py --
  <candidate.glb> <private-temp-folder>
"""
import bpy
import hashlib
import json
import math
import sys
from pathlib import Path
from mathutils import Vector, Quaternion

EXPECTED_HASH = "4b8d41393bb94affe469af551c2915d6b39890cd2add18048d78da8610505a1e"
SHAPES = ("hip_width", "waist_shape", "smile")
FRAMES = (
    ("neutralFront", "front", False, False, False),
    ("morphedFront", "front", True, False, False),
    ("neutralQuarter", "quarter", False, False, False),
    ("morphedQuarter", "quarter", True, False, False),
    ("morphedPose", "quarter", True, True, False),
    ("morphedFace", "front", True, False, True),
)

def need(ok, label):
    if not ok:
        raise RuntimeError("RED_LUM_VISUAL: " + label)

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def aim(camera, target):
    direction = Vector(target) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

def placeArea(name, position, power, rgb, size, target):
    light_data = bpy.data.lights.new(name, type="AREA")
    light_data.energy = power
    light_data.color = rgb
    light_data.shape = "DISK"
    light_data.size = size
    light = bpy.data.objects.new(name, light_data)
    bpy.context.collection.objects.link(light)
    light.location = position
    aim(light, target)

def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    need(len(args) == 2, "required model path and output directory")
    model_path, out_path = args
    out = Path(out_path)
    out.mkdir(parents=True, exist_ok=True)
    need(digest(model_path) == EXPECTED_HASH, "GLB SHA mismatch")
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(Path(model_path).resolve()), import_pack_images=True)
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    armatures = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"]
    need(len(meshes) > 0 and len(armatures) > 0, "rigged mesh import missing")
    found = set()
    for mesh in meshes:
        keys = mesh.data.shape_keys
        if keys:
            found.update(keys.key_blocks.keys())
    need(set(SHAPES).issubset(found), "actual named morph keys missing: " + repr(sorted(found)))
    bone_names = set()
    for arm in armatures:
        bone_names.update(arm.pose.bones.keys())
    expected_bones = {"LeftArm", "RightArm", "LeftLeg", "RightLeg"}
    need(expected_bones.issubset(bone_names), "four canonical limb bones missing")

    # The import may add a 1/100 transform. Use evaluated world-space bounds,
    # not assumptions about model height in scene units.
    corners = [obj.matrix_world @ Vector(corner) for obj in meshes for corner in obj.bound_box]
    min_corner = Vector(tuple(min(p[k] for p in corners) for k in range(3)))
    max_corner = Vector(tuple(max(p[k] for p in corners) for k in range(3)))
    center = (min_corner + max_corner) * 0.5
    height = max(0.0001, max_corner.z - min_corner.z)
    need(height > 0.00001 and math.isfinite(height), "invalid geometry bounds")

    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 10
    scene.render.resolution_x = 448
    scene.render.resolution_y = 576
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"  # temporary only; FFmpeg emits WebP
    scene.render.film_transparent = False
    scene.world.color = (0.012, 0.012, 0.025)
    world = bpy.data.worlds.new("LumReviewWorld")
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = (0.025, 0.016, 0.045, 1)
    bg.inputs["Strength"].default_value = 0.6
    scene.world = world
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "Medium High Contrast"
    scene.camera = bpy.data.objects.new("ReviewCamera", bpy.data.cameras.new("ReviewCamera"))
    bpy.context.collection.objects.link(scene.camera)
    cam = scene.camera
    cam.data.type = "ORTHO"
    cam.data.lens = 55
    cam.data.ortho_scale = height * 1.24
    light_span = height * 1.7
    placeArea("LumKeyLight", center + Vector((-light_span, -light_span, height * .8)), 370, (0.64, 0.93, 1.0), height * 1.8, center)
    placeArea("LumRimLight", center + Vector((light_span, light_span * .6, height * 1.0)), 470, (0.92, 0.25, 1.0), height * 1.25, center)
    placeArea("LumFill", center + Vector((light_span*.7, -light_span, height*.4)), 200, (1.0, .84, .76), height * 1.8, center)

    original_poses = {}
    for arm in armatures:
        original_poses[arm.name] = {bone.name: bone.rotation_quaternion.copy() for bone in arm.pose.bones}
        if arm.animation_data is not None:
            arm.animation_data.action = None
    for mesh in meshes:
        if mesh.animation_data is not None:
            mesh.animation_data.action = None

    report = {"schema": "luhmOs.lumMorphPhase2VisualReview.v1",
              "sourceSha256": EXPECTED_HASH,
              "renderer": "Blender Cycles CPU", "status": "REVIEW_REQUIRED",
              "morphNames": list(SHAPES), "modelMeshes": len(meshes),
              "armatures": len(armatures), "clipPenetrationCertified": False,
              "artisticIdentityApproved": False, "canonPromoted": False,
              "modelBinaryInArtifact": False, "crown": "STOP",
              "frames": []}

    for frame_name, viewpoint, use_morph, use_pose, closeup in FRAMES:
        for mesh in meshes:
            if mesh.data.shape_keys is None:
                continue
            for key in mesh.data.shape_keys.key_blocks:
                if key.name in SHAPES:
                    key.value = 0.80 if use_morph else 0.0
        for arm in armatures:
            for bone in arm.pose.bones:
                bone.rotation_mode = "QUATERNION"
                bone.rotation_quaternion = original_poses[arm.name][bone.name].copy()
            if use_pose:
                for name, degrees in (("LeftArm", 35), ("RightArm", -35), ("LeftLeg", 20), ("RightLeg", -20)):
                    bone = arm.pose.bones.get(name)
                    if bone:
                        axis = Vector((1,0,0)) if "Leg" in name else Vector((0,0,1))
                        bone.rotation_quaternion = bone.rotation_quaternion @ Quaternion(axis, math.radians(degrees))
        target = center + Vector((0, 0, height * (0.22 if closeup else 0.0)))
        if viewpoint == "quarter":
            cam.location = center + Vector((height * 1.1, -height * 2.0, height * .3))
        else:
            cam.location = center + Vector((0, -height * 2.4, height * .23))
        aim(cam, target)
        cam.data.ortho_scale = height * (.45 if closeup else 1.22)
        bpy.context.view_layer.update()
        filename = frame_name + ".png"
        scene.render.filepath = str(out / filename)
        bpy.ops.render.render(write_still=True)
        image_path = out / filename
        need(image_path.exists() and image_path.stat().st_size > 5000, "render missing: " + frame_name)
        report["frames"].append({"name": frame_name, "temporaryPngSha256": digest(image_path), "pose": use_pose, "morphApplied": use_morph, "faceCloseup": closeup})
        print("LUM_VISUAL_FRAME_GREEN", frame_name, image_path.stat().st_size, flush=True)
    (out / "visualReviewReceipt.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("LUM_VISUAL_RENDER_GATE_GREEN_REVIEW_PENDING", flush=True)

if __name__ == "__main__":
    main()

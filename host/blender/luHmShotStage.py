#!/usr/bin/env python3
"""Run inside a local Blender Python interpreter to stage an original LuHm scene.
Example: blender --background --python host/blender/luHmShotStage.py -- --input story.json --scene nightglassBarHub --output /tmp/preview.blend
No network, scripts from source, asset download, silent overwrites or headless server.
"""
from __future__ import annotations
import argparse
import json
import math
import sys
from pathlib import Path

def parseSource(path,sceneId):
    data=json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("schema")!="luhmOs.creatorStudioWorld.v1" or data.get("product")!="LuHm-OS":
        raise ValueError("LuHm-OS Creator Studio JSON required")
    if data.get("assetPolicy",{}).get("thirdPartyDataAllowed") is not False:
        raise ValueError("Third-party runtime art forbidden")
    for scene in data.get("scenes",[]):
        if scene.get("sceneId")==sceneId and scene.get("kind") in ("socialHub","exploration"):
            colors=scene.get("palette",{})
            if not all(isinstance(colors.get(k),str) and len(colors[k])==6 and all(c in "0123456789abcdefABCDEF" for c in colors[k]) for k in ("sky","floor","light")):
                raise ValueError("Invalid palette")
            return scene
    raise ValueError("Scene not found or not previewable")

def rgb(value):
    from mathutils import Color
    col=Color(tuple(int(value[i:i+2],16)/255 for i in (0,2,4)))
    return tuple(col)+ (1.0,)

def stage(scene,bpy):
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.ops.mesh.primitive_cube_add(location=(0,0,-0.1))
    floor=bpy.context.object
    floor.name="OriginalFloor"
    floor.scale=(10,8,0.1)
    material=bpy.data.materials.new("OriginalFloorMaterial")
    material.diffuse_color=rgb(scene["palette"]["floor"])
    floor.data.materials.append(material)
    if scene["kind"]=="socialHub":
        bpy.ops.mesh.primitive_cube_add(location=(0,-2,0.7))
        bpy.context.object.name="OriginalBarCounter"
        bpy.context.object.scale=(4.5,0.6,0.7)
    else:
        bpy.ops.mesh.primitive_cube_add(location=(0,-3,0))
        bpy.context.object.name="OriginalShoreline"
        bpy.context.object.scale=(9,3,0.08)
    bpy.ops.object.light_add(type="AREA",location=(0,-1,6))
    light=bpy.context.object
    light.name="OriginalSceneKeyLight"
    light.data.energy=650
    light.data.color=rgb(scene["palette"]["light"])[:3]
    bpy.ops.object.camera_add(location=(0,8,5))
    cam=bpy.context.object
    cam.name="OriginalStudioCamera"
    direction=Vector((0.0,0.0,0.0))-cam.location
    cam.rotation_euler=direction.to_track_quat("-Z","Y").to_euler()
    bpy.context.scene.camera=cam
    bpy.context.scene.render.resolution_x=1280
    bpy.context.scene.render.resolution_y=720
    bpy.context.scene.render.resolution_percentage=50

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True)
    p.add_argument("--scene",required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args(argv)
    output=Path(args.output)
    if output.exists() or output.suffix.lower()!=".blend" or not output.parent.is_dir():
        raise ValueError("new .blend output in existing local directory required")
    scene=parseSource(args.input,args.scene)
    try:
        import bpy
        from mathutils import Vector
    except ImportError as exc:
        raise RuntimeError("Use Blender's own Python interpreter") from exc
    stage(scene,bpy)
    bpy.ops.wm.save_as_mainfile(filepath=str(output.resolve()))
    print(json.dumps({"status":"ORIGINAL_BLENDER_STAGE_WRITTEN","scene":args.scene,"assetDownloads":False,"crown":"STOP"}))

if __name__=="__main__":
    argv=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
    main(argv)

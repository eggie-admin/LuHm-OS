#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path
import struct


def require(ok, message):
    if not ok:
        raise SystemExit(f"RED: {message}")
    print(f"GREEN: {message}")


def git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def load_glb(path: Path):
    data = path.read_bytes()
    require(len(data) >= 20, "GLB has data")
    magic, version, length = struct.unpack_from("<4sII", data, 0)
    require(magic == b"glTF", "GLB magic")
    require(version == 2, "glTF version 2")
    require(length == len(data), "GLB declared length matches")
    offset = 12
    doc = None
    while offset < length:
        chunk_len, chunk_type = struct.unpack_from("<II", data, offset)
        offset += 8
        chunk = data[offset: offset + chunk_len]
        offset += chunk_len
        if chunk_type == 0x4E4F534A:
            doc = json.loads(chunk.decode("utf-8").rstrip("\x00 \t\r\n"))
    require(isinstance(doc, dict), "GLB JSON chunk parses")
    return data, doc


def main():
    p = argparse.ArgumentParser()
    p.add_argument("path", type=Path)
    p.add_argument("--expected-git-blob", required=True)
    p.add_argument("--receipt", type=Path)
    args = p.parse_args()

    data, doc = load_glb(args.path)
    actual_blob = git_blob_sha1(data)
    require(actual_blob == args.expected_git_blob.lower(), "immutable donor Git blob matches")

    materials = doc.get("materials", [])
    textures = doc.get("textures", [])
    images = doc.get("images", [])
    meshes = doc.get("meshes", [])
    skins = doc.get("skins", [])
    nodes = doc.get("nodes", [])
    animations = doc.get("animations", [])
    morph_targets = sum(
        len(primitive.get("targets", []))
        for mesh in meshes
        for primitive in mesh.get("primitives", [])
    )

    require(len(meshes) >= 1, "donor has render mesh")
    require(len(materials) >= 1, "donor has materials")
    require(len(textures) >= 1, "donor has textures")
    require(len(images) >= 1, "donor has image payloads")
    require(len(skins) >= 1, "donor has skinned rig")

    vrm = doc.get("extensions", {}).get("VRM", {})
    require(isinstance(vrm, dict) and bool(vrm), "VRM metadata present")
    meta = vrm.get("meta", {})
    license_name = str(meta.get("licenseName", ""))
    require(license_name.upper() == "CC0", "embedded VRM license is CC0")

    human_bones = vrm.get("humanoid", {}).get("humanBones", [])
    require(len(human_bones) >= 20, "VRM humanoid map is substantial")
    mapped = {str(item.get("bone", "")): int(item.get("node", -1)) for item in human_bones}
    for key in ("hips", "spine", "chest", "neck", "head", "leftEye", "rightEye", "leftHand", "rightHand", "leftFoot", "rightFoot"):
        require(key in mapped, f"humanoid semantic present: {key}")

    blend_groups = vrm.get("blendShapeMaster", {}).get("blendShapeGroups", [])
    require(len(blend_groups) >= 5, "VRM expression groups present")
    spring_groups = vrm.get("secondaryAnimation", {}).get("boneGroups", [])

    def node_name(index):
        if 0 <= index < len(nodes):
            return str(nodes[index].get("name", ""))
        return ""

    canonical = {semantic: node_name(index) for semantic, index in mapped.items() if node_name(index)}
    expression_names = [str(x.get("name", "")) for x in blend_groups]
    material_names = [str(x.get("name", "")) for x in materials]

    receipt = {
        "schema": "luhm-os.character-donor-receipt.v1",
        "path": str(args.path),
        "gitBlobSha1": actual_blob,
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
        "license": license_name,
        "counts": {
            "meshes": len(meshes),
            "materials": len(materials),
            "textures": len(textures),
            "images": len(images),
            "skins": len(skins),
            "nodes": len(nodes),
            "animations": len(animations),
            "morphTargets": morph_targets,
            "vrmHumanoidBones": len(human_bones),
            "vrmExpressionGroups": len(blend_groups),
            "vrmSpringBoneGroups": len(spring_groups),
        },
        "canonicalBoneMap": canonical,
        "expressionNames": expression_names,
        "materialNames": material_names,
        "status": "GREEN_DONOR_STATIC_AUDIT",
    }
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()

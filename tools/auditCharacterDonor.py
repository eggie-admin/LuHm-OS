#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path
import re
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


def norm(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower().replace("mixamorig", ""))


ALIASES = {
    "hips": ["hips", "pelvis"],
    "spine": ["spine"],
    "chest": ["spine1", "chest"],
    "upper_chest": ["spine2", "upperchest"],
    "neck": ["neck"],
    "head": ["head"],
    "left_upper_leg": ["leftupleg", "leftthigh"],
    "left_lower_leg": ["leftleg", "leftcalf"],
    "left_foot": ["leftfoot"],
    "right_upper_leg": ["rightupleg", "rightthigh"],
    "right_lower_leg": ["rightleg", "rightcalf"],
    "right_foot": ["rightfoot"],
    "left_shoulder": ["leftshoulder"],
    "left_upper_arm": ["leftarm", "leftupperarm"],
    "left_lower_arm": ["leftforearm", "leftlowerarm"],
    "left_hand": ["lefthand"],
    "right_shoulder": ["rightshoulder"],
    "right_upper_arm": ["rightarm", "rightupperarm"],
    "right_lower_arm": ["rightforearm", "rightlowerarm"],
    "right_hand": ["righthand"],
    "left_eye": ["lefteye", "eyeleft"],
    "right_eye": ["righteye", "eyeright"],
}


def canonical_from_nodes(nodes, joint_indices):
    names = {}
    for idx in joint_indices:
        if 0 <= idx < len(nodes):
            raw = str(nodes[idx].get("name", ""))
            if raw:
                names[norm(raw)] = raw
    out = {}
    for semantic, aliases in ALIASES.items():
        for alias in aliases:
            if norm(alias) in names:
                out[semantic] = names[norm(alias)]
                break
    return out


def collect_target_names(meshes):
    names = []
    for mesh in meshes:
        extras = mesh.get("extras", {})
        target_names = extras.get("targetNames", []) if isinstance(extras, dict) else []
        names.extend(str(x) for x in target_names)
    return names


def main():
    p = argparse.ArgumentParser()
    p.add_argument("path", type=Path)
    p.add_argument("--expected-git-blob", required=True)
    p.add_argument("--license", default="CC0")
    p.add_argument("--profile", choices=("auto", "vrm", "facial-glb"), default="auto")
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
    target_names = collect_target_names(meshes)
    all_joints = sorted({int(j) for skin in skins for j in skin.get("joints", [])})

    print("DONOR_COUNTS", json.dumps({
        "meshes": len(meshes), "materials": len(materials), "textures": len(textures),
        "images": len(images), "skins": len(skins), "nodes": len(nodes),
        "animations": len(animations), "morphTargets": morph_targets,
        "jointNodes": len(all_joints), "targetNames": len(target_names)
    }, sort_keys=True))

    require(len(meshes) >= 1, "donor has render mesh")
    require(len(materials) >= 1, "donor has materials")
    require(len(textures) >= 1, "donor has textures")
    require(len(images) >= 1, "donor has image payloads")
    require(len(skins) >= 1, "donor has skinned rig")
    require(str(args.license).upper() == "CC0", "external provenance declares CC0")

    vrm = doc.get("extensions", {}).get("VRM", {})
    profile = args.profile
    if profile == "auto":
        profile = "vrm" if isinstance(vrm, dict) and bool(vrm) else "facial-glb"

    canonical = {}
    expression_names = []
    spring_groups = []
    embedded_license = None

    if profile == "vrm":
        require(isinstance(vrm, dict) and bool(vrm), "VRM metadata present")
        meta = vrm.get("meta", {})
        embedded_license = str(meta.get("licenseName", ""))
        require(embedded_license.upper() == "CC0", "embedded VRM license is CC0")
        human_bones = vrm.get("humanoid", {}).get("humanBones", [])
        require(len(human_bones) >= 20, "VRM humanoid map is substantial")
        mapped = {str(item.get("bone", "")): int(item.get("node", -1)) for item in human_bones}
        for key in ("hips", "spine", "chest", "neck", "head", "leftEye", "rightEye", "leftHand", "rightHand", "leftFoot", "rightFoot"):
            require(key in mapped, f"humanoid semantic present: {key}")
        def node_name(index):
            return str(nodes[index].get("name", "")) if 0 <= index < len(nodes) else ""
        canonical = {semantic: node_name(index) for semantic, index in mapped.items() if node_name(index)}
        blend_groups = vrm.get("blendShapeMaster", {}).get("blendShapeGroups", [])
        expression_names = [str(x.get("name", "")) for x in blend_groups]
        spring_groups = vrm.get("secondaryAnimation", {}).get("boneGroups", [])
        require(len(expression_names) >= 5, "VRM expression groups present")
    else:
        require(len(all_joints) >= 20, "facial GLB has substantial skeleton")
        canonical = canonical_from_nodes(nodes, all_joints)
        core = ["hips", "spine", "neck", "head", "left_upper_leg", "left_lower_leg", "left_foot", "right_upper_leg", "right_lower_leg", "right_foot", "left_upper_arm", "left_lower_arm", "left_hand", "right_upper_arm", "right_lower_arm", "right_hand"]
        missing = [x for x in core if x not in canonical]
        require(not missing, "core humanoid semantics resolve")
        require(morph_targets >= 15, "facial GLB exposes substantial morph targets")
        expression_names = target_names
        lower = {x.lower() for x in target_names}
        viseme_hits = sum(1 for x in ("viseme_pp", "viseme_ff", "viseme_aa", "viseme_e", "viseme_i", "viseme_o", "viseme_u") if x in lower)
        arkit_hits = sum(1 for x in ("eyeblinkleft", "eyeblinkright", "jawopen", "mouthsmileleft", "mouthsmileright") if x in lower)
        require(viseme_hits >= 5, "Oculus-style viseme set detected")
        require(arkit_hits >= 3, "ARKit-style expression set detected")

    material_names = [str(x.get("name", "")) for x in materials]
    receipt = {
        "schema": "luhm-os.character-donor-receipt.v2",
        "path": str(args.path),
        "profile": profile,
        "gitBlobSha1": actual_blob,
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
        "license": str(args.license),
        "embeddedLicense": embedded_license,
        "counts": {
            "meshes": len(meshes), "materials": len(materials), "textures": len(textures),
            "images": len(images), "skins": len(skins), "nodes": len(nodes),
            "animations": len(animations), "morphTargets": morph_targets,
            "jointNodes": len(all_joints), "expressionNames": len(expression_names),
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

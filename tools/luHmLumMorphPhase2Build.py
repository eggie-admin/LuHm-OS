#!/usr/bin/env python3
"""Build a reversible Lum GLB candidate from pinned donor, with no binary publication."""
import copy
import hashlib
import json
import os
import struct
import sys
import zipfile
from pathlib import Path
import numpy as np

BUNDLE_SHA = "fedaf37220d5f9477560fdc0b5624d30e95191db989f5b8428ca4d1a19b1d3da"
BASE_SHA = "06bdfcc196e147c4cb92c7c5489110a8feb30ee8a8f362fac585802eced33b69"
CANDIDATE_SHA = "4b8d41393bb94affe469af551c2915d6b39890cd2add18048d78da8610505a1e"

def need(ok, why):
    if not ok:
        raise RuntimeError("RED_LUM_MORPH: " + why)

def digest(blob):
    return hashlib.sha256(blob).hexdigest()

def readGlb(data):
    magic, version, glen = struct.unpack_from("<4sII", data)
    need(magic == b"glTF" and version == 2 and glen == len(data), "glbHeader")
    jsonSize, jsonKind = struct.unpack_from("<I4s", data, 12)
    need(jsonKind == b"JSON", "jsonChunk")
    scene = json.loads(data[20:20 + jsonSize])
    off = 20 + jsonSize
    binSize, binKind = struct.unpack_from("<I4s", data, off)
    need(binKind == b"BIN\x00", "binChunk")
    binary = data[off + 8:off + 8 + binSize]
    need(len(binary) == binSize, "binSize")
    return scene, binary

def accessor(scene, binary, idx):
    item = scene["accessors"][idx]
    view = scene["bufferViews"][item["bufferView"]]
    need("byteStride" not in view, "interleavedAccessor")
    kind = {5126: "<f4", 5123: "<u2", 5121: "u1", 5125: "<u4"}[item["componentType"]]
    width = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}[item["type"]]
    offset = view.get("byteOffset", 0) + item.get("byteOffset", 0)
    return np.frombuffer(binary, dtype=kind, count=item["count"] * width, offset=offset).reshape(item["count"], width).copy()

def smooth(a, b, v):
    t = np.clip((v - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)

def gauss(v, mu, sig):
    return np.exp(-0.5 * ((v - mu) / sig) ** 2)

def normals(pos, idx):
    tri = pos[idx]
    face = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    n = np.zeros_like(pos, dtype="float64")
    for corner in range(3):
        np.add.at(n, idx[:, corner], face)
    lengths = np.linalg.norm(n, axis=1)
    lengths[lengths == 0] = 1
    return (n / lengths[:, None]).astype("<f4")

def main(donor):
    source = Path(donor).read_bytes()
    need(digest(source) == BUNDLE_SHA, "donorBundleHash")
    with zipfile.ZipFile(Path(donor)) as z:
        matches = [n for n in z.namelist() if n.endswith("_Character_output.glb")]
        need(len(matches) == 1, "donorSelection")
        original = z.read(matches[0])
    need(digest(original) == BASE_SHA, "originalGlbHash")
    scene, oldBinary = readGlb(original)
    need(len(scene.get("skins", [])) == 1 and len(scene["skins"][0]["joints"]) == 24, "rigCount")
    need(len(scene.get("animations", [])) == 1, "animationCount")
    need(len(scene.get("meshes", [])) == 1 and len(scene["meshes"][0]["primitives"]) == 1, "meshCount")
    primitive = scene["meshes"][0]["primitives"][0]
    need("targets" not in primitive, "existingTargets")
    pos = accessor(scene, oldBinary, primitive["attributes"]["POSITION"]).astype("<f4")
    idx = accessor(scene, oldBinary, primitive["indices"]).ravel().astype("int32").reshape(-1, 3)
    need(len(pos) == 38432, "vertexCount")
    x, y, z = pos.T
    center = 1 - smooth(0.22, 0.37, np.abs(x))
    nearBody = smooth(0.035, 0.08, np.abs(x))
    hip = np.zeros_like(pos)
    hip[:, 0] = 0.061 * np.sign(x) * gauss(y, 0.91, 0.148) * center * nearBody
    waist = np.zeros_like(pos)
    waist[:, 0] = -0.041 * np.sign(x) * gauss(y, 1.113, 0.087) * (1 - smooth(.19, .27, np.abs(x))) * nearBody
    smile = np.zeros_like(pos)
    corner = gauss(np.abs(x), .078, .032) * gauss(y, 1.475, .047) * smooth(.075, .15, z)
    smile[:, 1] = .014 * corner
    smile[:, 0] = .004 * np.sign(x) * corner
    targets = {"hip_width": hip.astype("<f4"), "waist_shape": waist.astype("<f4"), "smile": smile.astype("<f4")}
    resultScene = copy.deepcopy(scene)
    binary = bytearray(oldBinary)
    baseNormals = normals(pos, idx)
    names = []
    counts = {}
    for name, delta in targets.items():
        moved = int(np.count_nonzero(np.linalg.norm(delta, axis=1) > 1e-5))
        need(moved > 15 and np.isfinite(delta).all(), "invalidGeometry:" + name)
        counts[name] = moved
        attrs = {}
        for attr, value in [("POSITION", delta), ("NORMAL", normals(pos + delta, idx) - baseNormals)]:
            while len(binary) % 4:
                binary.append(0)
            offset = len(binary)
            blob = value.astype("<f4").tobytes(order="C")
            binary.extend(blob)
            view = len(resultScene["bufferViews"])
            resultScene["bufferViews"].append({"buffer": 0, "byteOffset": offset, "byteLength": len(blob)})
            item = {"bufferView": view, "componentType": 5126, "count": len(pos), "type": "VEC3"}
            if attr == "POSITION":
                item["min"] = delta.min(axis=0).astype(float).tolist()
                item["max"] = delta.max(axis=0).astype(float).tolist()
            attrs[attr] = len(resultScene["accessors"])
            resultScene["accessors"].append(item)
        resultScene["meshes"][0]["primitives"][0].setdefault("targets", []).append(attrs)
        names.append(name)
    resultScene["meshes"][0]["weights"] = [0.0] * len(names)
    resultScene["meshes"][0].setdefault("extras", {})["targetNames"] = names
    resultScene["buffers"][0]["byteLength"] = len(binary)
    jblob = json.dumps(resultScene, ensure_ascii=False, separators=(",", ":")).encode("utf8")
    jblob += b" " * (-len(jblob) % 4)
    binary += b"\0" * (-len(binary) % 4)
    size = 12 + 8 + len(jblob) + 8 + len(binary)
    candidate = (struct.pack("<4sII", b"glTF", 2, size) + struct.pack("<I4s", len(jblob), b"JSON") + jblob + struct.pack("<I4s", len(binary), b"BIN\0") + binary)
    newScene, newBinary = readGlb(candidate)
    need(newBinary[:len(oldBinary)] == oldBinary and newScene["skins"] == scene["skins"], "sourceOrSkinChanged")
    need(newScene["nodes"] == scene["nodes"] and newScene["animations"] == scene["animations"], "nodesOrAnimationsChanged")
    need(newScene["meshes"][0]["weights"] == [0.0, 0.0, 0.0], "nonzeroDefaultMorph")
    need(np.array_equal(accessor(newScene, newBinary, primitive["attributes"]["POSITION"]), pos), "baseGeometryChanged")
    for i, name in enumerate(names):
        mapped = newScene["meshes"][0]["primitives"][0]["targets"][i]["POSITION"]
        need(np.array_equal(accessor(newScene, newBinary, mapped), targets[name]), "morphRoundTrip:" + name)
    need(digest(candidate) == CANDIDATE_SHA, "candidateBinaryDrift")
    out = Path(os.environ.get("LUM_PHASE2_OUT", "/tmp/luHmLumPhase2"))
    out.mkdir(parents=True, exist_ok=True)
    (out / "lumMorphPhase2Candidate.glb").write_bytes(candidate)
    receipt = {"schema": "luhmOs.lumMorphPhase2CiCandidate.v1", "state": "GEOMETRY_ONLY_CANDIDATE", "sourceSha256": BUNDLE_SHA, "baseSha256": BASE_SHA, "candidateSha256": digest(candidate), "skeletonJoints": 24, "animationCount": 1, "movedVertices": counts, "originalBytesPreserved": True, "defaultMorphWeightsZero": True, "godotRuntime": "NOT_YET_TESTED", "crown": "STOP", "redistribution": "NOT_APPROVED"}
    (out / "geometryReceipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print("LUM_MORPH_PHASE2_GEOMETRY_GREEN " + digest(candidate))

if __name__ == "__main__":
    need(len(sys.argv) == 2, "usage: source.zip")
    main(sys.argv[1])

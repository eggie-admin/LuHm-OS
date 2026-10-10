#!/usr/bin/env python3
"""Fail-closed source/binary audit for the LuHm Drive-to-Library-to-Godot bridge."""
import argparse
import hashlib
import json
import struct
import zipfile
from pathlib import Path

rootPath = Path(__file__).resolve().parents[1]
bridgePath = rootPath / "doctrine" / "godotDriveLibraryHandoffV1.json"
buildPath = rootPath / "tools" / "buildGodotWebHarness.sh"

def need(testValue, label):
    if not testValue:
        raise SystemExit("RED_GODOT_DRIVE_BRIDGE: " + label)

def inspectBundle(asset, bundlePath):
    data = bundlePath.read_bytes()
    need(len(data) <= 64 * 1024 * 1024, "bundleSize")
    need(hashlib.sha256(data).hexdigest() == asset["bundleSha256"], "bundleDigest")
    with zipfile.ZipFile(bundlePath) as archive:
        names = archive.namelist()
        expected = {member["path"] for member in asset["members"]}
        need(len(names) == len(set(names)) and set(names) == expected, "zipInventory")
        for name in names:
            parts = Path(name).parts
            need(bool(parts) and not name.startswith("/") and ".." not in parts and "\\" not in name, "zipPath")
        for member in asset["members"]:
            blob = archive.read(member["path"])
            need(hashlib.sha256(blob).hexdigest() == member["sha256"], "memberDigest:" + member["role"])
            need(len(blob) >= 20, "glbTooShort")
            magic, version, length = struct.unpack_from("<4sII", blob, 0)
            need(magic == b"glTF" and version == 2 and length == len(blob), "glbHeader")
            jsonSize, jsonType = struct.unpack_from("<I4s", blob, 12)
            need(jsonType == b"JSON" and 20 + jsonSize <= len(blob), "glbJsonChunk")
            scene = json.loads(blob[20:20 + jsonSize])
            skins = scene.get("skins", [])
            need(len(skins) >= 1 and len(skins[0].get("joints", [])) == member["skeletonJoints"], "skinJoints")
            animations = [animation.get("name") for animation in scene.get("animations", [])]
            need(animations == member["animations"], "glbAnimation")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, help="Optional locally staged private ZIP for binary verification")
    args = parser.parse_args()
    bridge = json.loads(bridgePath.read_text(encoding="utf-8"))
    need(bridge["schema"] == "luhmOs.godotDriveLibraryHandoff.v1", "schema")
    need(bridge["safety"]["noPublicDriveIds"] and bridge["safety"]["libraryNotGameServer"], "policy")
    need(not any(word in bridgePath.read_text(encoding="utf-8") for word in ("driveFileId", "drive.google.com/file/d/", "oauthToken")), "privateIdLeak")
    asset = bridge["asset"]
    need(asset["rightsState"] == "PROVENANCE_AND_REDISTRIBUTION_REVIEW_PENDING", "rightsOverclaim")
    buildText = buildPath.read_text(encoding="utf-8")
    need("BUNDLE_SHA='" + asset["bundleSha256"] + "'" in buildText, "bundleSourcePin")
    need("BASE_SHA='" + asset["members"][0]["sha256"] + "'" in buildText, "characterSourcePin")
    need("RUN_SHA='" + asset["members"][1]["sha256"] + "'" in buildText, "runningSourcePin")
    need(buildText.index('echo "$BUNDLE_SHA  $BUNDLE" | sha256sum -c -') < buildText.index('unzip -q "$BUNDLE"'), "verifyBeforeExtract")
    if args.bundle is not None:
        inspectBundle(asset, args.bundle)
        print("GODOT_DRIVE_BRIDGE_GREEN_BINARY_AND_SOURCE")
    else:
        print("GODOT_DRIVE_BRIDGE_GREEN_SOURCE_PINS_ONLY")
if __name__ == "__main__":
    main()

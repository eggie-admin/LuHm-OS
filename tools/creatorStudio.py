#!/usr/bin/env python3
"""LuHm-OS local-only Creator Studio. No network, AI execution, or autonomous CAST."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DDL = ROOT / "host/api/creatorStudioV1.sql"
CAMEL = re.compile(r"^[a-z][A-Za-z0-9]{0,79}$")
SHA = re.compile(r"^[0-9a-f]{40}$")
HEX = re.compile(r"^[0-9a-f]{6}$")
KINDS = {"socialHub", "exploration", "dungeon", "cutscene"}
INTENTS = {"banter", "bond", "quest", "route", "combat", "ambient", "cutscene", "system"}
STATUSES = {"proceduralPlaceholder", "rightsReviewed", "importVerified"}

class StudioError(ValueError):
    pass

def require(condition, message):
    if not condition:
        raise StudioError(message)

def name(value, context):
    require(isinstance(value, str) and bool(CAMEL.fullmatch(value)), "invalid camelHump " + context)
    return value

def _rows(value, context, maximum):
    require(isinstance(value, list) and 1 <= len(value) <= maximum, "invalid " + context)
    return value

def validateWorld(world):
    require(type(world) is dict, "world must be JSON object")
    require(world.get("schema") == "luhmOs.creatorStudioWorld.v1", "unknown schema")
    require(world.get("product") == "LuHm-OS", "product identity mismatch")
    require(world.get("status") == "PROPOSED_PRIVATE_SOURCE", "not a draft source")
    worldId = name(world.get("worldId"), "worldId")
    require(0 < len(str(world.get("displayName", ""))) <= 160, "bad world displayName")
    assets = world.get("assetPolicy")
    require(type(assets) is dict and assets.get("thirdPartyDataAllowed") is False and assets.get("autoPublish") is False, "unsafe asset policy")
    scenes = {}
    for scene in _rows(world.get("scenes"), "scenes", 32):
        require(type(scene) is dict, "invalid scene")
        sceneId = name(scene.get("sceneId"), "sceneId")
        require(sceneId not in scenes, "duplicate sceneId")
        require(scene.get("kind") in KINDS, "unknown scene kind")
        require(0 < len(str(scene.get("displayName", ""))) <= 160, "bad scene label")
        pal = scene.get("palette")
        require(type(pal) is dict and all(type(pal.get(k)) is str and HEX.fullmatch(pal[k]) for k in ("sky", "floor", "light")), "bad scene palette")
        require(type(scene.get("camera")) is list and len(scene["camera"]) == 3 and all(type(v) in (int, float) and -50 <= v <= 50 for v in scene["camera"]), "bad camera")
        name(scene.get("spawnDialogueId"), "spawnDialogueId")
        scenes[sceneId] = scene
    for scene in scenes.values():
        require(name(scene.get("destination"), "destination") in scenes, "unknown scene destination")
    characters = {}
    for row in _rows(world.get("characters"), "characters", 32):
        require(type(row) is dict, "invalid character")
        characterId = name(row.get("characterId"), "characterId")
        require(characterId not in characters, "duplicate character")
        name(row.get("role"), "role")
        require(row.get("currentArt") in STATUSES and type(row.get("approvedRig")) is bool, "bad character proof")
        require(row["currentArt"] != "importVerified" or row["approvedRig"] is True, "unproven rig claim")
        characters[characterId] = row
    dialogue = {}
    for row in _rows(world.get("dialogue"), "dialogue", 256):
        require(type(row) is dict, "invalid dialogue")
        lineId = name(row.get("lineId"), "lineId")
        require(lineId not in dialogue, "duplicate dialogue line")
        require(row.get("sceneId") in scenes and row.get("speakerId") in characters, "dialogue points outside known scene/character")
        require(row.get("intentTag") in INTENTS, "unknown intentTag")
        require(type(row.get("text")) is str and 1 <= len(row["text"]) <= 1000, "dialogue length")
        choices = _rows(row.get("choices"), "choices", 8)
        seen = set()
        for c in choices:
            require(type(c) is dict, "invalid choice")
            choiceId = name(c.get("choiceId"), "choiceId")
            require(choiceId not in seen, "duplicate choiceId in line")
            seen.add(choiceId)
            require(type(c.get("label")) is str and 1 <= len(c["label"]) <= 120, "bad choice label")
            name(c.get("nextLineId"), "nextLineId")
        dialogue[lineId] = row
    for row in dialogue.values():
        for choice in row["choices"]:
            target = dialogue.get(choice["nextLineId"])
            require(target is not None and target["sceneId"] == row["sceneId"], "choice leads to missing/cross-scene line")
    for scene in scenes.values():
        start = dialogue.get(scene["spawnDialogueId"])
        require(start is not None and start["sceneId"] == scene["sceneId"], "scene spawn dialogue invalid")
    morph = world.get("morphStudio", {})
    require(type(morph) is dict and morph.get("outfitConform") == "NOT_IMPLEMENTED", "false outfit conform proof")
    orchestra = world.get("orchestration", {})
    require(type(orchestra) is dict and orchestra.get("productAuthority") == "LuHm-OS" and orchestra.get("supervisor") == "lum", "orchestra identity mismatch")
    require(orchestra.get("liveWorkerState") == "QUARANTINED" and orchestra.get("sqlPromotionFromSuggestion") is False, "worker quarantine cannot be bypassed")
    release = world.get("release", {})
    require(type(release) is dict and release.get("cast") == "STOP" and release.get("androidInstalled") is False and release.get("sqlServerOnline") is False, "release authority mismatch")
    return {"worldId": worldId, "scenes": len(scenes), "characters": len(characters), "dialogueLines": len(dialogue), "status": "VALIDATED_SOURCE_ONLY"}

def readWorld(path):
    raw = Path(path).read_bytes()
    require(len(raw) <= 1024 * 1024, "world JSON exceeds 1 MiB")
    world = json.loads(raw.decode("utf-8"))
    validateWorld(world)
    return world

def connect(dbPath):
    path = Path(dbPath)
    if str(path) == ":memory:":
        db = sqlite3.connect(":memory:")
    else:
        require(path.suffix in (".sqlite", ".db"), "local .sqlite/.db required")
        path.parent.mkdir(parents=True, exist_ok=True)
        db = sqlite3.connect(path)
    db.execute("PRAGMA foreign_keys=ON")
    db.execute("PRAGMA busy_timeout=3000")
    db.executescript(DDL.read_text(encoding="utf-8"))
    return db

def importWorld(db, world, sourceRef):
    require(type(sourceRef) is str and SHA.fullmatch(sourceRef), "exact 40-character sourceRef required")
    meta = validateWorld(world)
    packed = json.dumps(world, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    digest = hashlib.sha256(packed.encode("utf-8")).hexdigest()
    worldId = meta["worldId"]
    with db:
        # REPLACE applies to this one locally selected world. Cascading deletes remain atomic.
        db.execute("INSERT OR REPLACE INTO studioWorld(worldId,product,displayName,status,sourceRef,contentHash,worldJson,updatedAt) VALUES(?,?,?,?,?,?,?,datetime('now'))",
                   (worldId, "LuHm-OS", world["displayName"], "draft", sourceRef, digest, packed))
        for s in world["scenes"]:
            db.execute("INSERT INTO studioScene VALUES(?,?,?,?,?,?,?)",
                       (worldId, s["sceneId"], s["displayName"], s["kind"], json.dumps(s["palette"], sort_keys=True), s["spawnDialogueId"], s["destination"]))
        for c in world["characters"]:
            db.execute("INSERT INTO studioCharacter VALUES(?,?,?,?,?)",
                       (worldId, c["characterId"], c["role"], c["currentArt"], int(c["approvedRig"])))
        for d in world["dialogue"]:
            db.execute("INSERT INTO studioDialogue VALUES(?,?,?,?,?,?,?)",
                       (worldId, d["lineId"], d["sceneId"], d["speakerId"], d["intentTag"], d["text"], json.dumps(d["choices"], sort_keys=True)))
    return {"worldId": worldId, "sha256": digest, "sourceRef": sourceRef, **meta, "promoted": False}

def listWorlds(db):
    return [dict(row) for row in db.execute("SELECT worldId,displayName,status,sourceRef,contentHash FROM studioWorld ORDER BY worldId")]

def exportWorld(db, worldId, destination):
    name(worldId, "worldId")
    row = db.execute("SELECT worldJson,contentHash FROM studioWorld WHERE worldId=?", (worldId,)).fetchone()
    require(row is not None, "world not found")
    original = json.loads(row["worldJson"])
    validateWorld(original)
    packed = json.dumps(original, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    require(hashlib.sha256(packed.encode("utf-8")).hexdigest() == row["contentHash"], "world hash mismatch")
    dest = Path(destination)
    require(not dest.exists(), "export will not overwrite an existing file")
    require(dest.suffix.lower() == ".json", "JSON export only")
    dest.write_text(json.dumps(original, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"worldId": worldId, "output": str(dest), "sha256": row["contentHash"], "promoted": False}

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    val = sub.add_parser("validate")
    val.add_argument("input")
    imp = sub.add_parser("importWorld")
    imp.add_argument("input")
    imp.add_argument("--db", required=True)
    imp.add_argument("--source-ref", required=True)
    ls = sub.add_parser("listWorlds")
    ls.add_argument("--db", required=True)
    exp = sub.add_parser("exportWorld")
    exp.add_argument("worldId")
    exp.add_argument("output")
    exp.add_argument("--db", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "validate":
            result = validateWorld(readWorld(args.input))
        else:
            with connect(args.db) as db:
                db.row_factory = sqlite3.Row
                if args.command == "importWorld":
                    result = importWorld(db, readWorld(args.input), args.source_ref)
                elif args.command == "listWorlds":
                    result = listWorlds(db)
                else:
                    result = exportWorld(db, args.worldId, args.output)
        print(json.dumps(result, indent=2))
        return 0
    except (StudioError, ValueError, OSError, sqlite3.Error) as exc:
        print(json.dumps({"status": "BLOCKED", "reason": str(exc)}))
        return 1

if __name__ == "__main__":
    raise SystemExit(main())

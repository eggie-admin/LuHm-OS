extends Node
## Canon 3D asset runtime gate. Never fetches files or upgrades art approval.
## Approved assets are packaged locally by CI; private candidates stay out of public builds.

const REGISTRY_PATH := "res://game/assets/canonRuntimeAssetsV1.json"
const CANON_PATH := "res://game/canon/CHARACTER_CANON_V1.json"
const APPROVED_PREFIX := "res://assets/approved3d/"
const ALLOWED_WORLDS := ["neonRiverwalk", "lumCoffeeHouse", "cathedral"]
const LICENSES := ["originalApproved", "redistributionApproved"]

var registry: Dictionary = {}
var last_receipt: Dictionary = {}

func _ready() -> void:
    registry = _read_json(REGISTRY_PATH)
    last_receipt = {"state": "REGISTRY_READY" if not registry.is_empty() else "REGISTRY_UNAVAILABLE",
        "canonPromoted": false, "publicArtPublished": false}

func character_model_status(character_id: String) -> Dictionary:
    var canon := _read_json(CANON_PATH)
    var canonical = canon.get("characters", {})
    if not canonical is Dictionary or not canonical.has(character_id):
        return _blocked("characterNotInCanon", character_id)
    var characters = registry.get("characters", {})
    if not characters is Dictionary or not characters.has(character_id):
        return _blocked("characterNotInRegistry", character_id)
    return _resolve_entry(characters[character_id], character_id)

func mount_world_props(world_id: String, world_root: Node3D) -> Dictionary:
    if not ALLOWED_WORLDS.has(world_id) or world_root == null:
        last_receipt = {"worldId": world_id, "status": "BLOCKED", "reason": "unknownWorldOrRoot",
            "mounted": 0, "canonPromoted": false}
        return last_receipt.duplicate(true)
    var worlds = registry.get("worlds", {})
    if not worlds is Dictionary or not worlds.has(world_id):
        last_receipt = {"worldId": world_id, "status": "BLOCKED", "reason": "worldNotInRegistry",
            "mounted": 0, "canonPromoted": false}
        return last_receipt.duplicate(true)
    var entries = worlds[world_id]
    if not entries is Array or entries.size() > 24:
        last_receipt = {"worldId": world_id, "status": "BLOCKED", "reason": "invalidWorldAssets",
            "mounted": 0, "canonPromoted": false}
        return last_receipt.duplicate(true)

    var mounted := 0
    var blockers: Array[String] = []
    for raw in entries:
        if not raw is Dictionary:
            blockers.append("invalidEntry")
            continue
        var asset_id := String(raw.get("id", ""))
        var decision := _resolve_entry(raw, asset_id)
        if not bool(decision.get("ok", false)):
            blockers.append("%s:%s" % [asset_id, decision.get("reason", "blocked")])
            continue
        var scene = load(String(decision.get("path", "")))
        if not scene is PackedScene:
            blockers.append("%s:unloadableScene" % asset_id)
            continue
        var instance = (scene as PackedScene).instantiate()
        if not instance is Node3D:
            instance.free()
            blockers.append("%s:notNode3D" % asset_id)
            continue
        instance.name = "CanonProp_%s" % asset_id
        world_root.add_child(instance)
        mounted += 1
    last_receipt = {"schema": "luhmOs.canon3dMountReceipt.v1", "worldId": world_id,
        "status": "PROCEDURAL_FALLBACK" if entries.is_empty() else ("MOUNTED" if blockers.is_empty() else "PARTIAL_BLOCKED"),
        "mounted": mounted, "blockers": blockers, "canonPromoted": false,
        "publicArtPublished": false}
    return last_receipt.duplicate(true)

func get_last_receipt() -> Dictionary:
    return last_receipt.duplicate(true)

func _resolve_entry(raw, asset_id: String) -> Dictionary:
    if not raw is Dictionary or asset_id.is_empty():
        return _blocked("invalidEntry", asset_id)
    if String(raw.get("status", "")) != "runtimeImportProven":
        return _blocked("assetNotPromoted", asset_id)
    if not bool(raw.get("publicAllowed", false)) or not bool(raw.get("importProven", false)):
        return _blocked("publicOrImportGateClosed", asset_id)
    if String(raw.get("approvedBy", "")) != "Professor" or not LICENSES.has(String(raw.get("license", ""))):
        return _blocked("rightsOrApprovalMissing", asset_id)
    var expected_sha := String(raw.get("sha256", ""))
    if expected_sha.length() != 64 or not expected_sha.is_valid_hex_number():
        return _blocked("sha256Unpinned", asset_id)
    var path := String(raw.get("path", ""))
    if not _is_safe_path(path):
        return _blocked("unapprovedPath", asset_id)
    if not ResourceLoader.exists(path):
        return _blocked("assetMissingFromBuild", asset_id)
    return {"ok": true, "assetId": asset_id, "path": path, "sha256": expected_sha,
        "source": "packagedAndBuildAudited", "canonPromoted": false}

func _is_safe_path(path: String) -> bool:
    if not path.begins_with(APPROVED_PREFIX):
        return false
    if ".." in path or "\\" in path or "?" in path or "#" in path:
        return false
    return path.ends_with(".glb") or path.ends_with(".tscn")

func _blocked(reason: String, asset_id: String) -> Dictionary:
    return {"ok": false, "assetId": asset_id, "reason": reason,
        "fallback": "proceduralOrNotShown", "canonPromoted": false}

func _read_json(path: String) -> Dictionary:
    if not FileAccess.file_exists(path):
        return {}
    var file := FileAccess.open(path, FileAccess.READ)
    if file == null:
        return {}
    var value = JSON.parse_string(file.get_as_text())
    return value if value is Dictionary else {}

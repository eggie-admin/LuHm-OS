extends Node

const CONTRACT_PATH := "res://game/assets/GODDESS_COMPONENT_CONTRACT_V1.json"

var avatar_root: Node3D
var contract: Dictionary = {}
var mounted: Dictionary = {}
var last_receipt: Dictionary = {}

func configure(root_node: Node3D) -> void:
    avatar_root = root_node
    if contract.is_empty():
        contract = _load_contract()

func assemble_character(character_id: String) -> Dictionary:
    if avatar_root == null:
        return _receipt(character_id, {}, [], ["avatar_root"])
    if contract.is_empty():
        contract = _load_contract()

    var characters = contract.get("characters", {})
    if not characters is Dictionary or not characters.has(character_id):
        return _receipt(character_id, {}, [], ["character:%s" % character_id])

    var requested = characters.get(character_id, {})
    if not requested is Dictionary:
        return _receipt(character_id, {}, [], ["component_map:%s" % character_id])

    var slots = contract.get("slots", {})
    var applied: Dictionary = {}
    var missing: Array[String] = []
    var blockers: Array[String] = []

    for slot_name in slots:
        var slot_rule = slots.get(slot_name, {})
        if not slot_rule is Dictionary:
            continue
        var socket_name := String(slot_rule.get("socket", ""))
        var required := bool(slot_rule.get("required", false))
        var source = requested.get(slot_name, null)

        if source == null or String(source).is_empty():
            if required:
                blockers.append("%s:unassigned" % slot_name)
            else:
                missing.append("%s:unassigned" % slot_name)
            continue

        var result := mount_component(String(slot_name), socket_name, String(source))
        if bool(result.get("ok", false)):
            applied[String(slot_name)] = result
        elif required:
            blockers.append("%s:%s" % [slot_name, result.get("reason", "unknown")])
        else:
            missing.append("%s:%s" % [slot_name, result.get("reason", "unknown")])

    last_receipt = _receipt(character_id, applied, missing, blockers)
    return last_receipt.duplicate(true)

func mount_component(slot_name: String, socket_name: String, resource_path: String) -> Dictionary:
    if avatar_root == null:
        return {"ok": false, "reason": "avatar_root"}
    if not _path_allowed(resource_path):
        return {"ok": false, "reason": "path_not_allowed", "path": resource_path}

    var socket := avatar_root.find_child(socket_name, true, false) as Node3D
    if socket == null:
        return {"ok": false, "reason": "socket_missing", "socket": socket_name}
    if not ResourceLoader.exists(resource_path):
        return {"ok": false, "reason": "resource_missing", "path": resource_path}

    var packed = load(resource_path)
    if not packed is PackedScene:
        return {"ok": false, "reason": "not_packed_scene", "path": resource_path}

    _clear_socket(socket)
    var instance := (packed as PackedScene).instantiate()
    instance.name = "%sComponent" % slot_name
    socket.add_child(instance)
    mounted[slot_name] = instance

    return {
        "ok": true,
        "slot": slot_name,
        "socket": socket_name,
        "path": resource_path,
        "node": instance.name
    }

func unmount_component(slot_name: String) -> bool:
    if not mounted.has(slot_name):
        return false
    var node = mounted[slot_name]
    if node is Node and is_instance_valid(node):
        (node as Node).queue_free()
    mounted.erase(slot_name)
    return true

func get_last_receipt() -> Dictionary:
    return last_receipt.duplicate(true)

func _clear_socket(socket: Node3D) -> void:
    for child in socket.get_children():
        child.queue_free()

func _path_allowed(resource_path: String) -> bool:
    var law = contract.get("runtimeLaw", {})
    var prefixes = law.get("allowedAssetPrefixes", []) if law is Dictionary else []
    for prefix in prefixes:
        if resource_path.begins_with(String(prefix)):
            return true
    return false

func _receipt(character_id: String, applied: Dictionary, missing: Array, blockers: Array) -> Dictionary:
    return {
        "schema": "luhmOs.goddessComponentRuntimeReceipt.v1",
        "character": character_id,
        "applied": applied,
        "appliedCount": applied.size(),
        "missing": missing.duplicate(),
        "missingCount": missing.size(),
        "blockers": blockers.duplicate(),
        "blockerCount": blockers.size(),
        "canonPromoted": false,
        "crownAuthority": false
    }

func _load_contract() -> Dictionary:
    if not FileAccess.file_exists(CONTRACT_PATH):
        return {}
    var file := FileAccess.open(CONTRACT_PATH, FileAccess.READ)
    if file == null:
        return {}
    var parsed = JSON.parse_string(file.get_as_text())
    return parsed if parsed is Dictionary else {}

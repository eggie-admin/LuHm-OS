extends Node3D

const CANON_PATH := "res://game/canon/CHARACTER_CANON_V1.json"
var canon: Dictionary = {}
var active_character := "lum"

func _ready() -> void:
    canon = _load_json(CANON_PATH)

func character_ids() -> Array[String]:
    var out: Array[String] = []
    var characters = canon.get("characters", {})
    if characters is Dictionary:
        for key in characters.keys():
            out.append(String(key))
    return out

func set_active_character(character_id: String) -> bool:
    if character_id not in character_ids():
        return false
    active_character = character_id
    return true

func summary(character_id: String) -> Dictionary:
    var characters = canon.get("characters", {})
    if characters is Dictionary:
        var value = characters.get(character_id, {})
        if value is Dictionary:
            return value.duplicate(true)
    return {}

func _load_json(path: String) -> Dictionary:
    if not FileAccess.file_exists(path):
        return {}
    var file := FileAccess.open(path, FileAccess.READ)
    if file == null:
        return {}
    var parsed = JSON.parse_string(file.get_as_text())
    return parsed if parsed is Dictionary else {}

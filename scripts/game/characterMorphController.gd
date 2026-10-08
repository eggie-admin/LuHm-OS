extends Node

const PRESET_PATH := "res://game/assets/GODDESS_MORPH_PRESETS_V1.json"

var target_root: Node3D
var profile: Dictionary = {}
var last_receipt: Dictionary = {}

func configure(root_node: Node3D) -> void:
    target_root = root_node
    if profile.is_empty():
        profile = _load_profile()

func apply_preset(character_id: String) -> Dictionary:
    if target_root == null:
        return _receipt(character_id, {}, [], ["target_root"])
    if profile.is_empty():
        profile = _load_profile()

    var presets = profile.get("presets", {})
    if not presets is Dictionary or not presets.has(character_id):
        return _receipt(character_id, {}, [], ["preset:%s" % character_id])

    var preset = presets.get(character_id, {})
    var values = preset.get("values", {}) if preset is Dictionary else {}
    if not values is Dictionary:
        return _receipt(character_id, {}, [], ["values:%s" % character_id])

    return apply_values(character_id, values)

func apply_values(character_id: String, values: Dictionary) -> Dictionary:
    var sliders = profile.get("sliders", {})
    var applied: Dictionary = {}
    var missing: Array[String] = []

    for slider_name in values:
        var weight := clampf(float(values[slider_name]), 0.0, 1.0)
        var aliases: Array[String] = []
        if sliders is Dictionary:
            var raw_aliases = sliders.get(slider_name, [])
            if raw_aliases is Array:
                for alias in raw_aliases:
                    aliases.append(String(alias).to_lower())
        if aliases.is_empty():
            aliases.append(String(slider_name).to_lower())

        var hits := _apply_aliases(aliases, weight)
        if hits > 0:
            applied[String(slider_name)] = {
                "weight": weight,
                "targets": hits
            }
        else:
            missing.append(String(slider_name))

    last_receipt = _receipt(character_id, applied, missing, [])
    return last_receipt.duplicate(true)

func _apply_aliases(aliases: Array[String], weight: float) -> int:
    if target_root == null:
        return 0

    var hits := 0
    for node in target_root.find_children("*", "MeshInstance3D", true, false):
        var mesh_instance := node as MeshInstance3D
        if mesh_instance == null:
            continue
        var mesh := mesh_instance.mesh
        if mesh == null:
            continue

        for index in range(mesh.get_blend_shape_count()):
            var shape_name := String(mesh.get_blend_shape_name(index))
            if shape_name.to_lower() in aliases:
                mesh_instance.set_blend_shape_value(index, weight)
                hits += 1
    return hits

func available_preset_ids() -> Array[String]:
    if profile.is_empty():
        profile = _load_profile()
    var out: Array[String] = []
    var presets = profile.get("presets", {})
    if presets is Dictionary:
        for key in presets:
            out.append(String(key))
    return out

func reset_known_shapes() -> int:
    if target_root == null:
        return 0
    var hits := 0
    for node in target_root.find_children("*", "MeshInstance3D", true, false):
        var mesh_instance := node as MeshInstance3D
        if mesh_instance == null or mesh_instance.mesh == null:
            continue
        for index in range(mesh_instance.mesh.get_blend_shape_count()):
            mesh_instance.set_blend_shape_value(index, 0.0)
            hits += 1
    return hits

func get_last_receipt() -> Dictionary:
    return last_receipt.duplicate(true)

func _receipt(character_id: String, applied: Dictionary, missing: Array, blockers: Array) -> Dictionary:
    return {
        "schema": "luhmOs.goddessMorphRuntimeReceipt.v1",
        "character": character_id,
        "applied": applied,
        "appliedCount": applied.size(),
        "missing": missing.duplicate(),
        "missingCount": missing.size(),
        "blockers": blockers.duplicate(),
        "physicsApplied": false,
        "canonPromoted": false,
        "crownAuthority": false
    }

func _load_profile() -> Dictionary:
    if not FileAccess.file_exists(PRESET_PATH):
        return {}
    var file := FileAccess.open(PRESET_PATH, FileAccess.READ)
    if file == null:
        return {}
    var parsed = JSON.parse_string(file.get_as_text())
    return parsed if parsed is Dictionary else {}

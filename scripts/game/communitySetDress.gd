extends Node3D

# Final-form build-time staged community props.
# The immutable selection is fetched before Godot import. This runtime never downloads assets.
const MANIFEST_PATH := "res://assets/community/selected-assets.json"
const LAYOUT_PATH := "res://assets/community/final-form-layout.json"
const RUNTIME_ROOT := "res://assets/community/runtime"

var instance_count := 0
var loaded_unique_count := 0
var missing_count := 0
var expected_unique_count := 0
var _loaded_paths: Dictionary = {}

func _ready() -> void:
    name = "CommunityCathedralSetDress"

    var manifest_assets := _load_manifest_assets()
    expected_unique_count = manifest_assets.size()

    # Hero coffee-house placements win. Anything not used here is deterministically
    # auto-dressed into the skyline/service-alley so every approved current asset
    # participates at least once.
    for spec in _load_hero_specs():
        _place(spec)

    var group_slots: Dictionary = {}
    for entry in manifest_assets:
        var group := String(entry.get("group", ""))
        var asset_name := String(entry.get("name", ""))
        var path := _runtime_path(group, asset_name)
        var slot := int(group_slots.get(group, 0))
        group_slots[group] = slot + 1
        if _loaded_paths.has(path):
            continue
        _place(_auto_spec(group, asset_name, slot))

    loaded_unique_count = _loaded_paths.size()
    print(
        "COMMUNITY_SET_DRESS instances=%d unique=%d expected=%d missing=%d"
        % [instance_count, loaded_unique_count, expected_unique_count, missing_count]
    )

func _load_json(path: String) -> Dictionary:
    if not FileAccess.file_exists(path):
        return {}
    var parsed = JSON.parse_string(FileAccess.get_file_as_string(path))
    return parsed if parsed is Dictionary else {}

func _load_manifest_assets() -> Array:
    var document := _load_json(MANIFEST_PATH)
    var groups = document.get("groups", {})
    var assets: Array = []
    if not (groups is Dictionary):
        return assets
    for group_name in groups:
        var names = groups[group_name]
        if not (names is Array):
            continue
        for asset_name in names:
            assets.append({
                "group": String(group_name),
                "name": String(asset_name)
            })
    return assets

func _load_hero_specs() -> Array:
    var document := _load_json(LAYOUT_PATH)
    var specs: Array = []
    var placements = document.get("hero_placements", [])
    if not (placements is Array):
        return specs
    for placement in placements:
        if not (placement is Dictionary):
            continue
        var group := String(placement.get("group", ""))
        var asset_name := String(placement.get("name", ""))
        specs.append({
            "path": _runtime_path(group, asset_name),
            "pos": _vec3(placement.get("pos", [0.0, 0.0, 0.0])),
            "rot": float(placement.get("rot_y", 0.0)),
            "scale": float(placement.get("scale", 1.0))
        })
    return specs

func _runtime_path(group: String, asset_name: String) -> String:
    return "%s/%s/%s" % [RUNTIME_ROOT, group, asset_name]

func _auto_spec(group: String, asset_name: String, slot: int) -> Dictionary:
    var pos := Vector3.ZERO
    var rot := 0.0
    var uniform_scale := 1.0

    match group:
        "city-industrial":
            # Skyline ring outside the walk. Alternate sides and stagger depth.
            var side := -1.0 if slot % 2 == 0 else 1.0
            var lane := float(slot % 4)
            var row := int(slot / 2)
            pos = Vector3(side * (19.0 + lane * 2.6), 0.0, 19.0 - float(row) * 3.4)
            rot = 16.0 * side
            uniform_scale = 2.1
        "factory":
            # Rear service yard, safely behind the coffee-house hero volume.
            var column := slot % 8
            var row := int(slot / 8)
            pos = Vector3(-10.5 + float(column) * 3.0, 0.0, 23.0 + float(row) * 3.0)
            rot = -18.0 + float((slot * 23) % 37)
            uniform_scale = 1.15
        "furniture":
            # All furniture is expected in the hero layout. This is a fail-soft
            # deterministic fallback for future manifest growth.
            var column := slot % 5
            var row := int(slot / 5)
            pos = Vector3(-4.8 + float(column) * 2.4, 0.0, 10.4 + float(row) * 2.4)
            rot = float((slot * 29) % 360)
            uniform_scale = 1.15
        _:
            pos = Vector3(0.0, 0.0, 28.0 + float(slot) * 2.0)

    return {
        "path": _runtime_path(group, asset_name),
        "pos": pos,
        "rot": rot,
        "scale": uniform_scale
    }

func _place(spec: Dictionary) -> void:
    var path := String(spec.get("path", ""))
    if path.is_empty() or not ResourceLoader.exists(path):
        missing_count += 1
        return

    var resource = load(path)
    if not (resource is PackedScene):
        missing_count += 1
        return

    var instance := (resource as PackedScene).instantiate()
    if not (instance is Node3D):
        instance.queue_free()
        missing_count += 1
        return

    var node := instance as Node3D
    node.name = "Community_%s_%03d" % [path.get_file().get_basename(), instance_count]
    var position_value = spec.get("pos", Vector3.ZERO)
    node.position = position_value if position_value is Vector3 else Vector3.ZERO
    node.rotation_degrees.y = float(spec.get("rot", 0.0))
    var uniform_scale := float(spec.get("scale", 1.0))
    node.scale = Vector3.ONE * uniform_scale
    add_child(node)

    instance_count += 1
    _loaded_paths[path] = true

func _vec3(value) -> Vector3:
    if value is Array and value.size() >= 3:
        return Vector3(float(value[0]), float(value[1]), float(value[2]))
    return Vector3.ZERO

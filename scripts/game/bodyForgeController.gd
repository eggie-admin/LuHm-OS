extends Node

const BodyProportionModifierScript := preload("res://scripts/game/bodyProportionModifier.gd")
const SLIDER_KEYS := ["height", "head", "shoulders", "torso", "arms", "legs", "hips", "frame"]
const DEFAULT_VALUE := 0.5

var avatar: Node3D
var model_root: Node3D
var skeleton: Skeleton3D
var modifier: SkeletonModifier3D
var _values: Dictionary = {}

func _ready() -> void:
    for key in SLIDER_KEYS:
        _values[key] = DEFAULT_VALUE

func configure(target_avatar: Node3D) -> void:
    avatar = target_avatar
    model_root = avatar.get("model_root") as Node3D
    skeleton = avatar.get("skeleton") as Skeleton3D
    if skeleton != null:
        modifier = BodyProportionModifierScript.new()
        modifier.name = "BodyProportionModifier"
        skeleton.add_child(modifier)
        if avatar.has_method("get_canonical_bone_map"):
            modifier.call("configure", avatar.call("get_canonical_bone_map"))
    _apply_height()

func set_slider(key: String, normalized: float) -> bool:
    if key not in SLIDER_KEYS:
        return false
    var value := clampf(normalized, 0.0, 1.0)
    _values[key] = value
    if key == "height":
        _apply_height()
        return true
    if modifier != null:
        return bool(modifier.call("set_normalized", key, value))
    return false

func reset_profile() -> void:
    for key in SLIDER_KEYS:
        _values[key] = DEFAULT_VALUE
    _apply_height()
    if modifier != null:
        modifier.call("reset_profile")

func get_profile() -> Dictionary:
    return _values.duplicate(true)

func get_summary() -> Dictionary:
    var rig_summary: Dictionary = {}
    if avatar != null and avatar.has_method("get_rig_summary"):
        rig_summary = avatar.call("get_rig_summary")
    var morph_count := _count_blend_shapes()
    return {
        "schema": "luhm.avatar.creator.summary.v1",
        "mode": "runtime_non_destructive",
        "proportion_engine": "SkeletonModifier3D",
        "mesh_morph_targets": morph_count,
        "mesh_morph_policy": "optional_when_donor_provides_targets",
        "current_donor_body_morphs": "unavailable" if morph_count == 0 else "available",
        "supported_sliders": SLIDER_KEYS.duplicate(),
        "profile": get_profile(),
        "skeleton_bones": int(rig_summary.get("skeleton_bones", 0)),
        "canonical_mapped": int(rig_summary.get("canonical_mapped", 0)),
        "canonical_required": int(rig_summary.get("canonical_required", 0))
    }

func _apply_height() -> void:
    if model_root == null:
        return
    var height_scale := lerpf(0.88, 1.12, float(_values.get("height", DEFAULT_VALUE)))
    model_root.scale = Vector3(1.0, height_scale, 1.0)

func _count_blend_shapes() -> int:
    if model_root == null:
        return 0
    var count := 0
    for node in model_root.find_children("*", "MeshInstance3D", true, false):
        var mesh_instance := node as MeshInstance3D
        var array_mesh := mesh_instance.mesh as ArrayMesh
        if array_mesh != null:
            count += array_mesh.get_blend_shape_count()
    return count

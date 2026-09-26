extends SkeletonModifier3D

const KEYS := ["head", "shoulders", "torso", "arms", "legs", "hips", "frame"]
const DEFAULT_VALUE := 0.5

var _bone_map: Dictionary = {}
var _values: Dictionary = {}
var _indices: Dictionary = {}
var _base_scales: Dictionary = {}

func _ready() -> void:
    for key in KEYS:
        _values[key] = DEFAULT_VALUE

func configure(canonical_bones: Dictionary) -> void:
    _bone_map = canonical_bones.duplicate(true)
    _indices.clear()
    _base_scales.clear()

func set_normalized(key: String, value: float) -> bool:
    if key not in KEYS:
        return false
    _values[key] = clampf(value, 0.0, 1.0)
    return true

func reset_profile() -> void:
    for key in KEYS:
        _values[key] = DEFAULT_VALUE

func get_profile() -> Dictionary:
    return _values.duplicate(true)

func get_supported_keys() -> Array:
    return KEYS.duplicate()

func _process_modification_with_delta(_delta: float) -> void:
    var target := get_skeleton()
    if target == null:
        return
    _ensure_indices(target)

    var multipliers: Dictionary = {}

    var head_scale := _mapped_scale("head", 0.84, 1.16)
    _multiply(multipliers, "head", Vector3.ONE * head_scale)

    var shoulder_scale := _mapped_scale("shoulders", 0.88, 1.14)
    _multiply(multipliers, "left_shoulder", Vector3(shoulder_scale, 1.0, 1.0))
    _multiply(multipliers, "right_shoulder", Vector3(shoulder_scale, 1.0, 1.0))

    var torso_scale := _mapped_scale("torso", 0.92, 1.10)
    for semantic in ["spine", "chest", "upper_chest"]:
        _multiply(multipliers, semantic, Vector3(1.0, torso_scale, 1.0))

    var arm_scale := _mapped_scale("arms", 0.92, 1.08)
    for semantic in ["left_upper_arm", "left_lower_arm", "right_upper_arm", "right_lower_arm"]:
        _multiply(multipliers, semantic, Vector3.ONE * arm_scale)

    var leg_scale := _mapped_scale("legs", 0.92, 1.08)
    for semantic in ["left_upper_leg", "left_lower_leg", "right_upper_leg", "right_lower_leg"]:
        _multiply(multipliers, semantic, Vector3.ONE * leg_scale)

    var hip_scale := _mapped_scale("hips", 0.90, 1.12)
    _multiply(multipliers, "hips", Vector3(hip_scale, 1.0, 1.0))

    var frame_scale := _mapped_scale("frame", 0.90, 1.12)
    for semantic in ["spine", "chest", "upper_chest"]:
        _multiply(multipliers, semantic, Vector3(frame_scale, 1.0, frame_scale))

    for semantic in multipliers:
        _apply_semantic(target, String(semantic), multipliers[semantic])

func _mapped_scale(key: String, low: float, high: float) -> float:
    return lerpf(low, high, float(_values.get(key, DEFAULT_VALUE)))

func _ensure_indices(target: Skeleton3D) -> void:
    if not _indices.is_empty():
        return
    for semantic in _bone_map:
        var bone_name := String(_bone_map[semantic])
        var bone_index := target.find_bone(bone_name)
        _indices[String(semantic)] = bone_index
        if bone_index >= 0:
            _base_scales[String(semantic)] = target.get_bone_pose_scale(bone_index)

func _multiply(multipliers: Dictionary, semantic: String, scale_value: Vector3) -> void:
    var current: Vector3 = multipliers.get(semantic, Vector3.ONE)
    multipliers[semantic] = current * scale_value

func _apply_semantic(target: Skeleton3D, semantic: String, multiplier: Vector3) -> void:
    var bone_index := int(_indices.get(semantic, -1))
    if bone_index < 0:
        return
    var base_scale: Vector3 = _base_scales.get(semantic, Vector3.ONE)
    target.set_bone_pose_scale(bone_index, base_scale * multiplier)

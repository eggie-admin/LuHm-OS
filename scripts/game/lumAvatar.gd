extends Node3D

const ASSET_PATH := "res://assets/lum/luhm.glb"
const RUN_ASSET_PATH := "res://assets/lum/luhmRunning.glb"
const BONE_MAP_PATH := "res://assets/lum/lumBoneMap.json"

var model_root: Node3D
var animation_player: AnimationPlayer
var animation_tree: AnimationTree
var skeleton: Skeleton3D
var look_target: Node3D
var external_model_loaded := false
var _home_scale := Vector3.ONE
var _home_y := 0.0
var _pulse_tween: Tween
var _idle_clock := 0.0

var _canonical_required: Dictionary = {}
var _canonical_missing: Array[String] = []
var _animation_states: Dictionary = {}
var _head_look: LookAtModifier3D
var _eye_look_left: LookAtModifier3D
var _eye_look_right: LookAtModifier3D
var _eye_tracking_mode := "unavailable"

func _ready() -> void:
    _home_scale = scale
    _home_y = position.y
    animation_tree = get_node_or_null("AnimationTree") as AnimationTree
    look_target = get_node_or_null("LookTarget") as Node3D
    _load_bone_map()
    _load_model_or_fallback()
    _set_default_look_target()

func _process(delta: float) -> void:
    _idle_clock += delta
    position.y = _home_y + sin(_idle_clock * 1.15) * 0.035

func _load_bone_map() -> void:
    _canonical_required.clear()
    if not FileAccess.file_exists(BONE_MAP_PATH):
        return
    var file := FileAccess.open(BONE_MAP_PATH, FileAccess.READ)
    if file == null:
        return
    var parsed = JSON.parse_string(file.get_as_text())
    if parsed is Dictionary:
        var required = parsed.get("required", {})
        if required is Dictionary:
            _canonical_required = required.duplicate(true)

func _load_model_or_fallback() -> void:
    external_model_loaded = false
    if ResourceLoader.exists(ASSET_PATH):
        var packed := load(ASSET_PATH)
        if packed is PackedScene:
            model_root = packed.instantiate()
            model_root.name = "LumModel"
            add_child(model_root)
            _normalize_imported_model()
            _bind_imported_runtime()
            _validate_canonical_bones()
            _build_animation_tree()
            _install_look_tracking()
            external_model_loaded = true
            _start_neutral_state()
            return
    _build_procedural_lum()

func _normalize_imported_model() -> void:
    if model_root == null:
        return
    model_root.scale = Vector3.ONE
    model_root.position = Vector3.ZERO

func _bind_imported_runtime() -> void:
    animation_player = model_root.find_child("AnimationPlayer", true, false) as AnimationPlayer
    if animation_player == null:
        var players := model_root.find_children("*", "AnimationPlayer", true, false)
        if not players.is_empty():
            animation_player = players[0] as AnimationPlayer

    var skeletons := model_root.find_children("*", "Skeleton3D", true, false)
    if not skeletons.is_empty():
        skeleton = skeletons[0] as Skeleton3D

func _validate_canonical_bones() -> void:
    _canonical_missing.clear()
    if skeleton == null:
        for semantic in _canonical_required:
            _canonical_missing.append(String(semantic))
        return
    for semantic in _canonical_required:
        var bone_name := String(_canonical_required[semantic])
        if skeleton.find_bone(bone_name) < 0:
            _canonical_missing.append(String(semantic))

func _build_animation_tree() -> void:
    _animation_states.clear()
    if animation_tree == null or animation_player == null:
        return

    var state_machine := AnimationNodeStateMachine.new()
    var names := animation_player.get_animation_list()
    var state_index := 0
    for animation_name in names:
        var node := AnimationNodeAnimation.new()
        node.animation = animation_name
        var state_name := _state_name_for_animation(String(animation_name), state_index)
        state_machine.add_node(state_name, node, Vector2(float(state_index) * 180.0, 0.0))
        _animation_states[String(animation_name).to_lower()] = state_name
        state_index += 1

    if state_index == 0:
        animation_tree.active = false
        return

    animation_tree.tree_root = state_machine
    animation_tree.anim_player = animation_tree.get_path_to(animation_player)
    animation_tree.active = true

func _state_name_for_animation(animation_name: String, index: int) -> StringName:
    var lowered := animation_name.to_lower()
    if lowered.contains("idle") or lowered.contains("clip0") or lowered == "reset":
        return &"Idle"
    if lowered.contains("run"):
        return &"Run"
    if lowered.contains("walk"):
        return &"Walk"
    return StringName("Clip_%02d" % index)

func _start_neutral_state() -> void:
    if animation_tree != null and animation_tree.active:
        var playback := animation_tree.get("parameters/playback") as AnimationNodeStateMachinePlayback
        if playback != null:
            for animation_key in _animation_states:
                var lowered := String(animation_key)
                if lowered.contains("idle") or lowered.contains("clip0") or lowered == "reset":
                    playback.start(_animation_states[animation_key], true)
                    return
            if not _animation_states.is_empty():
                playback.start(_animation_states.values()[0], true)
                return
    _apply_neutral_pose_direct()

func _apply_neutral_pose_direct() -> void:
    if animation_player == null:
        return
    var names := animation_player.get_animation_list()
    for name in names:
        var lowered := String(name).to_lower()
        if lowered.contains("clip0") or lowered.contains("idle") or lowered == "reset":
            animation_player.play(name)
            animation_player.seek(0.0, true)
            animation_player.pause()
            return

func _install_look_tracking() -> void:
    _eye_tracking_mode = "unavailable"
    if skeleton == null or look_target == null:
        return

    var head_bone := _find_bone_alias(["Head", "head"])
    if not head_bone.is_empty():
        _head_look = _make_look_modifier("HeadLook", head_bone, 55.0, 35.0, 0.14)

    var left_eye := _find_bone_alias(["Eye_L", "LeftEye", "eye.L", "eye_l"])
    var right_eye := _find_bone_alias(["Eye_R", "RightEye", "eye.R", "eye_r"])
    if not left_eye.is_empty() and not right_eye.is_empty():
        _eye_look_left = _make_look_modifier("EyeLookLeft", left_eye, 28.0, 18.0, 0.08)
        _eye_look_right = _make_look_modifier("EyeLookRight", right_eye, 28.0, 18.0, 0.08)
        _eye_tracking_mode = "bone_pair"
    elif _head_look != null:
        _eye_tracking_mode = "head_fallback"

func _make_look_modifier(node_name: String, bone_name: String, primary_degrees: float, secondary_degrees: float, duration_seconds: float) -> LookAtModifier3D:
    var modifier := LookAtModifier3D.new()
    modifier.name = node_name
    modifier.bone_name = bone_name
    modifier.relative = true
    modifier.use_angle_limitation = true
    modifier.symmetry_limitation = true
    modifier.primary_limit_angle = deg_to_rad(primary_degrees)
    modifier.secondary_limit_angle = deg_to_rad(secondary_degrees)
    modifier.duration = duration_seconds
    skeleton.add_child(modifier)
    modifier.target_node = modifier.get_path_to(look_target)
    return modifier

func _find_bone_alias(aliases: Array) -> String:
    if skeleton == null:
        return ""
    for alias in aliases:
        var candidate := String(alias)
        if skeleton.find_bone(candidate) >= 0:
            return candidate
    return ""

func _set_default_look_target() -> void:
    if look_target == null:
        return
    look_target.global_position = global_position + Vector3(0.0, 1.8, -4.0)

func set_look_target_world(world_position: Vector3) -> void:
    if look_target != null:
        look_target.global_position = world_position

func uses_external_model() -> bool:
    return external_model_loaded

func get_canonical_bone_map() -> Dictionary:
    return _canonical_required.duplicate(true)

func get_rig_summary() -> Dictionary:
    var names: Array[String] = []
    if animation_player != null:
        for animation_name in animation_player.get_animation_list():
            names.append(String(animation_name))
    return {
        "external": external_model_loaded,
        "skeleton_bones": skeleton.get_bone_count() if skeleton != null else 0,
        "animations": names.size(),
        "animation_names": names,
        "running_asset_present": ResourceLoader.exists(RUN_ASSET_PATH),
        "canonical_required": _canonical_required.size(),
        "canonical_mapped": _canonical_required.size() - _canonical_missing.size(),
        "canonical_missing": _canonical_missing.duplicate(),
        "animation_tree_active": animation_tree != null and animation_tree.active,
        "animation_tree_states": _animation_states.size(),
        "head_tracking": _head_look != null,
        "eye_tracking": _eye_look_left != null and _eye_look_right != null,
        "eye_tracking_mode": _eye_tracking_mode
    }

func play_motion_hint(token: String) -> bool:
    if animation_player == null:
        return false
    var needle := token.to_lower()

    if animation_tree != null and animation_tree.active:
        var playback := animation_tree.get("parameters/playback") as AnimationNodeStateMachinePlayback
        if playback != null:
            for animation_key in _animation_states:
                if String(animation_key).contains(needle):
                    playback.start(_animation_states[animation_key], true)
                    return true

    for animation_name in animation_player.get_animation_list():
        if String(animation_name).to_lower().contains(needle):
            animation_player.play(animation_name)
            return true
    return false

func _build_procedural_lum() -> void:
    external_model_loaded = false
    animation_player = null
    skeleton = null
    _canonical_missing.clear()
    _animation_states.clear()
    _eye_tracking_mode = "unavailable"
    if animation_tree != null:
        animation_tree.active = false

    model_root = Node3D.new()
    model_root.name = "LumFallback"
    add_child(model_root)

    var dark := _material(Color("16101d"), 0.45, 0.36)
    var pale := _material(Color("f0dce9"), 0.0, 0.72)
    var pink := _material(Color("ff4f9f"), 0.15, 0.3, Color("ff3b98"), 2.8)

    var body := MeshInstance3D.new()
    var body_mesh := CapsuleMesh.new()
    body_mesh.radius = 0.52
    body_mesh.height = 1.65
    body.mesh = body_mesh
    body.position = Vector3(0.0, 1.0, 0.0)
    body.material_override = dark
    model_root.add_child(body)

    var head := MeshInstance3D.new()
    var head_mesh := SphereMesh.new()
    head_mesh.radius = 0.48
    head_mesh.height = 0.96
    head.mesh = head_mesh
    head.position = Vector3(0.0, 2.12, 0.0)
    head.material_override = pale
    model_root.add_child(head)

    for side in [-1.0, 1.0]:
        var horn := MeshInstance3D.new()
        var horn_mesh := CylinderMesh.new()
        horn_mesh.top_radius = 0.035
        horn_mesh.bottom_radius = 0.14
        horn_mesh.height = 0.58
        horn.mesh = horn_mesh
        horn.position = Vector3(0.28 * side, 2.63, 0.0)
        horn.rotation_degrees.z = -18.0 * side
        horn.material_override = dark
        model_root.add_child(horn)

        var eye := MeshInstance3D.new()
        var eye_mesh := SphereMesh.new()
        eye_mesh.radius = 0.055
        eye_mesh.height = 0.11
        eye.mesh = eye_mesh
        eye.position = Vector3(0.16 * side, 2.16, -0.43)
        eye.material_override = pink
        model_root.add_child(eye)

    var core := MeshInstance3D.new()
    var core_mesh := SphereMesh.new()
    core_mesh.radius = 0.16
    core_mesh.height = 0.32
    core.mesh = core_mesh
    core.position = Vector3(0.0, 1.22, -0.5)
    core.material_override = pink
    model_root.add_child(core)

func pulse(duration: float) -> void:
    _kill_pulse_tween()
    var half := maxf(duration * 0.5, 0.06)
    _pulse_tween = create_tween()
    _pulse_tween.set_trans(Tween.TRANS_SINE)
    _pulse_tween.set_ease(Tween.EASE_IN_OUT)
    _pulse_tween.tween_property(self, "scale", _home_scale * 1.16, half)
    _pulse_tween.tween_property(self, "scale", _home_scale, half)

func restore_visual_state() -> void:
    _kill_pulse_tween()
    scale = _home_scale
    set_expression("neutral", 0.0)
    _start_neutral_state()

func set_expression(expression_name: String, weight: float = 1.0) -> void:
    if model_root == null:
        return
    var aliases := _expression_aliases(expression_name)
    if expression_name.to_lower() == "neutral":
        weight = 0.0
        aliases = ["neutral", "smile", "happy", "joy", "blink", "blink_l", "blink_r", "eye_blink", "aa", "a", "mouth_open", "jawopen"]
    for node in model_root.find_children("*", "MeshInstance3D", true, false):
        var mesh_instance := node as MeshInstance3D
        var array_mesh := mesh_instance.mesh as ArrayMesh
        if array_mesh == null:
            continue
        for index in range(array_mesh.get_blend_shape_count()):
            var shape_name := str(array_mesh.get_blend_shape_name(index))
            if shape_name.to_lower() in aliases:
                mesh_instance.set("blend_shapes/%s" % shape_name, clampf(weight, 0.0, 1.0))

func _expression_aliases(expression_name: String) -> Array[String]:
    match expression_name.to_lower():
        "smile":
            return ["smile", "happy", "joy"]
        "blink":
            return ["blink", "blink_l", "blink_r", "eye_blink"]
        "talk":
            return ["aa", "a", "mouth_open", "jawopen"]
        _:
            return ["neutral"]

func _material(color: Color, metallic: float, roughness: float, emission: Color = Color(0, 0, 0, 1), emission_energy: float = 0.0) -> StandardMaterial3D:
    var mat := StandardMaterial3D.new()
    mat.albedo_color = color
    mat.metallic = metallic
    mat.roughness = roughness
    if emission_energy > 0.0:
        mat.emission_enabled = true
        mat.emission = emission
        mat.emission_energy_multiplier = emission_energy
    return mat

func _kill_pulse_tween() -> void:
    if _pulse_tween != null and _pulse_tween.is_valid():
        _pulse_tween.kill()
    _pulse_tween = null

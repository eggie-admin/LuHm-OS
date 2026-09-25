extends Node3D

const ASSET_PATH := "res://assets/lum/luhm.glb"

var model_root: Node3D
var animation_player: AnimationPlayer
var _home_scale := Vector3.ONE
var _home_y := 0.0
var _pulse_tween: Tween
var _idle_clock := 0.0

func _ready() -> void:
    _home_scale = scale
    _home_y = position.y
    _load_model_or_fallback()

func _process(delta: float) -> void:
    _idle_clock += delta
    position.y = _home_y + sin(_idle_clock * 1.15) * 0.035

func _load_model_or_fallback() -> void:
    if ResourceLoader.exists(ASSET_PATH):
        var packed := load(ASSET_PATH)
        if packed is PackedScene:
            model_root = packed.instantiate()
            model_root.name = "LumModel"
            add_child(model_root)
            _normalize_imported_model()
            animation_player = model_root.find_child("AnimationPlayer", true, false) as AnimationPlayer
            _play_idle_if_available()
            return
    _build_procedural_lum()

func _normalize_imported_model() -> void:
    if model_root == null:
        return
    model_root.scale = Vector3.ONE
    model_root.position = Vector3.ZERO

func _play_idle_if_available() -> void:
    if animation_player == null:
        return
    for candidate in ["idleBreath", "Idle", "idle", "RESET"]:
        if animation_player.has_animation(candidate):
            if candidate != "RESET":
                animation_player.play(candidate)
            return

func _build_procedural_lum() -> void:
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

func set_expression(expression_name: String, weight: float = 1.0) -> void:
    if model_root == null:
        return
    var aliases := _expression_aliases(expression_name)
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

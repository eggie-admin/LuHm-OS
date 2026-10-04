extends Node3D

var oni_name := "UNKNOWN"
var target: Node3D
var accent := Color("b783ff")
var _clock := 0.0
var _lifetime := 8.0
var _visual_root: Node3D

func configure(name_value: String, target_value: Node3D) -> void:
    oni_name = name_value.strip_edges().left(32)
    if oni_name.is_empty():
        oni_name = "UNKNOWN"
    target = target_value
    accent = _accent_for(oni_name)

func _ready() -> void:
    _build_visual()

func _process(delta: float) -> void:
    _clock += delta
    if target == null or not is_instance_valid(target):
        queue_free()
        return
    var angle := _clock * 1.9
    var desired := target.global_position + Vector3(cos(angle) * 1.15, 1.45 + sin(_clock * 2.8) * 0.12, sin(angle) * 1.15)
    global_position = global_position.lerp(desired, minf(delta * 7.5, 1.0))
    if _visual_root != null:
        _visual_root.rotation.y += delta * 2.2
    if _clock >= _lifetime:
        queue_free()

func _build_visual() -> void:
    _visual_root = Node3D.new()
    _visual_root.name = "OniEchoCompanionVisual"
    add_child(_visual_root)

    var core := MeshInstance3D.new()
    var core_mesh := SphereMesh.new()
    core_mesh.radius = 0.13
    core_mesh.height = 0.26
    core.mesh = core_mesh
    core.material_override = _emissive(accent, 4.4)
    _visual_root.add_child(core)

    var halo := MeshInstance3D.new()
    var halo_mesh := TorusMesh.new()
    halo_mesh.inner_radius = 0.20
    halo_mesh.outer_radius = 0.25
    halo.mesh = halo_mesh
    halo.rotation_degrees.x = 90.0
    halo.material_override = _emissive(accent.lightened(0.12), 3.2)
    _visual_root.add_child(halo)

func _accent_for(name_value: String) -> Color:
    var palette := [
        Color("5ee7ff"),
        Color("b783ff"),
        Color("ff6e86"),
        Color("73ef9f"),
        Color("ffd36c")
    ]
    var total := 0
    for i in range(name_value.length()):
        total += name_value.unicode_at(i)
    return palette[total % palette.size()]

func _emissive(color: Color, energy: float) -> StandardMaterial3D:
    var material := StandardMaterial3D.new()
    material.albedo_color = color.darkened(0.42)
    material.emission_enabled = true
    material.emission = color
    material.emission_energy_multiplier = energy
    material.metallic = 0.22
    material.roughness = 0.28
    return material

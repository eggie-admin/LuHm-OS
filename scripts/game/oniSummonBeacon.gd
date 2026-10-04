extends Node3D

var oni_name := "UNKNOWN"
var accent := Color("b783ff")
var _clock := 0.0
var _lifetime := 3.2
var _visual_root: Node3D

func configure(name_value: String) -> void:
    oni_name = name_value.strip_edges().left(32)
    if oni_name.is_empty():
        oni_name = "UNKNOWN"
    accent = _accent_for(oni_name)

func _ready() -> void:
    _build_visual()

func _process(delta: float) -> void:
    _clock += delta
    if _visual_root != null:
        _visual_root.rotation.y += delta * 1.8
        _visual_root.position.y = 0.18 + sin(_clock * 3.2) * 0.12
        var pulse := 0.92 + sin(_clock * 6.0) * 0.08
        _visual_root.scale = Vector3.ONE * pulse
    if _clock >= _lifetime:
        queue_free()

func _build_visual() -> void:
    _visual_root = Node3D.new()
    _visual_root.name = "OniBeaconVisual"
    add_child(_visual_root)

    var core := MeshInstance3D.new()
    var core_mesh := SphereMesh.new()
    core_mesh.radius = 0.18
    core_mesh.height = 0.36
    core.mesh = core_mesh
    core.position.y = 1.0
    core.material_override = _emissive(accent, 5.2)
    _visual_root.add_child(core)

    for i in range(3):
        var ring := MeshInstance3D.new()
        var ring_mesh := TorusMesh.new()
        ring_mesh.inner_radius = 0.24 + float(i) * 0.11
        ring_mesh.outer_radius = 0.29 + float(i) * 0.11
        ring.mesh = ring_mesh
        ring.position.y = 1.0 + float(i - 1) * 0.16
        ring.rotation_degrees = Vector3(90.0 if i != 1 else 0.0, float(i) * 60.0, 0.0)
        ring.material_override = _emissive(accent, 3.6 - float(i) * 0.4)
        _visual_root.add_child(ring)

    for side in [-1.0, 1.0]:
        var horn := MeshInstance3D.new()
        var horn_mesh := CylinderMesh.new()
        horn_mesh.top_radius = 0.02
        horn_mesh.bottom_radius = 0.08
        horn_mesh.height = 0.34
        horn.mesh = horn_mesh
        horn.position = Vector3(0.16 * side, 1.28, 0.0)
        horn.rotation_degrees.z = 28.0 * side
        horn.material_override = _emissive(accent.lightened(0.18), 4.0)
        _visual_root.add_child(horn)

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
    material.albedo_color = color.darkened(0.4)
    material.emission_enabled = true
    material.emission = color
    material.emission_energy_multiplier = energy
    material.metallic = 0.28
    material.roughness = 0.24
    return material

extends Area3D

var interaction_id := ""
var event_name := ""
var prompt := "INTERACT"
var accent := Color("55dfff")
var _visual_root: Node3D
var _clock := 0.0
var _home_y := 0.0

func configure(id_value: String, event_value: String, prompt_value: String, accent_value: Color) -> void:
    interaction_id = id_value
    event_name = event_value
    prompt = prompt_value
    accent = accent_value

func _ready() -> void:
    collision_layer = 0
    collision_mask = 0
    monitoring = false
    monitorable = false
    _home_y = position.y
    _build_marker()

func _process(delta: float) -> void:
    if _visual_root == null or not _visual_root.visible:
        return
    _clock += delta
    _visual_root.rotation.y += delta * 0.8
    _visual_root.position.y = sin(_clock * 2.2) * 0.08

func get_event_name() -> String:
    return event_name

func get_prompt() -> String:
    return prompt

func get_interaction_id() -> String:
    return interaction_id

func set_active(active: bool) -> void:
    if _visual_root != null:
        _visual_root.visible = active

func _build_marker() -> void:
    if _visual_root != null:
        return
    _visual_root = Node3D.new()
    _visual_root.name = "InteractionMarker"
    add_child(_visual_root)

    match event_name:
        "collectSignalShard":
            _build_signal_shard()
        "collectCoffee":
            _build_coffee()
        "clearStaticWisp":
            _build_static_wisp()
        _:
            _build_gate_or_objective_marker()

func _build_signal_shard() -> void:
    var shard := MeshInstance3D.new()
    var mesh := BoxMesh.new()
    mesh.size = Vector3(0.24, 1.15, 0.24)
    shard.mesh = mesh
    shard.rotation_degrees = Vector3(18.0, 45.0, 18.0)
    shard.position.y = 0.75
    shard.material_override = _emissive(accent, 4.0)
    _visual_root.add_child(shard)
    _add_halo(0.18, 0.34, 0.2)

func _build_coffee() -> void:
    var cup := MeshInstance3D.new()
    var mesh := CylinderMesh.new()
    mesh.top_radius = 0.26
    mesh.bottom_radius = 0.22
    mesh.height = 0.52
    cup.mesh = mesh
    cup.position.y = 0.48
    cup.material_override = _emissive(accent, 1.8)
    _visual_root.add_child(cup)

    var handle := MeshInstance3D.new()
    var handle_mesh := TorusMesh.new()
    handle_mesh.inner_radius = 0.10
    handle_mesh.outer_radius = 0.16
    handle.mesh = handle_mesh
    handle.position = Vector3(0.27, 0.5, 0.0)
    handle.rotation_degrees.y = 90.0
    handle.material_override = _emissive(accent, 1.8)
    _visual_root.add_child(handle)
    _add_halo(0.24, 0.38, 0.12)

func _build_static_wisp() -> void:
    for i in range(3):
        var orb := MeshInstance3D.new()
        var mesh := SphereMesh.new()
        mesh.radius = 0.22 - float(i) * 0.035
        mesh.height = mesh.radius * 2.0
        orb.mesh = mesh
        var angle := TAU * float(i) / 3.0
        orb.position = Vector3(cos(angle) * 0.34, 0.9 + float(i) * 0.12, sin(angle) * 0.34)
        orb.material_override = _emissive(accent, 4.8 - float(i) * 0.6)
        _visual_root.add_child(orb)
    _add_halo(0.38, 0.58, 0.15)

func _build_gate_or_objective_marker() -> void:
    var stem := MeshInstance3D.new()
    var stem_mesh := CylinderMesh.new()
    stem_mesh.top_radius = 0.035
    stem_mesh.bottom_radius = 0.035
    stem_mesh.height = 1.2
    stem.mesh = stem_mesh
    stem.position.y = 0.6
    stem.material_override = _emissive(accent, 2.6)
    _visual_root.add_child(stem)
    _add_halo(0.22, 0.34, 0.0)

func _add_halo(inner_radius: float, outer_radius: float, y_offset: float) -> void:
    var halo := MeshInstance3D.new()
    var halo_mesh := TorusMesh.new()
    halo_mesh.inner_radius = inner_radius
    halo_mesh.outer_radius = outer_radius
    halo.mesh = halo_mesh
    halo.rotation_degrees.x = 90.0
    halo.position.y = 1.3 + y_offset
    halo.material_override = _emissive(accent, 3.4)
    _visual_root.add_child(halo)

func _emissive(color: Color, energy: float) -> StandardMaterial3D:
    var material := StandardMaterial3D.new()
    material.albedo_color = color.darkened(0.45)
    material.emission_enabled = true
    material.emission = color
    material.emission_energy_multiplier = energy
    material.metallic = 0.22
    material.roughness = 0.36
    return material

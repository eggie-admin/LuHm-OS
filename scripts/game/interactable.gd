extends Area3D

var interaction_id := ""
var event_name := ""
var prompt := "INTERACT"
var accent := Color("55dfff")
var _visual_root: Node3D

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
    _build_marker()

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

    var stem := MeshInstance3D.new()
    var stem_mesh := CylinderMesh.new()
    stem_mesh.top_radius = 0.035
    stem_mesh.bottom_radius = 0.035
    stem_mesh.height = 1.2
    stem.mesh = stem_mesh
    stem.position.y = 0.6
    stem.material_override = _emissive(accent, 2.6)
    _visual_root.add_child(stem)

    var halo := MeshInstance3D.new()
    var halo_mesh := TorusMesh.new()
    halo_mesh.inner_radius = 0.22
    halo_mesh.outer_radius = 0.34
    halo.mesh = halo_mesh
    halo.rotation_degrees.x = 90.0
    halo.position.y = 1.3
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

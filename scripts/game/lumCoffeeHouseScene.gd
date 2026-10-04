extends Node3D

const LumAvatarScene := preload("res://scenes/LumAvatar.tscn")
const InteractableScript := preload("res://scripts/game/interactable.gd")

var player_spawn := Vector3(0.0, 1.15, 6.5)
var lum_avatar: Node3D
var interaction_points: Array[Area3D] = []

func _ready() -> void:
    _build_room()
    _build_bar()
    _build_seating()
    _build_lum_corner()
    _build_interactions()

func _build_room() -> void:
    var environment := WorldEnvironment.new()
    var settings := Environment.new()
    settings.background_mode = Environment.BG_COLOR
    settings.background_color = Color("120d10")
    settings.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
    settings.ambient_light_color = Color("d19a72")
    settings.ambient_light_energy = 0.48
    environment.environment = settings
    add_child(environment)
    _box("CoffeeHouseFloor", Vector3(0, -0.25, 0), Vector3(18, 0.5, 22), Color("241916"), true)
    _box("BackWall", Vector3(0, 2.5, -10.5), Vector3(18, 5, 0.35), Color("211419"), true)
    _box("LeftWall", Vector3(-8.8, 2.5, 0), Vector3(0.35, 5, 21), Color("1b1518"), true)
    _box("RightWall", Vector3(8.8, 2.5, 0), Vector3(0.35, 5, 21), Color("1b1518"), true)

func _build_bar() -> void:
    _box("CoffeeBar", Vector3(-5.8, 0.7, -3.5), Vector3(1.2, 1.4, 9.0), Color("351c19"), true)
    _box("CoffeeBarTop", Vector3(-5.45, 1.45, -3.5), Vector3(1.9, 0.14, 9.2), Color("6a3827"), true)
    for z in [-6.2, -3.5, -0.8]:
        _box("BarStool%s" % int(z * 10), Vector3(-3.8, 0.45, z), Vector3(0.7, 0.9, 0.7), Color("29191d"), true)

func _build_seating() -> void:
    for z in [-5.5, 0.0, 5.0]:
        _box("Table%s" % int(z * 10), Vector3(3.8, 0.65, z), Vector3(2.3, 0.18, 1.5), Color("4a2b20"), true)
        _box("SeatL%s" % int(z * 10), Vector3(2.3, 0.45, z), Vector3(0.9, 0.9, 1.3), Color("211a22"), true)
        _box("SeatR%s" % int(z * 10), Vector3(5.3, 0.45, z), Vector3(0.9, 0.9, 1.3), Color("211a22"), true)

func _build_lum_corner() -> void:
    _box("LumCornerStage", Vector3(3.8, 0.18, -7.8), Vector3(4.4, 0.36, 3.2), Color("20151e"), true)
    lum_avatar = LumAvatarScene.instantiate() as Node3D
    lum_avatar.name = "LumAvatarSocket"
    lum_avatar.position = Vector3(3.8, 0.55, -7.8)
    add_child(lum_avatar)
    var lamp := OmniLight3D.new()
    lamp.name = "LumCoffeeLamp"
    lamp.position = Vector3(3.8, 3.0, -7.8)
    lamp.light_color = Color("f3b47c")
    lamp.light_energy = 2.2
    lamp.omni_range = 7.0
    add_child(lamp)

func get_lum_focus_position() -> Vector3:
    return lum_avatar.global_position + Vector3(0, 1.65, 0)

func pulse_lum(duration: float) -> void:
    if lum_avatar != null: lum_avatar.pulse(duration)

func restore_lum() -> void:
    if lum_avatar != null: lum_avatar.restore_visual_state()

func set_lum_expression(expression_name: String, weight: float = 1.0) -> void:
    if lum_avatar != null: lum_avatar.set_expression(expression_name, weight)

func set_lum_look_target(world_position: Vector3) -> void:
    if lum_avatar != null and lum_avatar.has_method("set_look_target_world"):
        lum_avatar.call("set_look_target_world", world_position)

func _box(name_value: String, pos: Vector3, size: Vector3, color: Color, collidable: bool) -> Node3D:
    var root_node: Node3D
    if collidable:
        var body := StaticBody3D.new()
        root_node = body
        var collision := CollisionShape3D.new()
        var shape := BoxShape3D.new()
        shape.size = size
        collision.shape = shape
        body.add_child(collision)
    else:
        root_node = Node3D.new()
    root_node.name = name_value
    root_node.position = pos
    add_child(root_node)
    var mesh_instance := MeshInstance3D.new()
    var mesh := BoxMesh.new()
    mesh.size = size
    mesh_instance.mesh = mesh
    var material := StandardMaterial3D.new()
    material.albedo_color = color
    material.metallic = 0.12
    material.roughness = 0.72
    mesh_instance.material_override = material
    root_node.add_child(mesh_instance)
    return root_node


func _build_interactions() -> void:
    _add_interaction("collectCoffee", "collectCoffee", "Take the coffee", Vector3(-4.25, 1.55, -3.5), Color("f3b47c"))
    _add_interaction("gateRiverwalk", "travel:neonRiverwalk", "Return to Riverwalk", Vector3(0.0, 0.35, 8.5), Color("55dfff"))
    _add_interaction("gateCathedral", "travel:cathedral", "Enter Cathedral gate", Vector3(7.0, 0.35, 7.5), Color("b76cff"))

func _add_interaction(interaction_id: String, event_name: String, prompt: String, pos: Vector3, accent: Color) -> void:
    var node := InteractableScript.new() as Area3D
    node.name = interaction_id
    node.position = pos
    node.configure(interaction_id, event_name, prompt, accent)
    add_child(node)
    interaction_points.append(node)

func get_interaction_points() -> Array[Area3D]:
    return interaction_points.duplicate()

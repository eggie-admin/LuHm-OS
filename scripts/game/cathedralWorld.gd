extends Node3D

const LumAvatarScene := preload("res://scenes/LumAvatar.tscn")

var player_spawn := Vector3(0.0, 1.15, 12.0)
var lum_avatar: Node3D

func _ready() -> void:
    _build_environment()
    _build_nave()
    _build_altar()
    _build_side_aisles()
    _build_quest_nook()
    _build_transition_anchors()
    _build_lum_focus()

func _build_environment() -> void:
    var environment := WorldEnvironment.new()
    environment.name = "CathedralEnvironment"
    var settings := Environment.new()
    settings.background_mode = Environment.BG_COLOR
    settings.background_color = Color("07070b")
    settings.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
    settings.ambient_light_color = Color("4c4568")
    settings.ambient_light_energy = 0.42
    settings.fog_enabled = true
    settings.fog_light_color = Color("211b2d")
    settings.fog_density = 0.018
    environment.environment = settings
    add_child(environment)

func _build_nave() -> void:
    _box("CathedralFloor", Vector3(0, -0.25, 0), Vector3(20, 0.5, 34), Color("15141a"), true)
    _box("BackWall", Vector3(0, 5, -16.5), Vector3(20, 10, 0.5), Color("111017"), true)
    _box("LeftWall", Vector3(-9.75, 5, 0), Vector3(0.5, 10, 33), Color("111017"), true)
    _box("RightWall", Vector3(9.75, 5, 0), Vector3(0.5, 10, 33), Color("111017"), true)
    for z in [-11.0, -5.0, 1.0, 7.0]:
        _column(Vector3(-6.2, 2.5, z))
        _column(Vector3(6.2, 2.5, z))
    for z in [-8.0, -2.0, 4.0, 10.0]:
        _box("NaveBenchL%s" % int(z), Vector3(-3.2, 0.45, z), Vector3(4.4, 0.9, 1.0), Color("33231e"), true)
        _box("NaveBenchR%s" % int(z), Vector3(3.2, 0.45, z), Vector3(4.4, 0.9, 1.0), Color("33231e"), true)

func _build_altar() -> void:
    _box("AltarDais", Vector3(0, 0.25, -13.0), Vector3(9.0, 0.5, 5.5), Color("211923"), true)
    _box("Altar", Vector3(0, 1.0, -14.0), Vector3(4.0, 1.5, 1.4), Color("4a3b36"), true)
    _box("RoseWindow", Vector3(0, 6.5, -16.15), Vector3(5.2, 5.2, 0.18), Color("4b244e"), false)
    var altar_light := OmniLight3D.new()
    altar_light.name = "AltarLight"
    altar_light.position = Vector3(0, 5.5, -12.5)
    altar_light.light_color = Color("b76cff")
    altar_light.light_energy = 3.2
    altar_light.omni_range = 12.0
    add_child(altar_light)

func _build_side_aisles() -> void:
    _box("LeftAisle", Vector3(-7.6, 0.02, 0), Vector3(3.0, 0.08, 29.0), Color("19151d"), false)
    _box("RightAisle", Vector3(7.6, 0.02, 0), Vector3(3.0, 0.08, 29.0), Color("19151d"), false)

func _build_quest_nook() -> void:
    _box("QuestNook", Vector3(-7.5, 0.35, -10.5), Vector3(3.5, 0.7, 4.0), Color("20171c"), true)
    _box("QuestLectern", Vector3(-7.5, 1.1, -11.0), Vector3(1.0, 1.5, 0.8), Color("4a2d24"), true)

func _build_transition_anchors() -> void:
    var riverwalk := Marker3D.new()
    riverwalk.name = "riverwalkDoor"
    riverwalk.position = Vector3(0, 0, 15.5)
    add_child(riverwalk)
    var coffee_house := Marker3D.new()
    coffee_house.name = "coffeeHouseDoor"
    coffee_house.position = Vector3(8.4, 0, 10.0)
    add_child(coffee_house)
    var encounter := Marker3D.new()
    encounter.name = "encounterAnchor"
    encounter.position = Vector3(0, 0, -6.0)
    add_child(encounter)

func _build_lum_focus() -> void:
    lum_avatar = LumAvatarScene.instantiate() as Node3D
    lum_avatar.name = "LumAvatarSocket"
    lum_avatar.position = Vector3(0, 0.55, -11.7)
    add_child(lum_avatar)

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

func _column(pos: Vector3) -> void:
    _box("Column%s%s" % [int(pos.x), int(pos.z)], pos, Vector3(0.8, 5.0, 0.8), Color("292630"), true)

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
    material.metallic = 0.18
    material.roughness = 0.68
    mesh_instance.material_override = material
    root_node.add_child(mesh_instance)
    return root_node

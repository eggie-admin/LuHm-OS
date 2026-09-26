extends Node3D

const LumAvatarScene := preload("res://scenes/LumAvatar.tscn")

var player_spawn := Vector3(0.0, 1.15, 0.5)
var lum_avatar: Node3D
var _neon_materials: Array[StandardMaterial3D] = []

func _ready() -> void:
    _build_environment()
    _build_riverwalk()
    _build_city()
    _build_lum_stage()
    _build_noir_details()

func _build_environment() -> void:
    var env_node := WorldEnvironment.new()
    env_node.name = "WorldEnvironment"
    var env := Environment.new()
    env.background_mode = Environment.BG_COLOR
    env.background_color = Color("070711")
    env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
    env.ambient_light_color = Color("79999f")
    env.ambient_light_energy = 0.85
    env.fog_enabled = true
    env.fog_light_color = Color("102330")
    env.fog_density = 0.008
    env_node.environment = env
    add_child(env_node)

    var moon := DirectionalLight3D.new()
    moon.name = "MoonLight"
    moon.light_color = Color("9ab8ff")
    moon.light_energy = 0.92
    moon.rotation_degrees = Vector3(-52.0, -28.0, 0.0)
    moon.shadow_enabled = true
    add_child(moon)

func _build_riverwalk() -> void:
    _box("WalkFloor", Vector3(0.0, -0.25, 0.0), Vector3(26.0, 0.5, 62.0), Color("11101a"), true)
    _box("River", Vector3(0.0, -0.52, -25.0), Vector3(58.0, 0.12, 18.0), Color("0b2840"), false, Color("0b3150"), 0.8)

    _box("LeftBoundary", Vector3(-13.0, 1.0, 0.0), Vector3(0.35, 2.0, 62.0), Color("17121f"), true)
    _box("RightBoundary", Vector3(13.0, 1.0, 0.0), Vector3(0.35, 2.0, 62.0), Color("17121f"), true)

    var cyan := Color("5fe7ff")
    for x in range(-12, 13, 3):
        _box("RailPost_%s" % x, Vector3(float(x), 0.55, -15.0), Vector3(0.12, 1.1, 0.12), Color("10131a"), true, cyan, 3.0)
    _box("RiverRail", Vector3(0.0, 1.0, -15.0), Vector3(25.0, 0.12, 0.12), Color("10131a"), true, cyan, 2.5)

    for z in [-10.0, -2.0, 6.0, 14.0]:
        _neon_strip(Vector3(-5.8, 0.04, z), Vector3(4.2, 0.04, 0.18), Color("ff3c9d"))
        _neon_strip(Vector3(5.8, 0.04, z - 2.0), Vector3(4.2, 0.04, 0.18), Color("55dfff"))

func _build_city() -> void:
    var heights := [6.0, 9.0, 13.0, 7.0, 15.0, 10.0, 8.0, 12.0, 6.5, 11.0, 14.0, 8.5]
    for i in range(heights.size()):
        var side := -1.0 if i % 2 == 0 else 1.0
        var lane := float(i % 3)
        var h: float = heights[i]
        var z: float = 10.0 - floor(float(i) / 2.0) * 7.2
        var x: float = side * (16.0 + lane * 3.8)
        _box(
            "CityBlock_%02d" % i,
            Vector3(x, h * 0.5, z),
            Vector3(5.0, h, 5.0),
            Color("15111f") if i % 2 == 0 else Color("101a24"),
            true
        )
        _window_stack(Vector3(x - side * 2.52, 1.6, z), h, Color("ff3c9d") if i % 2 == 0 else Color("55dfff"), side)

    _arch(Vector3(0.0, 0.0, -6.5))
    # Keep the foreground clear of overhead neon clipping the portrait view.

    var accent := OmniLight3D.new()
    accent.name = "RiverwalkAccent"
    accent.position = Vector3(0.0, 5.0, -8.0)
    accent.light_color = Color("ff3c9d")
    accent.light_energy = 3.4
    accent.omni_range = 14.0
    add_child(accent)

func _build_lum_stage() -> void:
    var plinth := _box("LumPlinth", Vector3(0.0, 0.3, -8.0), Vector3(3.8, 0.6, 3.8), Color("16101d"), true)
    plinth.rotation.y = PI * 0.25

    lum_avatar = LumAvatarScene.instantiate() as Node3D
    lum_avatar.name = "LumAvatarSocket"
    lum_avatar.position = Vector3(0.0, 0.65, -8.0)
    add_child(lum_avatar)

    var halo := OmniLight3D.new()
    halo.name = "LumHalo"
    halo.position = Vector3(0.0, 3.0, -8.0)
    halo.light_color = Color("ff4f9f")
    halo.light_energy = 3.0
    halo.omni_range = 8.0
    add_child(halo)

func get_lum_focus_position() -> Vector3:
    return lum_avatar.global_position + Vector3(0.0, 1.65, 0.0)

func pulse_lum(duration: float) -> void:
    if lum_avatar != null:
        lum_avatar.pulse(duration)

func restore_lum() -> void:
    if lum_avatar != null:
        lum_avatar.restore_visual_state()

func set_lum_expression(expression_name: String, weight: float = 1.0) -> void:
    if lum_avatar != null:
        lum_avatar.set_expression(expression_name, weight)

func set_lum_look_target(world_position: Vector3) -> void:
    if lum_avatar != null and lum_avatar.has_method("set_look_target_world"):
        lum_avatar.call("set_look_target_world", world_position)

func _box(name_value: String, pos: Vector3, size: Vector3, color: Color, collidable: bool, emission: Color = Color(0, 0, 0, 1), emission_energy: float = 0.0) -> Node3D:
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
    material.metallic = 0.32
    material.roughness = 0.58
    if emission_energy > 0.0:
        material.emission_enabled = true
        material.emission = emission
        material.emission_energy_multiplier = emission_energy
        _neon_materials.append(material)
    mesh_instance.material_override = material
    root_node.add_child(mesh_instance)
    return root_node

func _neon_strip(pos: Vector3, size: Vector3, color: Color) -> void:
    _box("NeonStrip_%s_%s" % [int(pos.x * 10.0), int(pos.z * 10.0)], pos, size, Color("111018"), false, color, 4.0)

func _window_stack(base: Vector3, height: float, color: Color, side: float) -> void:
    var count := maxi(2, int(height / 2.2))
    for level in range(count):
        var y := 1.2 + float(level) * 2.0
        var size := Vector3(0.06, 0.28, 2.4)
        var pos := Vector3(base.x, y, base.z)
        _box("Window_%s_%s" % [int(base.z * 10.0), level], pos, size, Color("101018"), false, color, 2.0)

func _arch(pos: Vector3) -> void:
    var pink := Color("ff3c9d")
    _box("ArchLeft_%s" % int(pos.z), pos + Vector3(-3.2, 2.4, 0.0), Vector3(0.25, 4.8, 0.25), Color("111018"), false, pink, 2.6)
    _box("ArchRight_%s" % int(pos.z), pos + Vector3(3.2, 2.4, 0.0), Vector3(0.25, 4.8, 0.25), Color("111018"), false, pink, 2.6)
    _box("ArchTop_%s" % int(pos.z), pos + Vector3(0.0, 4.8, 0.0), Vector3(6.65, 0.25, 0.25), Color("111018"), false, pink, 2.6)

func _sign(title: String, pos: Vector3, tint: Color, font_size: int = 64) -> void:
    var sign := Label3D.new()
    sign.text = title
    sign.position = pos
    sign.font_size = font_size
    sign.pixel_size = 0.009
    sign.modulate = tint
    sign.outline_modulate = Color("07151e")
    sign.outline_size = 10
    sign.no_depth_test = false
    add_child(sign)

func _build_noir_details() -> void:
    _sign("NEON RIVERWALK", Vector3(0, 5.5, -7), Color("8dffe0"), 72)
    _sign("D E T R O I T   /   A F T E R   D A R K", Vector3(0, 4.8, -7), Color("f6bd7b"), 28)
    _sign("L U M", Vector3(0, 0.8, -5.8), Color("90ffe3"), 42)
    # A distant skyline closes the empty horizon without new textures.
    for i in range(11):
        var h := 4.0 + float((i * 7) % 9)
        var x := float(i - 5) * 3.7
        _box("DistantTower%d" % i, Vector3(x, h / 2, -31), Vector3(2.8, h, 3), Color("142e3b"), false)
        for row in range(int(h)):
            _box("DistantWindow%d_%d" % [i, row], Vector3(x, 0.7 + row, -29.45), Vector3(1.8, 0.12, 0.05), Color("c7975d"), false, Color("ceaa74"), 0.7)
    for side in [-1.0, 1.0]:
        for z in [-11.0, -3.0, 5.0]:
            var x: float = side * 8.0
            _box("LampMast", Vector3(x, 2.2, z), Vector3(0.16, 4.4, 0.16), Color("334651"), false)
            _box("LampCap", Vector3(x, 4.4, z), Vector3(1.1, 0.13, 0.5), Color("ffd49b"), false, Color("ffd49b"), 1.2)
            _box("Bench", Vector3(side * 9.0, 0.55, z + 2), Vector3(2.5, 0.25, 0.7), Color("4b4142"), true)
        _box("StagePylon", Vector3(side * 4.6, 1.6, -8), Vector3(0.8, 3.2, 0.8), Color("263d48"), true)
        _box("PylonTrim", Vector3(side * 4.6, 1.6, -7.57), Vector3(0.12, 2.8, 0.05), Color("68e5ca"), false, Color("68e5ca"), 1.3)
    var key := OmniLight3D.new()
    key.name = "LumPortraitKey"
    key.position = Vector3(0, 3.8, -4.5)
    key.light_color = Color("b5f9e3")
    key.light_energy = 3.2
    key.omni_range = 9
    add_child(key)

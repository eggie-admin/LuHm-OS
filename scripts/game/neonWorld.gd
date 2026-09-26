extends Node3D

const LumAvatarScript := preload("res://scripts/game/lumAvatar.gd")

var player_spawn := Vector3(0.0, 1.15, 8.0)
var lum_avatar: Node3D
var lum_plinth: Node3D
var lum_halo: OmniLight3D
var crown_core: Node3D
var _crown_tween: Tween
var _neon_materials: Array[StandardMaterial3D] = []

func _ready() -> void:
    _build_environment()
    _build_riverwalk()
    _build_city()
    _build_lum_stage()

func _process(delta: float) -> void:
    if crown_core != null:
        crown_core.rotate_y(delta * 0.72)

func _build_environment() -> void:
    var env_node := WorldEnvironment.new()
    env_node.name = "WorldEnvironment"
    var env := Environment.new()
    env.background_mode = Environment.BG_COLOR
    env.background_color = Color("070711")
    env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
    env.ambient_light_color = Color("5e4b87")
    env.ambient_light_energy = 0.62
    env.fog_enabled = true
    env.fog_light_color = Color("23152f")
    env.fog_density = 0.012
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
    _arch(Vector3(0.0, 0.0, 5.0))

    var accent := OmniLight3D.new()
    accent.name = "RiverwalkAccent"
    accent.position = Vector3(0.0, 5.0, -8.0)
    accent.light_color = Color("ff3c9d")
    accent.light_energy = 3.4
    accent.omni_range = 14.0
    add_child(accent)

func _build_lum_stage() -> void:
    lum_plinth = _box("LumPlinth", Vector3(0.0, 0.3, -8.0), Vector3(3.8, 0.6, 3.8), Color("16101d"), true)
    lum_plinth.rotation.y = PI * 0.25

    lum_avatar = LumAvatarScript.new()
    lum_avatar.name = "LumAvatarSocket"
    lum_avatar.position = Vector3(0.0, 0.65, -8.0)
    add_child(lum_avatar)

    lum_halo = OmniLight3D.new()
    lum_halo.name = "LumHalo"
    lum_halo.position = Vector3(0.0, 3.0, -8.0)
    lum_halo.light_color = Color("ff4f9f")
    lum_halo.light_energy = 3.0
    lum_halo.omni_range = 8.0
    add_child(lum_halo)

    _build_crown_core()

func _build_crown_core() -> void:
    crown_core = Node3D.new()
    crown_core.name = "ProfessorCrownCore"
    crown_core.position = Vector3(0.0, 4.15, -8.0)
    add_child(crown_core)

    var gold := _material(Color("6b5317"), 0.5, 0.26, Color("ffd85f"), 4.6)
    var pink := _material(Color("4b1737"), 0.35, 0.3, Color("ff4f9f"), 3.8)

    var orb := MeshInstance3D.new()
    orb.name = "CrownOrb"
    var orb_mesh := SphereMesh.new()
    orb_mesh.radius = 0.30
    orb_mesh.height = 0.60
    orb.mesh = orb_mesh
    orb.material_override = pink
    crown_core.add_child(orb)

    for i in range(5):
        var angle := TAU * float(i) / 5.0
        var jewel := MeshInstance3D.new()
        jewel.name = "CrownJewel_%02d" % i
        var jewel_mesh := SphereMesh.new()
        jewel_mesh.radius = 0.09
        jewel_mesh.height = 0.18
        jewel.mesh = jewel_mesh
        jewel.position = Vector3(cos(angle) * 0.48, 0.06, sin(angle) * 0.48)
        jewel.material_override = gold
        crown_core.add_child(jewel)

        var spike := MeshInstance3D.new()
        spike.name = "CrownSpike_%02d" % i
        var spike_mesh := CylinderMesh.new()
        spike_mesh.top_radius = 0.025
        spike_mesh.bottom_radius = 0.075
        spike_mesh.height = 0.46
        spike.mesh = spike_mesh
        spike.position = Vector3(cos(angle) * 0.42, 0.34, sin(angle) * 0.42)
        spike.material_override = gold
        crown_core.add_child(spike)

func pet_lum() -> void:
    if lum_avatar == null:
        return
    lum_avatar.pulse(0.46)
    lum_avatar.set_expression("smile", 1.0)
    var home_rotation := lum_avatar.rotation_degrees
    var tween := create_tween()
    tween.set_trans(Tween.TRANS_BACK)
    tween.set_ease(Tween.EASE_OUT)
    tween.tween_property(lum_avatar, "rotation_degrees", home_rotation + Vector3(0.0, 18.0, -4.0), 0.14)
    tween.tween_property(lum_avatar, "rotation_degrees", home_rotation + Vector3(0.0, -12.0, 4.0), 0.14)
    tween.tween_property(lum_avatar, "rotation_degrees", home_rotation, 0.14)
    tween.tween_callback(func(): lum_avatar.set_expression("neutral", 0.0))

func crown_pulse() -> void:
    if crown_core == null or lum_halo == null:
        return
    if _crown_tween != null and _crown_tween.is_valid():
        _crown_tween.kill()
    crown_core.scale = Vector3.ONE
    lum_halo.light_energy = 3.0
    _crown_tween = create_tween()
    _crown_tween.set_trans(Tween.TRANS_SINE)
    _crown_tween.set_ease(Tween.EASE_IN_OUT)
    _crown_tween.tween_property(crown_core, "scale", Vector3.ONE * 1.72, 0.18)
    _crown_tween.parallel().tween_property(lum_halo, "light_energy", 8.0, 0.18)
    _crown_tween.tween_property(crown_core, "scale", Vector3.ONE, 0.34)
    _crown_tween.parallel().tween_property(lum_halo, "light_energy", 3.0, 0.34)
    if lum_avatar != null:
        lum_avatar.pulse(0.52)

func oni_pop() -> void:
    for i in range(3):
        _spawn_oni_orb(i)

func _spawn_oni_orb(index: int) -> void:
    var oni := Node3D.new()
    oni.name = "MiniOni_%02d" % index
    var angle := -0.8 + float(index) * 0.8
    oni.position = Vector3(sin(angle) * 2.2, 0.72, -8.0 + cos(angle) * 1.8)
    oni.scale = Vector3.ONE * 0.12
    add_child(oni)

    var body_material := _material(Color("241229"), 0.3, 0.34, Color("ff4f9f") if index % 2 == 0 else Color("55dfff"), 4.0)
    var horn_material := _material(Color("15111d"), 0.55, 0.28, Color("ffd85f"), 2.0)

    var head := MeshInstance3D.new()
    var head_mesh := SphereMesh.new()
    head_mesh.radius = 0.32
    head_mesh.height = 0.64
    head.mesh = head_mesh
    head.material_override = body_material
    oni.add_child(head)

    for side in [-1.0, 1.0]:
        var horn := MeshInstance3D.new()
        var horn_mesh := CylinderMesh.new()
        horn_mesh.top_radius = 0.02
        horn_mesh.bottom_radius = 0.07
        horn_mesh.height = 0.28
        horn.mesh = horn_mesh
        horn.position = Vector3(0.16 * side, 0.32, 0.0)
        horn.rotation_degrees.z = -18.0 * side
        horn.material_override = horn_material
        oni.add_child(horn)

    var start := oni.position
    var tween := create_tween()
    tween.set_trans(Tween.TRANS_BACK)
    tween.set_ease(Tween.EASE_OUT)
    tween.tween_property(oni, "scale", Vector3.ONE, 0.20 + float(index) * 0.04)
    tween.parallel().tween_property(oni, "position", start + Vector3(0.0, 1.1 + float(index) * 0.18, 0.0), 0.24)
    tween.tween_interval(0.52)
    tween.set_trans(Tween.TRANS_SINE)
    tween.set_ease(Tween.EASE_IN)
    tween.tween_property(oni, "scale", Vector3.ZERO, 0.24)
    tween.parallel().tween_property(oni, "position", start + Vector3(0.0, 2.2, 0.0), 0.24)
    tween.tween_callback(oni.queue_free)

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

func _material(color: Color, metallic: float, roughness: float, emission: Color = Color(0, 0, 0, 1), emission_energy: float = 0.0) -> StandardMaterial3D:
    var material := StandardMaterial3D.new()
    material.albedo_color = color
    material.metallic = metallic
    material.roughness = roughness
    if emission_energy > 0.0:
        material.emission_enabled = true
        material.emission = emission
        material.emission_energy_multiplier = emission_energy
        _neon_materials.append(material)
    return material

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

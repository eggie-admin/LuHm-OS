extends Node3D

const MOVE_SPEED := 5.5
const TURN_SPEED := 1.8

var player: CharacterBody3D
var camera: Camera3D
var cathedral: Control
var world_hud: Control
var move_axis := Vector2.ZERO

func _ready() -> void:
    _build_world()
    _build_ui()
    _show_cathedral()

func _process(delta: float) -> void:
    if cathedral.visible:
        return
    var key_axis := Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
    var axis := key_axis if key_axis.length() > move_axis.length() else move_axis
    if axis.length() > 0.05:
        var forward := -player.global_transform.basis.z
        var right := player.global_transform.basis.x
        var dir := (right * axis.x + forward * axis.y)
        dir.y = 0.0
        dir = dir.normalized()
        player.velocity.x = dir.x * MOVE_SPEED
        player.velocity.z = dir.z * MOVE_SPEED
        player.look_at(player.global_position + dir, Vector3.UP)
    else:
        player.velocity.x = move_toward(player.velocity.x, 0.0, MOVE_SPEED * delta * 5.0)
        player.velocity.z = move_toward(player.velocity.z, 0.0, MOVE_SPEED * delta * 5.0)
    if not player.is_on_floor():
        player.velocity.y -= 18.0 * delta
    player.move_and_slide()

func _build_world() -> void:
    var env := WorldEnvironment.new()
    var environment := Environment.new()
    environment.background_mode = Environment.BG_COLOR
    environment.background_color = Color("080710")
    environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
    environment.ambient_light_color = Color("7253a8")
    environment.ambient_light_energy = 0.55
    env.environment = environment
    add_child(env)

    var sun := DirectionalLight3D.new()
    sun.rotation_degrees = Vector3(-58.0, -28.0, 0.0)
    sun.light_energy = 1.15
    sun.shadow_enabled = true
    add_child(sun)

    var ground := MeshInstance3D.new()
    var ground_mesh := PlaneMesh.new()
    ground_mesh.size = Vector2(80.0, 80.0)
    ground.mesh = ground_mesh
    var ground_mat := StandardMaterial3D.new()
    ground_mat.albedo_color = Color("10101a")
    ground_mat.metallic = 0.35
    ground_mat.roughness = 0.78
    ground.material_override = ground_mat
    add_child(ground)

    _add_riverwalk()
    _add_city_blocks()
    _add_lum_beacon()

    player = CharacterBody3D.new()
    player.name = "Player"
    player.position = Vector3(0.0, 1.1, 8.0)
    var body_shape := CollisionShape3D.new()
    var capsule := CapsuleShape3D.new()
    capsule.radius = 0.45
    capsule.height = 1.7
    body_shape.shape = capsule
    player.add_child(body_shape)
    add_child(player)

    camera = Camera3D.new()
    camera.position = Vector3(0.0, 3.0, 6.2)
    camera.rotation_degrees.x = -10.0
    camera.current = true
    player.add_child(camera)

func _add_riverwalk() -> void:
    var river := MeshInstance3D.new()
    var river_mesh := BoxMesh.new()
    river_mesh.size = Vector3(70.0, 0.08, 18.0)
    river.mesh = river_mesh
    river.position = Vector3(0.0, -0.02, -20.0)
    var mat := StandardMaterial3D.new()
    mat.albedo_color = Color("12334a")
    mat.metallic = 0.65
    mat.roughness = 0.2
    mat.emission_enabled = true
    mat.emission = Color("0b2140")
    mat.emission_energy_multiplier = 0.65
    river.material_override = mat
    add_child(river)

    var rail_mat := StandardMaterial3D.new()
    rail_mat.albedo_color = Color("59e5ff")
    rail_mat.emission_enabled = true
    rail_mat.emission = Color("59e5ff")
    rail_mat.emission_energy_multiplier = 2.5
    for x in range(-16, 17, 4):
        var post := MeshInstance3D.new()
        var post_mesh := BoxMesh.new()
        post_mesh.size = Vector3(0.12, 1.0, 0.12)
        post.mesh = post_mesh
        post.position = Vector3(float(x), 0.5, -10.7)
        post.material_override = rail_mat
        add_child(post)

func _add_city_blocks() -> void:
    var heights := [5.0, 8.0, 11.0, 6.5, 14.0, 9.0, 7.5, 12.0, 5.5, 10.0]
    for i in range(heights.size()):
        var building := MeshInstance3D.new()
        var mesh := BoxMesh.new()
        var h: float = heights[i]
        mesh.size = Vector3(3.2, h, 3.2)
        building.mesh = mesh
        var side := -1.0 if i % 2 == 0 else 1.0
        building.position = Vector3(side * (7.0 + (i % 3) * 4.2), h * 0.5, 2.0 - floor(i / 2.0) * 6.0)
        var mat := StandardMaterial3D.new()
        mat.albedo_color = Color("171323") if i % 2 == 0 else Color("21132b")
        mat.metallic = 0.15
        mat.roughness = 0.82
        building.material_override = mat
        add_child(building)

        var crown := OmniLight3D.new()
        crown.position = building.position + Vector3(0.0, h * 0.55, 0.0)
        crown.light_color = Color("ff4b88") if i % 2 == 0 else Color("59e5ff")
        crown.light_energy = 2.2
        crown.omni_range = 5.0
        add_child(crown)

func _add_lum_beacon() -> void:
    var lum := MeshInstance3D.new()
    var mesh := SphereMesh.new()
    mesh.radius = 0.75
    mesh.height = 1.5
    lum.mesh = mesh
    lum.position = Vector3(0.0, 1.6, -7.0)
    var mat := StandardMaterial3D.new()
    mat.albedo_color = Color("ff4b88")
    mat.emission_enabled = true
    mat.emission = Color("ff4b88")
    mat.emission_energy_multiplier = 3.4
    lum.material_override = mat
    add_child(lum)

    var light := OmniLight3D.new()
    light.position = lum.position
    light.light_color = Color("ff4b88")
    light.light_energy = 4.5
    light.omni_range = 8.0
    add_child(light)

func _build_ui() -> void:
    cathedral = Control.new()
    cathedral.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    add_child(cathedral)

    var shade := ColorRect.new()
    shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    shade.color = Color(0.025, 0.02, 0.06, 0.92)
    cathedral.add_child(shade)

    var panel := VBoxContainer.new()
    panel.set_anchors_preset(Control.PRESET_CENTER)
    panel.position = Vector2(-390.0, -360.0)
    panel.custom_minimum_size = Vector2(780.0, 720.0)
    panel.add_theme_constant_override("separation", 28)
    cathedral.add_child(panel)

    var title := Label.new()
    title.text = "LUHM OS // CATHEDRAL"
    title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    title.add_theme_font_size_override("font_size", 44)
    panel.add_child(title)

    var sub := Label.new()
    sub.text = "CLEAN PLAY SPINE · NATIVE GODOT · HUMAN CROWN GATE"
    sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    sub.add_theme_font_size_override("font_size", 20)
    panel.add_child(sub)

    var line := Label.new()
    line.text = "Detroit riverwalk prototype online.\nNo legacy control plane. No cloud required."
    line.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    line.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    line.add_theme_font_size_override("font_size", 27)
    panel.add_child(line)

    var enter := Button.new()
    enter.text = "WORLD MODE"
    enter.custom_minimum_size = Vector2(0.0, 110.0)
    enter.add_theme_font_size_override("font_size", 32)
    enter.pressed.connect(_show_world)
    panel.add_child(enter)

    world_hud = Control.new()
    world_hud.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    add_child(world_hud)

    var top_bar := HBoxContainer.new()
    top_bar.position = Vector2(28.0, 36.0)
    top_bar.custom_minimum_size = Vector2(1024.0, 90.0)
    world_hud.add_child(top_bar)

    var back := Button.new()
    back.text = "CATHEDRAL"
    back.custom_minimum_size = Vector2(270.0, 80.0)
    back.add_theme_font_size_override("font_size", 24)
    back.pressed.connect(_show_cathedral)
    top_bar.add_child(back)

    var hud_label := Label.new()
    hud_label.text = "  RIVERWALK // CLEANPLAY 01"
    hud_label.add_theme_font_size_override("font_size", 25)
    top_bar.add_child(hud_label)

    var dpad := GridContainer.new()
    dpad.columns = 3
    dpad.position = Vector2(44.0, 1810.0)
    dpad.custom_minimum_size = Vector2(470.0, 470.0)
    world_hud.add_child(dpad)

    _dpad_blank(dpad)
    _dpad_button(dpad, "▲", Vector2(0, -1))
    _dpad_blank(dpad)
    _dpad_button(dpad, "◀", Vector2(-1, 0))
    _dpad_button(dpad, "▼", Vector2(0, 1))
    _dpad_button(dpad, "▶", Vector2(1, 0))

func _dpad_blank(parent: Control) -> void:
    var spacer := Control.new()
    spacer.custom_minimum_size = Vector2(150.0, 150.0)
    parent.add_child(spacer)

func _dpad_button(parent: Control, glyph: String, axis: Vector2) -> void:
    var button := Button.new()
    button.text = glyph
    button.custom_minimum_size = Vector2(150.0, 150.0)
    button.add_theme_font_size_override("font_size", 42)
    button.button_down.connect(func(): move_axis = axis)
    button.button_up.connect(func(): move_axis = Vector2.ZERO)
    parent.add_child(button)

func _show_world() -> void:
    cathedral.visible = false
    world_hud.visible = true

func _show_cathedral() -> void:
    cathedral.visible = true
    world_hud.visible = false
    move_axis = Vector2.ZERO

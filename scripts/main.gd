extends Node3D

signal cutscene_event(event_name: String)

const MOVE_SPEED := 5.5
const TURN_SPEED := 1.8
const INTRO_CUTSCENE_PATH := "res://cutscenes/lumBeaconIntro.json"
const CutsceneDirectorScript := preload("res://scripts/cutsceneDirector.gd")

var player: CharacterBody3D
var camera: Camera3D
var cathedral: Control
var world_hud: Control
var dialogue_label: Label
var lum_beacon: MeshInstance3D
var lum_beacon_light: OmniLight3D
var cutscene_director
var move_axis := Vector2.ZERO
var controls_locked := false
var intro_cutscene_played := false
var camera_home_transform := Transform3D.IDENTITY
var lum_beacon_home_scale := Vector3.ONE
var lum_beacon_home_energy := 4.5

func _ready() -> void:
    _build_world()
    _build_ui()
    _build_cutscene_runtime()
    _show_cathedral()

func _process(delta: float) -> void:
    if cathedral.visible:
        return

    if controls_locked:
        move_axis = Vector2.ZERO
        player.velocity.x = move_toward(player.velocity.x, 0.0, MOVE_SPEED * delta * 5.0)
        player.velocity.z = move_toward(player.velocity.z, 0.0, MOVE_SPEED * delta * 5.0)
        if not player.is_on_floor():
            player.velocity.y -= 18.0 * delta
        player.move_and_slide()
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
    lum_beacon = MeshInstance3D.new()
    lum_beacon.name = "LumBeacon"
    var mesh := SphereMesh.new()
    mesh.radius = 0.75
    mesh.height = 1.5
    lum_beacon.mesh = mesh
    lum_beacon.position = Vector3(0.0, 1.6, -7.0)
    var mat := StandardMaterial3D.new()
    mat.albedo_color = Color("ff4b88")
    mat.emission_enabled = true
    mat.emission = Color("ff4b88")
    mat.emission_energy_multiplier = 3.4
    lum_beacon.material_override = mat
    add_child(lum_beacon)

    lum_beacon_light = OmniLight3D.new()
    lum_beacon_light.name = "LumBeaconLight"
    lum_beacon_light.position = lum_beacon.position
    lum_beacon_light.light_color = Color("ff4b88")
    lum_beacon_light.light_energy = lum_beacon_home_energy
    lum_beacon_light.omni_range = 8.0
    add_child(lum_beacon_light)

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
    title.text = "LUHM OS // BACKEND CATHEDRAL"
    title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    title.add_theme_font_size_override("font_size", 44)
    panel.add_child(title)

    var sub := Label.new()
    sub.text = "NATIVE GODOT SYSTEM COCKPIT · HUMAN CROWN GATE"
    sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    sub.add_theme_font_size_override("font_size", 20)
    panel.add_child(sub)

    var line := Label.new()
    line.text = "jQuery front end dry run active.\nNative Cathedral retained as backend authority."
    line.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    line.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    line.add_theme_font_size_override("font_size", 27)
    panel.add_child(line)

    var enter := Button.new()
    enter.text = "3D WORLD / DIAGNOSTIC"
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
    back.text = "BACKEND CATHEDRAL"
    back.custom_minimum_size = Vector2(270.0, 80.0)
    back.add_theme_font_size_override("font_size", 24)
    back.pressed.connect(_show_cathedral)
    top_bar.add_child(back)

    var hud_label := Label.new()
    hud_label.text = "  RIVERWALK // BACKEND NATIVE 01"
    hud_label.add_theme_font_size_override("font_size", 25)
    top_bar.add_child(hud_label)

    dialogue_label = Label.new()
    dialogue_label.position = Vector2(90.0, 1500.0)
    dialogue_label.custom_minimum_size = Vector2(900.0, 150.0)
    dialogue_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    dialogue_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
    dialogue_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    dialogue_label.add_theme_font_size_override("font_size", 32)
    dialogue_label.add_theme_color_override("font_color", Color("f8eff8"))
    dialogue_label.add_theme_color_override("font_outline_color", Color("120914"))
    dialogue_label.add_theme_constant_override("outline_size", 10)
    dialogue_label.visible = false
    world_hud.add_child(dialogue_label)

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

func _build_cutscene_runtime() -> void:
    cutscene_director = CutsceneDirectorScript.new()
    cutscene_director.name = "CutsceneDirector"
    add_child(cutscene_director)
    cutscene_director.beat_started.connect(_on_cutscene_beat_started)
    cutscene_director.cutscene_finished.connect(_on_cutscene_finished)
    cutscene_director.cutscene_cancelled.connect(_on_cutscene_cancelled)
    cutscene_director.cutscene_failed.connect(_on_cutscene_failed)

func _dpad_blank(parent: Control) -> void:
    var spacer := Control.new()
    spacer.custom_minimum_size = Vector2(150.0, 150.0)
    parent.add_child(spacer)

func _dpad_button(parent: Control, glyph: String, axis: Vector2) -> void:
    var button := Button.new()
    button.text = glyph
    button.custom_minimum_size = Vector2(150.0, 150.0)
    button.add_theme_font_size_override("font_size", 42)
    button.button_down.connect(func(): _set_move_axis(axis))
    button.button_up.connect(func(): _set_move_axis(Vector2.ZERO))
    parent.add_child(button)

func _set_move_axis(axis: Vector2) -> void:
    move_axis = Vector2.ZERO if controls_locked else axis

func _show_world() -> void:
    cathedral.visible = false
    world_hud.visible = true
    if not intro_cutscene_played:
        intro_cutscene_played = true
        call_deferred("_play_intro_cutscene")

func _show_cathedral() -> void:
    if cutscene_director != null and cutscene_director.is_running():
        cutscene_director.cancel()
    _restore_cutscene_state(0.0)
    _unlock_player()
    cathedral.visible = true
    world_hud.visible = false
    move_axis = Vector2.ZERO

func _play_intro_cutscene() -> void:
    var document := _load_cutscene_document(INTRO_CUTSCENE_PATH)
    if document.is_empty():
        push_warning("LuHm cutscene document unavailable")
        return
    camera_home_transform = camera.transform
    lum_beacon_home_scale = lum_beacon.scale
    lum_beacon_home_energy = lum_beacon_light.light_energy
    await cutscene_director.play_cutscene(document)

func _load_cutscene_document(path: String) -> Dictionary:
    if not FileAccess.file_exists(path):
        return {}
    var decoded = JSON.parse_string(FileAccess.get_file_as_string(path))
    if decoded is Dictionary:
        return decoded
    return {}

func _on_cutscene_beat_started(beat: Dictionary) -> void:
    var beat_type := str(beat.get("type", ""))
    var duration := maxf(float(beat.get("duration", 0.0)), 0.0)
    match beat_type:
        "lock_player":
            _lock_player()
        "camera_move":
            _camera_cutscene_move(duration)
        "lum_beacon_pulse":
            _pulse_lum_beacon(duration)
        "dialogue":
            _show_cutscene_dialogue(beat)
        "restore":
            _restore_cutscene_state(duration)

func _lock_player() -> void:
    controls_locked = true
    move_axis = Vector2.ZERO
    if player != null:
        player.velocity.x = 0.0
        player.velocity.z = 0.0

func _unlock_player() -> void:
    controls_locked = false
    move_axis = Vector2.ZERO

func _camera_cutscene_move(duration: float) -> void:
    if camera == null:
        return
    var tween := create_tween()
    tween.set_trans(Tween.TRANS_SINE)
    tween.set_ease(Tween.EASE_IN_OUT)
    tween.set_parallel(true)
    tween.tween_property(camera, "position", Vector3(0.0, 2.35, 2.8), duration)
    tween.tween_property(camera, "rotation_degrees", Vector3(-4.0, 0.0, 0.0), duration)

func _pulse_lum_beacon(duration: float) -> void:
    if lum_beacon == null or lum_beacon_light == null:
        return
    var half := maxf(duration * 0.5, 0.05)
    var tween := create_tween()
    tween.set_trans(Tween.TRANS_SINE)
    tween.set_ease(Tween.EASE_IN_OUT)
    tween.tween_property(lum_beacon, "scale", lum_beacon_home_scale * 1.35, half)
    tween.parallel().tween_property(lum_beacon_light, "light_energy", lum_beacon_home_energy * 1.7, half)
    tween.tween_property(lum_beacon, "scale", lum_beacon_home_scale, half)
    tween.parallel().tween_property(lum_beacon_light, "light_energy", lum_beacon_home_energy, half)

func _show_cutscene_dialogue(beat: Dictionary) -> void:
    if dialogue_label != null:
        dialogue_label.text = str(beat.get("dialogue", ""))
        dialogue_label.visible = not dialogue_label.text.is_empty()
    var event_name := str(beat.get("event", ""))
    if not event_name.is_empty():
        cutscene_event.emit(event_name)

func _restore_cutscene_state(duration: float) -> void:
    if dialogue_label != null:
        dialogue_label.visible = false
    if lum_beacon != null:
        lum_beacon.scale = lum_beacon_home_scale
    if lum_beacon_light != null:
        lum_beacon_light.light_energy = lum_beacon_home_energy
    if camera == null:
        return
    if duration <= 0.0:
        camera.transform = camera_home_transform
        return
    var tween := create_tween()
    tween.set_trans(Tween.TRANS_SINE)
    tween.set_ease(Tween.EASE_IN_OUT)
    tween.tween_property(camera, "transform", camera_home_transform, duration)

func _on_cutscene_finished(_cutscene_id: String) -> void:
    _restore_cutscene_state(0.0)
    _unlock_player()

func _on_cutscene_cancelled(_cutscene_id: String) -> void:
    _restore_cutscene_state(0.0)
    _unlock_player()

func _on_cutscene_failed(reason: String) -> void:
    push_warning("LuHm cutscene failed: %s" % reason)
    _restore_cutscene_state(0.0)
    _unlock_player()

extends Node3D
## Source-only playable rehearsal; stylized stand-ins are not approved 3D models.
const CANON_PATH := "res://game/canon/CHARACTER_CANON_V1.json"
const LumAvatarScene := preload("res://scenes/LumAvatar.tscn")
const IDS := ["lum", "urd", "belldandy", "skuld"]
const COLORS := [Color("#19b4af"), Color("#a346af"), Color("#d3a578"), Color("#6e9fc8")]
const LINES := [
    "Lum: One base rig, four personalities. Try not to break the furniture, Professor.",
    "Urd: I brought the dramatic lighting. Someone else can do the paperwork.",
    "Belldandy: Welcome home. Your savepoint is ready.",
    "Skuld: The physics simulation is calibrated. Mostly."
]
var actor_roots: Array[Node3D] = []
var message: Label
var active_index := 0
var elapsed := 0.0
var _hud_column: VBoxContainer
var _selector_grid: GridContainer
var _canon_roles: Dictionary = {}
var _focus_markers: Array[Node3D] = []
var _lum_rig_loaded := false

func _ready() -> void:
    var file := FileAccess.open(CANON_PATH, FileAccess.READ)
    if file == null:
        push_error("Missing character canon; rehearsal refuses to misidentify the cast.")
        return
    var canon = JSON.parse_string(file.get_as_text())
    if not canon is Dictionary or not canon.has("characters"):
        push_error("Invalid character canon; rehearsal stopped.")
        return
    var characters: Dictionary = canon["characters"]
    for id in IDS:
        if not characters.has(id):
            push_error("Missing canonical character: " + id)
            return
    for id in IDS:
        _canon_roles[id] = str((characters[id] as Dictionary).get("role", "Goddess"))
    _build_stage()
    for i in IDS.size():
        _build_actor(i)
    _build_hud()
    _select(0)

func _build_stage() -> void:
    var camera := Camera3D.new()
    camera.position = Vector3(0, 3.4, 11.5)
    camera.rotation_degrees = Vector3(-11, 0, 0)
    camera.current = true
    add_child(camera)
    var sun := DirectionalLight3D.new()
    sun.rotation_degrees = Vector3(-50, -20, 0)
    sun.light_energy = 1.7
    add_child(sun)
    var floor := MeshInstance3D.new()
    var plane := PlaneMesh.new()
    plane.size = Vector2(16, 10)
    floor.mesh = plane
    floor.material_override = _material(Color("#151727"))
    add_child(floor)
    var environment := WorldEnvironment.new()
    var env := Environment.new()
    env.background_mode = Environment.BG_COLOR
    env.background_color = Color("#0b0916")
    environment.environment = env
    add_child(environment)

    # Lightweight neon stage geometry. No mod assets, images, or remote downloads.
    for x in [-5.6, 5.6]:
        for z in [-6.0, -1.5, 3.0]:
            _box(self, Vector3(x, 2.2, z), Vector3(0.65, 4.4, 0.65), Color("#252238"))
            _box(self, Vector3(x, 4.45, z), Vector3(1.25, 0.14, 1.25), Color("#ac47d4"), true)
    _box(self, Vector3(-4.1, 2.8, -7.0), Vector3(0.34, 5.6, 0.4), Color("#883dcb"), true)
    _box(self, Vector3(4.1, 2.8, -7.0), Vector3(0.34, 5.6, 0.4), Color("#883dcb"), true)
    _box(self, Vector3(0, 5.55, -7.0), Vector3(8.4, 0.35, 0.4), Color("#b248e1"), true)
    _box(self, Vector3(0, 4.6, -7.15), Vector3(5.8, 0.10, 0.15), Color("#28b7d6"), true)
    for z in [-6.5, -4.0, -1.5, 1.0, 3.5]:
        _box(self, Vector3(0, 0.035, z), Vector3(11.0, 0.04, 0.045), Color("#40284b"), true)
    for x in [-4.65, 4.65]:
        _box(self, Vector3(x, 0.04, -0.6), Vector3(0.055, 0.045, 11.5), Color("#16b7c7"), true)
    var stage_light := OmniLight3D.new()
    stage_light.position = Vector3(0, 4.5, 3.0)
    stage_light.light_color = Color("#b66aff")
    stage_light.light_energy = 1.2
    stage_light.omni_range = 12.0
    add_child(stage_light)

func _material(color: Color, glow: bool = false) -> StandardMaterial3D:
    var material := StandardMaterial3D.new()
    material.albedo_color = color
    material.roughness = 0.68
    if glow:
        material.emission_enabled = true
        material.emission = color
        material.emission_energy_multiplier = 1.7
    return material

func _part(parent: Node3D, shape: Mesh, pos: Vector3, color: Color, glow: bool = false) -> void:
    var node := MeshInstance3D.new()
    node.mesh = shape
    node.position = pos
    node.material_override = _material(color, glow)
    parent.add_child(node)

func _box(parent: Node3D, pos: Vector3, size: Vector3, color: Color, glow: bool = false) -> void:
    var mesh := BoxMesh.new()
    mesh.size = size
    _part(parent, mesh, pos, color, glow)

func _build_actor(i: int) -> void:
    var actor := Node3D.new()
    actor.name = IDS[i]
    actor.position = Vector3((float(i) - 1.5) * 2.1, 0, 0)
    add_child(actor)
    actor_roots.append(actor)
    var focus := Node3D.new()
    focus.name = "TapFocus"
    focus.position = Vector3(0, 2.92, 0)
    actor.add_child(focus)
    _box(focus, Vector3(0, 0, 0), Vector3(0.30, 0.30, 0.07), COLORS[i], true)
    focus.rotation_degrees.z = 45.0
    focus.visible = false
    _focus_markers.append(focus)
    var pedestal := CylinderMesh.new()
    pedestal.top_radius = 0.65
    pedestal.bottom_radius = 0.7
    pedestal.height = 0.18
    _part(actor, pedestal, Vector3(0, 0.1, 0), Color("#383045"))
    _box(actor, Vector3(0, 0.21, 0.50), Vector3(0.92, 0.05, 0.08), COLORS[i], true)

    # Reuse the actual Godot avatar socket. The existing verified Web build already
    # stages the GLB; the socket supplies a fallback for source-only Godot CI.
    if i == 0:
        var avatar := LumAvatarScene.instantiate() as Node3D
        avatar.name = "LumRigSocket"
        avatar.position = Vector3(0.0, 0.20, 0.0)
        actor.add_child(avatar)
        _lum_rig_loaded = bool(avatar.call("uses_external_model"))
        return

    # Only Urd, Belldandy and Skuld still use primitive stand-ins.
    var body := CylinderMesh.new()
    body.top_radius = 0.37
    body.bottom_radius = 0.49
    body.height = 1.35
    _part(actor, body, Vector3(0, 1.15, 0), COLORS[i])
    var head := SphereMesh.new()
    head.radius = 0.38
    head.height = 0.76
    _part(actor, head, Vector3(0, 2.13, 0), Color("#e6b5ab"))
    var hair := SphereMesh.new()
    hair.radius = 0.41
    hair.height = 0.43
    _part(actor, hair, Vector3(0, 2.43, -0.045), [Color("#a34e35"), Color("#343044"), Color("#3a221f"), Color("#252a4c")][i])
    if i == 0:
        var horn := CylinderMesh.new()
        horn.top_radius = 0.015
        horn.bottom_radius = 0.10
        horn.height = 0.32
        _part(actor, horn, Vector3(-0.25, 2.7, 0), Color("#181522"))
        _part(actor, horn, Vector3(0.25, 2.7, 0), Color("#181522"))
    # Remaining three Goddesses use explicitly temporary costume silhouettes.
    match i:
        0:
            # Lum's auburn updo, oni horns, teal executive lapels.
            var bun := SphereMesh.new()
            bun.radius = 0.20
            bun.height = 0.40
            _part(actor, bun, Vector3(0.08, 2.75, -0.12), Color("#a34e35"))
            _box(actor, Vector3(0, 1.55, 0.38), Vector3(0.16, 0.56, 0.07), Color("#111924"))
            _box(actor, Vector3(0, 1.70, 0.43), Vector3(0.07, 0.12, 0.04), Color("#3de0cf"), true)
        1:
            # Urd's magenta thread charms and dramatic weave sash.
            _box(actor, Vector3(0, 1.12, 0.44), Vector3(0.66, 0.14, 0.11), Color("#ff54b9"), true)
            var thread_orb := SphereMesh.new()
            thread_orb.radius = 0.13
            thread_orb.height = 0.26
            for x in [-0.65, 0.65]:
                _part(actor, thread_orb, Vector3(x, 1.73, 0.30), Color("#b46dff"), true)
        2:
            # Belldandy's ivory mantle, oxblood ribbons, antique-gold crown.
            _box(actor, Vector3(0, 1.68, 0.38), Vector3(0.72, 0.16, 0.12), Color("#e5d5b7"))
            for x in [-0.27, 0.27]:
                _box(actor, Vector3(x, 1.20, 0.37), Vector3(0.11, 0.88, 0.06), Color("#792d40"))
            var gold := SphereMesh.new()
            gold.radius = 0.13
            gold.height = 0.26
            _part(actor, gold, Vector3(0, 2.83, 0), Color("#bfa069"), true)
        3:
            # Adult Skuld's hardware belt, tool charms and chrome accents.
            _box(actor, Vector3(0, 1.13, 0.43), Vector3(0.70, 0.17, 0.12), Color("#bec4d8"))
            for x in [-0.30, 0.30]:
                _box(actor, Vector3(x, 0.95, 0.45), Vector3(0.14, 0.20, 0.09), Color("#29c8d7"), true)
            _box(actor, Vector3(0, 1.60, 0.39), Vector3(0.22, 0.12, 0.08), Color("#151627"))

func _build_hud() -> void:
    var canvas := CanvasLayer.new()
    add_child(canvas)
    var column := VBoxContainer.new()
    column.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
    column.offset_top = -205
    column.offset_bottom = -12
    column.offset_left = 14
    column.offset_right = -14
    canvas.add_child(column)
    _hud_column = column
    message = Label.new()
    message.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    message.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    message.add_theme_font_size_override("font_size", 19)
    column.add_child(message)
    var row := GridContainer.new()
    row.name = "GoddessSelector"
    row.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    column.add_child(row)
    _selector_grid = row
    for i in IDS.size():
        var index := i
        var button := Button.new()
        button.text = IDS[i].capitalize()
        button.custom_minimum_size = Vector2(110, 44)
        button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
        button.pressed.connect(func(): _select(index))
        row.add_child(button)
    var back := Button.new()
    back.text = "RETURN TO CATHEDRAL"
    back.custom_minimum_size = Vector2(0, 44)
    back.pressed.connect(func(): get_tree().change_scene_to_file("res://scenes/Main.tscn"))
    column.add_child(back)
    get_viewport().size_changed.connect(_refresh_hud_layout)
    _refresh_hud_layout()

func _refresh_hud_layout() -> void:
    if _hud_column == null or _selector_grid == null:
        return
    var portrait := get_viewport().get_visible_rect().size.x < 630.0
    _selector_grid.columns = 2 if portrait else 4
    _hud_column.offset_top = -265 if portrait else -205

func _select(i: int) -> void:
    active_index = i
    for index in actor_roots.size():
        actor_roots[index].scale = Vector3.ONE * (1.10 if index == i else 1.0)
        _focus_markers[index].visible = index == i
    if message != null:
        var art_state := "IMPORTED 3D RIG" if _lum_rig_loaded else "AVATAR FALLBACK"
        if i != 0:
            art_state = "PROTOTYPE STAND-IN · MODEL PENDING"
        message.text = LINES[i] + "\n" + str(_canon_roles.get(IDS[i], "Goddess")) + " · " + art_state

func _process(delta: float) -> void:
    elapsed += delta
    for i in actor_roots.size():
        actor_roots[i].position.y = sin(elapsed * 1.4 + i) * 0.045
        actor_roots[i].rotation.y = sin(elapsed * 0.8 + i) * 0.12

func _tap_actor(screen_point: Vector2) -> void:
    var camera := get_viewport().get_camera_3d()
    if camera == null:
        return
    var best_index := -1
    var best_distance := 90.0
    for index in actor_roots.size():
        var center := actor_roots[index].global_position + Vector3(0.0, 1.6, 0.0)
        if camera.is_position_behind(center):
            continue
        var point := camera.unproject_position(center)
        var distance := point.distance_to(screen_point)
        if distance < best_distance:
            best_index = index
            best_distance = distance
    if best_index >= 0:
        _select(best_index)

func _unhandled_input(event: InputEvent) -> void:
    if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
        _tap_actor(event.position)
    elif event is InputEventScreenTouch and event.pressed:
        _tap_actor(event.position)
    elif event is InputEventKey and event.pressed and not event.echo:
        if event.keycode == KEY_LEFT:
            _select((active_index + IDS.size() - 1) % IDS.size())
        elif event.keycode == KEY_RIGHT:
            _select((active_index + 1) % IDS.size())

extends Node3D
## Source-only playable rehearsal; stylized stand-ins are not approved 3D models.
const CANON_PATH := "res://game/canon/CHARACTER_CANON_V1.json"
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

func _material(color: Color) -> StandardMaterial3D:
    var material := StandardMaterial3D.new()
    material.albedo_color = color
    material.roughness = 0.75
    return material

func _part(parent: Node3D, shape: Mesh, pos: Vector3, color: Color) -> void:
    var node := MeshInstance3D.new()
    node.mesh = shape
    node.position = pos
    node.material_override = _material(color)
    parent.add_child(node)

func _build_actor(i: int) -> void:
    var actor := Node3D.new()
    actor.name = IDS[i]
    actor.position = Vector3((float(i) - 1.5) * 2.1, 0, 0)
    add_child(actor)
    actor_roots.append(actor)
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
    var pedestal := CylinderMesh.new()
    pedestal.top_radius = 0.65
    pedestal.bottom_radius = 0.7
    pedestal.height = 0.18
    _part(actor, pedestal, Vector3(0, 0.1, 0), Color("#383045"))

func _build_hud() -> void:
    var canvas := CanvasLayer.new()
    add_child(canvas)
    var column := VBoxContainer.new()
    column.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
    column.offset_top = -135
    column.offset_bottom = -12
    column.offset_left = 20
    column.offset_right = -20
    canvas.add_child(column)
    message = Label.new()
    message.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    message.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    message.add_theme_font_size_override("font_size", 19)
    column.add_child(message)
    var row := HBoxContainer.new()
    row.alignment = BoxContainer.ALIGNMENT_CENTER
    column.add_child(row)
    for i in IDS.size():
        var index := i
        var button := Button.new()
        button.text = IDS[i].capitalize()
        button.custom_minimum_size = Vector2(110, 44)
        button.pressed.connect(func(): _select(index))
        row.add_child(button)

func _select(i: int) -> void:
    active_index = i
    if message != null:
        message.text = LINES[i] + "\nPROTOTYPE STAND-INS · NO CANON MODEL CLAIM"

func _process(delta: float) -> void:
    elapsed += delta
    for i in actor_roots.size():
        actor_roots[i].position.y = sin(elapsed * 1.4 + i) * 0.045
        actor_roots[i].rotation.y = sin(elapsed * 0.8 + i) * 0.12

func _unhandled_input(event: InputEvent) -> void:
    if event is InputEventKey and event.pressed and not event.echo:
        if event.keycode == KEY_LEFT:
            _select((active_index + IDS.size() - 1) % IDS.size())
        elif event.keycode == KEY_RIGHT:
            _select((active_index + 1) % IDS.size())

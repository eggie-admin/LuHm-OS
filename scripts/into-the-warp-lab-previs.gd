extends Node3D
## Into the Warp: private first-camera proxy scene, not a final character model.
const LENGTH := 4.5
var _time := 0.0
var _camera: Camera3D

func _ready() -> void:
    _stage()
    _monitors()
    _actors()
    _camera = Camera3D.new()
    _camera.name = "PrevisCamera"
    _camera.current = true
    _camera.fov = 76.0
    add_child(_camera)
    _frame_camera(0.0)
    var overlay := CanvasLayer.new()
    overlay.name = "ReviewSlate"
    add_child(overlay)
    var title := Label.new()
    title.name = "SourceBoundary"
    title.text = "INTO THE WARP // LAB PREVIS 300 // PROXY ACTORS ONLY"
    title.position = Vector2(30, 36)
    title.add_theme_font_size_override("font_size", 20)
    overlay.add_child(title)
    print("LAB_PREVIS_READY four_monitors=true actors=human_eggie_and_lum")

func _process(delta: float) -> void:
    _time += delta
    _frame_camera(clampf(_time / LENGTH, 0.0, 1.0))
    if _time >= LENGTH:
        print("LAB_PREVIS_COMPLETE 4.5s")
        get_tree().quit(0)

func _frame_camera(t: float) -> void:
    var ease := t * t * (3.0 - 2.0 * t)
    _camera.position = Vector3(0.65, 2.98, 8.8).lerp(Vector3(-0.35, 2.60, 6.0), ease)
    _camera.look_at(Vector3(0.0, 1.75, -2.4), Vector3.UP)

func _mat(color: Color, glow: bool = false) -> StandardMaterial3D:
    var material := StandardMaterial3D.new()
    material.albedo_color = color
    material.metallic = 0.18
    material.roughness = 0.62
    if glow:
        material.emission_enabled = true
        material.emission = color
        material.emission_energy_multiplier = 1.45
    return material

func _box(parent: Node3D, name: String, point: Vector3, size: Vector3, color: Color, glow: bool = false) -> void:
    var node := MeshInstance3D.new()
    node.name = name
    var mesh := BoxMesh.new()
    mesh.size = size
    node.mesh = mesh
    node.position = point
    node.material_override = _mat(color, glow)
    parent.add_child(node)

func _sphere(parent: Node3D, name: String, point: Vector3, radius: float, color: Color) -> void:
    var node := MeshInstance3D.new()
    node.name = name
    var mesh := SphereMesh.new()
    mesh.radius = radius
    mesh.height = radius * 2.0
    node.mesh = mesh
    node.position = point
    node.material_override = _mat(color)
    parent.add_child(node)

func _cylinder(parent: Node3D, name: String, point: Vector3, radius: float, height: float, color: Color) -> void:
    var node := MeshInstance3D.new()
    node.name = name
    var mesh := CylinderMesh.new()
    mesh.top_radius = radius
    mesh.bottom_radius = radius
    mesh.height = height
    node.mesh = mesh
    node.position = point
    node.material_override = _mat(color)
    parent.add_child(node)

func _stage() -> void:
    var environment := WorldEnvironment.new()
    environment.name = "LabEnvironment"
    var world := Environment.new()
    world.background_mode = Environment.BG_COLOR
    world.background_color = Color("#090c16")
    world.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
    world.ambient_light_color = Color("#617389")
    world.ambient_light_energy = 0.7
    environment.environment = world
    add_child(environment)
    var light := DirectionalLight3D.new()
    light.name = "LabKeyLight"
    light.rotation_degrees = Vector3(-40, -30, 0)
    light.light_color = Color("#efae75")
    light.light_energy = 1.7
    light.shadow_enabled = true
    add_child(light)
    var crt := OmniLight3D.new()
    crt.name = "CRTFill"
    crt.position = Vector3(0, 3.5, -2.5)
    crt.light_color = Color("#43c7d7")
    crt.light_energy = 1.7
    crt.omni_range = 12
    add_child(crt)
    var set := Node3D.new()
    set.name = "LaboratorySet"
    add_child(set)
    _box(set, "Floor", Vector3(0, -0.12, -0.7), Vector3(11, 0.24, 12), Color("#242129"))
    _box(set, "RearWall", Vector3(0, 3.0, -5.3), Vector3(11, 6, 0.23), Color("#25252d"))
    _box(set, "BenchTop", Vector3(-3.2, 0.98, 0.4), Vector3(2.5, 0.16, 1.3), Color("#624837"))
    _box(set, "BenchBase", Vector3(-3.2, 0.48, 0.4), Vector3(2, 0.91, 0.8), Color("#33303c"))
    _box(set, "StarboardWindow", Vector3(4.75, 2.6, -2.0), Vector3(0.12, 3.25, 2.4), Color("#bd7580"), true)
    _box(set, "RearHatch", Vector3(-4.55, 1.65, -5.1), Vector3(1.22, 3.18, 0.21), Color("#171924"))
    for i in range(6):
        _box(set, "DeckLine%02d" % i, Vector3(0, 0.016, -4.1 + i * 1.6), Vector3(10.0, 0.015, 0.04), Color("#655140"))
    for i in range(5):
        _box(set, "BenchSwitch%02d" % i, Vector3(-3.9 + i * 0.31, 1.1, 0.25), Vector3(0.07, 0.10, 0.07), Color("#6bdce0"), true)

func _monitors() -> void:
    var subjects := ["01 HOME", "02 LUM", "03 BELLDANDY", "04 SKULD"]
    for i in range(4):
        var screen := Node3D.new()
        screen.name = "Monitor%02d" % (i + 1)
        screen.position = Vector3(-3.15 + float(i) * 2.1, 3.15, -4.94)
        add_child(screen)
        _box(screen, "Frame", Vector3.ZERO, Vector3(1.83, 1.30, 0.18), Color("#0e101c"))
        _box(screen, "CRT", Vector3(0, 0, 0.11), Vector3(1.61, 1.05, 0.03), Color("#176775"), true)
        var caption := Label3D.new()
        caption.name = "Feed"
        caption.text = subjects[i]
        caption.font_size = 32
        caption.pixel_size = 0.0041
        caption.position = Vector3(0, 0, 0.145)
        caption.modulate = Color("#dbf5e5")
        screen.add_child(caption)

func _actors() -> void:
    var eggie := Node3D.new()
    eggie.name = "EggieHumanProxy"
    eggie.position = Vector3(-0.90, 0, -1.0)
    add_child(eggie)
    _cylinder(eggie, "Suit", Vector3(0, 1.26, 0), 0.37, 1.12, Color("#40343c"))
    _box(eggie, "Waistcoat", Vector3(0, 1.34, 0.32), Vector3(0.45, 0.56, 0.10), Color("#79707a"))
    for side in [-1.0, 1.0]:
        _cylinder(eggie, "HumanLeg", Vector3(side * 0.21, 0.46, 0), 0.13, 0.9, Color("#292630"))
        _cylinder(eggie, "HumanArm", Vector3(side * 0.50, 1.25, 0), 0.12, 0.90, Color("#40343c"))
    _sphere(eggie, "HumanHead", Vector3(0, 2.17, 0), 0.31, Color("#bb957e"))
    _sphere(eggie, "SilverHair", Vector3(0, 2.39, -0.04), 0.28, Color("#c9c7ca"))
    _sphere(eggie, "SilverBeard", Vector3(0, 1.99, 0.22), 0.18, Color("#b6b4ba"))
    for side in [-1.0, 1.0]:
        var glasses := MeshInstance3D.new()
        glasses.name = "RoundWireGlasses"
        var ring := TorusMesh.new()
        ring.inner_radius = 0.11
        ring.outer_radius = 0.15
        glasses.mesh = ring
        glasses.position = Vector3(side * 0.16, 2.18, 0.31)
        glasses.rotation_degrees.x = 90.0
        glasses.material_override = _mat(Color("#d7d5d7"))
        eggie.add_child(glasses)
    var lum := Node3D.new()
    lum.name = "LumOniProxy"
    lum.position = Vector3(1.48, 0, -1.50)
    add_child(lum)
    _cylinder(lum, "TealBlackCoat", Vector3(0, 1.20, 0), 0.31, 1.20, Color("#174953"))
    _box(lum, "BlackLapels", Vector3(0, 1.3, 0.26), Vector3(0.32, 0.67, 0.08), Color("#111320"))
    for side in [-1.0, 1.0]:
        _cylinder(lum, "Leg", Vector3(side * 0.17, 0.39, 0), 0.10, 0.76, Color("#161723"))
        _cylinder(lum, "Arm", Vector3(side * 0.39, 1.18, 0), 0.10, 0.88, Color("#163b48"))
        _cylinder(lum, "SmallOniHorn", Vector3(side * 0.18, 2.47, 0), 0.055, 0.22, Color("#141722"))
    _sphere(lum, "Head", Vector3(0, 2.02, 0), 0.28, Color("#e1ad9f"))
    _sphere(lum, "AuburnUpdo", Vector3(0, 2.28, -0.10), 0.25, Color("#7c392d"))

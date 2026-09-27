extends Node3D

# Final-form scene layer: a compact Japanese kissaten / coffee-house shell around
# the existing Cathedral furniture. Geometry is procedural so the distributable
# build stays original and the existing pinned CC0 community assets remain the
# prop library. No runtime network access.

var _materials: Array[StandardMaterial3D] = []

func _ready() -> void:
    name = "CoffeeHouseSetDress"
    _build_architecture()
    _build_shoji()
    _build_counter_backdrop()
    _build_lanterns()
    _build_signage()

func _material(color: Color, roughness := 0.72, metallic := 0.0, emission := Color(0, 0, 0, 1), emission_energy := 0.0) -> StandardMaterial3D:
    var material := StandardMaterial3D.new()
    material.albedo_color = color
    material.roughness = roughness
    material.metallic = metallic
    if emission_energy > 0.0:
        material.emission_enabled = true
        material.emission = emission
        material.emission_energy_multiplier = emission_energy
    _materials.append(material)
    return material

func _box(node_name: String, pos: Vector3, size: Vector3, material: StandardMaterial3D, collidable := false) -> Node3D:
    var root: Node3D
    if collidable:
        var body := StaticBody3D.new()
        var collision := CollisionShape3D.new()
        var shape := BoxShape3D.new()
        shape.size = size
        collision.shape = shape
        body.add_child(collision)
        root = body
    else:
        root = Node3D.new()
    root.name = node_name
    root.position = pos
    add_child(root)

    var mesh_instance := MeshInstance3D.new()
    var mesh := BoxMesh.new()
    mesh.size = size
    mesh_instance.mesh = mesh
    mesh_instance.material_override = material
    root.add_child(mesh_instance)
    return root

func _build_architecture() -> void:
    var wood := _material(Color("241711"), 0.78)
    var dark_wood := _material(Color("120b09"), 0.84)
    var plaster := _material(Color("d7c8aa"), 0.92)
    var floor_mat := _material(Color("2d2018"), 0.74)

    _box("KissatenFloor", Vector3(0.0, 0.03, 14.2), Vector3(13.8, 0.10, 10.8), floor_mat, true)
    _box("KissatenBackWall", Vector3(0.0, 2.5, 19.2), Vector3(13.8, 5.0, 0.24), plaster, true)
    _box("KissatenLeftWall", Vector3(-6.8, 2.5, 14.2), Vector3(0.24, 5.0, 10.2), dark_wood, true)
    _box("KissatenRightWall", Vector3(6.8, 2.5, 14.2), Vector3(0.24, 5.0, 10.2), dark_wood, true)
    _box("KissatenCeilingBeam", Vector3(0.0, 4.65, 14.2), Vector3(13.8, 0.28, 0.34), wood)
    _box("KissatenFrontBeam", Vector3(0.0, 3.95, 9.15), Vector3(13.8, 0.34, 0.34), wood)

    # Preserve a clear center entrance/sightline for the opening Lum portrait.
    # The previous x=0 post sat directly between the camera and Lum on Samsung.
    for x in [-5.8, -3.0, 3.0, 5.8]:
        _box("KissatenPost_%s" % int((x + 6.0) * 10.0), Vector3(x, 2.05, 9.25), Vector3(0.22, 4.1, 0.22), wood)

func _build_shoji() -> void:
    var frame := _material(Color("4b3022"), 0.80)
    var paper := _material(Color("efe4c9"), 0.95, 0.0, Color("ffe7bd"), 0.16)
    var z := 18.98
    for panel in range(4):
        var x0 := -4.8 + float(panel) * 3.2
        _box("ShojiPaper_%d" % panel, Vector3(x0, 2.1, z), Vector3(2.75, 3.25, 0.05), paper)
        for rung in range(4):
            _box("ShojiH_%d_%d" % [panel, rung], Vector3(x0, 0.78 + float(rung) * 0.86, z - 0.04), Vector3(2.95, 0.07, 0.07), frame)
        for rung in range(3):
            _box("ShojiV_%d_%d" % [panel, rung], Vector3(x0 - 0.95 + float(rung) * 0.95, 2.1, z - 0.04), Vector3(0.07, 3.35, 0.07), frame)

func _build_counter_backdrop() -> void:
    var wood := _material(Color("352217"), 0.76)
    var brass := _material(Color("7a5a2d"), 0.42, 0.58)
    var black := _material(Color("09090b"), 0.48, 0.15)
    _box("BackCounter", Vector3(0.0, 1.15, 17.8), Vector3(7.2, 2.1, 0.75), wood, true)
    _box("CoffeeMachineBody", Vector3(-1.6, 2.35, 17.6), Vector3(1.35, 1.15, 0.82), black)
    _box("CoffeeMachineTop", Vector3(-1.6, 3.05, 17.6), Vector3(1.10, 0.18, 0.66), brass)
    for i in range(4):
        _box("CoffeeCup_%d" % i, Vector3(0.3 + float(i) * 0.55, 2.34, 17.55), Vector3(0.32, 0.34, 0.32), _material(Color("dad0bd"), 0.90))

func _build_lanterns() -> void:
    var lantern := _material(Color("f2d3a0"), 0.92, 0.0, Color("ffb56b"), 1.7)
    for i in range(3):
        var x := -3.8 + float(i) * 3.8
        _box("PaperLantern_%d" % i, Vector3(x, 3.45, 12.0), Vector3(0.72, 1.05, 0.72), lantern)
    for spec in [
        {"name":"WarmKeyA", "pos":Vector3(-3.6, 3.0, 13.0)},
        {"name":"WarmKeyB", "pos":Vector3(3.6, 3.0, 15.5)}
    ]:
        var light := OmniLight3D.new()
        light.name = spec["name"]
        light.position = spec["pos"]
        light.light_color = Color("ffb56b")
        light.light_energy = 1.15
        light.omni_range = 7.5
        light.shadow_enabled = false
        add_child(light)

func _build_signage() -> void:
    var label := Label3D.new()
    label.name = "OniCoffeeSign"
    label.text = "鬼珈琲  •  LUHM KISSA"
    label.position = Vector3(0.0, 4.18, 18.82)
    label.font_size = 48
    label.modulate = Color("ffd6a3")
    label.outline_size = 6
    label.outline_modulate = Color("1a0d0b")
    add_child(label)

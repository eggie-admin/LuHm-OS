extends Node3D

# Original distributable Crown Cathedral facade layered over the kissaten shell.
# Geometry is deliberately low-cost for Android GL Compatibility, but authored
# around the Lum focal socket instead of functioning as generic test geometry.

var _materials: Array[StandardMaterial3D] = []

func _ready() -> void:
    name = "CrownCathedralSetDress"
    _build_entry_plinth()
    _build_crown_gate()
    _build_roofline()
    _build_window_glow()
    _build_neon_spine()
    _build_identity()

func _material(color: Color, roughness := 0.7, metallic := 0.0, emission := Color(0, 0, 0, 1), emission_energy := 0.0) -> StandardMaterial3D:
    var mat := StandardMaterial3D.new()
    mat.albedo_color = color
    mat.roughness = roughness
    mat.metallic = metallic
    if emission_energy > 0.0:
        mat.emission_enabled = true
        mat.emission = emission
        mat.emission_energy_multiplier = emission_energy
    _materials.append(mat)
    return mat

func _box(node_name: String, pos: Vector3, size: Vector3, mat: StandardMaterial3D, rot := Vector3.ZERO) -> MeshInstance3D:
    var node := MeshInstance3D.new()
    node.name = node_name
    var mesh := BoxMesh.new()
    mesh.size = size
    node.mesh = mesh
    node.position = pos
    node.rotation_degrees = rot
    node.material_override = mat
    add_child(node)
    return node

func _build_entry_plinth() -> void:
    var stone := _material(Color("17141a"), 0.68, 0.24)
    var brass := _material(Color("7d5d31"), 0.38, 0.70)
    _box("CathedralPlinth", Vector3(0.0, 0.10, 9.55), Vector3(13.2, 0.22, 1.25), stone)
    for i in range(4):
        _box("CathedralStep_%d" % i, Vector3(0.0, 0.05 + float(i) * 0.06, 8.65 + float(i) * 0.24), Vector3(8.2 - float(i) * 0.5, 0.10, 0.46), stone)
    _box("BrassThreshold", Vector3(0.0, 0.25, 9.22), Vector3(6.4, 0.07, 0.16), brass)

func _build_crown_gate() -> void:
    var black_wood := _material(Color("100b10"), 0.58, 0.22)
    var magenta := _material(Color("21101c"), 0.35, 0.30, Color("ff3c9d"), 4.8)
    var cyan := _material(Color("0d1b20"), 0.32, 0.36, Color("55dfff"), 4.3)

    _box("CrownGateLeft", Vector3(-6.15, 2.25, 9.0), Vector3(0.34, 4.5, 0.42), black_wood)
    _box("CrownGateRight", Vector3(6.15, 2.25, 9.0), Vector3(0.34, 4.5, 0.42), black_wood)
    _box("CrownGateTop", Vector3(0.0, 4.35, 9.0), Vector3(12.7, 0.38, 0.46), black_wood)
    _box("CrownNeonLeft", Vector3(-5.88, 2.35, 8.76), Vector3(0.07, 3.35, 0.06), magenta)
    _box("CrownNeonRight", Vector3(5.88, 2.35, 8.76), Vector3(0.07, 3.35, 0.06), cyan)
    _box("CrownNeonTop", Vector3(0.0, 4.12, 8.75), Vector3(11.75, 0.07, 0.06), magenta)

    # Stylized oni crown horns, original geometry.
    _box("OniHornLeft", Vector3(-2.05, 4.93, 9.0), Vector3(0.34, 1.25, 0.34), black_wood, Vector3(0.0, 0.0, -24.0))
    _box("OniHornRight", Vector3(2.05, 4.93, 9.0), Vector3(0.34, 1.25, 0.34), black_wood, Vector3(0.0, 0.0, 24.0))

func _build_roofline() -> void:
    var roof := _material(Color("130f18"), 0.54, 0.34)
    var trim := _material(Color("3a2433"), 0.40, 0.42, Color("b579ff"), 1.8)
    _box("RoofLeft", Vector3(-3.35, 5.05, 14.3), Vector3(7.5, 0.28, 10.2), roof, Vector3(0.0, 0.0, -8.0))
    _box("RoofRight", Vector3(3.35, 5.05, 14.3), Vector3(7.5, 0.28, 10.2), roof, Vector3(0.0, 0.0, 8.0))
    _box("RoofRidge", Vector3(0.0, 5.58, 14.3), Vector3(0.42, 0.42, 10.5), trim)
    _box("RoofFrontTrim", Vector3(0.0, 4.84, 9.34), Vector3(13.9, 0.16, 0.22), trim)

func _build_window_glow() -> void:
    var frame := _material(Color("1e1319"), 0.70, 0.20)
    var warm := _material(Color("2c1a10"), 0.86, 0.02, Color("ffb56b"), 1.15)
    for side in [-1.0, 1.0]:
        var x := side * 4.65
        _box("WindowFrame_%s" % int(side), Vector3(x, 2.25, 18.82), Vector3(3.0, 3.0, 0.16), frame)
        _box("WindowGlow_%s" % int(side), Vector3(x, 2.25, 18.72), Vector3(2.62, 2.62, 0.05), warm)
        for rung in [-0.85, 0.0, 0.85]:
            _box("WindowRungV_%s_%s" % [int(side), int(rung * 100.0)], Vector3(x + rung, 2.25, 18.62), Vector3(0.06, 2.72, 0.05), frame)
        for rung in [1.40, 2.25, 3.10]:
            _box("WindowRungH_%s_%s" % [int(side), int(rung * 100.0)], Vector3(x, rung, 18.62), Vector3(2.72, 0.06, 0.05), frame)

func _build_neon_spine() -> void:
    var cyan := _material(Color("0d1d22"), 0.30, 0.40, Color("55dfff"), 4.8)
    var pink := _material(Color("25101d"), 0.30, 0.36, Color("ff3c9d"), 5.2)
    _box("CathedralSpine", Vector3(0.0, 0.055, 13.5), Vector3(0.13, 0.04, 8.1), pink)
    _box("CathedralCrossA", Vector3(-2.8, 0.055, 11.3), Vector3(3.5, 0.04, 0.10), cyan)
    _box("CathedralCrossB", Vector3(2.8, 0.055, 15.6), Vector3(3.5, 0.04, 0.10), cyan)

func _build_identity() -> void:
    var sign := Label3D.new()
    sign.name = "CrownCathedralSign"
    sign.text = "LUHM // ONI CATHEDRAL"
    sign.position = Vector3(0.0, 4.55, 8.70)
    sign.font_size = 54
    sign.modulate = Color("ffe0ef")
    sign.outline_size = 8
    sign.outline_modulate = Color("180a16")
    add_child(sign)

    var subtitle := Label3D.new()
    subtitle.name = "CrownCathedralSubtitle"
    subtitle.text = "鬼珈琲  •  RIVERWALK KISSA"
    subtitle.position = Vector3(0.0, 3.82, 8.69)
    subtitle.font_size = 30
    subtitle.modulate = Color("8cecff")
    subtitle.outline_size = 5
    subtitle.outline_modulate = Color("071016")
    add_child(subtitle)

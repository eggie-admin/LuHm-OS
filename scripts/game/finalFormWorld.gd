extends "res://scripts/game/neonWorld.gd"

# Final-form layer. The proven NeonWorld remains the physics/render/runtime base;
# this script only adds the coffee-house hero composition and layout overrides.
const FINAL_LAYOUT_PATH := "res://assets/community/final-form-layout.json"

func _ready() -> void:
    super._ready()
    name = "NeonWorld"
    _apply_final_layout()
    _build_kissaten_shell()
    _warm_final_environment()

func _load_final_layout() -> Dictionary:
    if not FileAccess.file_exists(FINAL_LAYOUT_PATH):
        return {}
    var parsed = JSON.parse_string(FileAccess.get_file_as_string(FINAL_LAYOUT_PATH))
    return parsed if parsed is Dictionary else {}

func _apply_final_layout() -> void:
    var document := _load_final_layout()
    var scene = document.get("scene", {})
    if not (scene is Dictionary):
        return

    player_spawn = _vec3(scene.get("player_spawn", [0.0, 1.15, 5.5]))

    var lum_position := _vec3(scene.get("lum_position", [0.8, 0.05, 12.4]))
    if lum_avatar != null:
        lum_avatar.position = lum_position

    var halo := get_node_or_null("LumHalo") as OmniLight3D
    if halo != null:
        halo.position = lum_position + Vector3(0.0, 2.95, 0.0)

func _build_kissaten_shell() -> void:
    var shell := Node3D.new()
    shell.name = "CoffeeHouseShell"
    add_child(shell)

    # Open-front late-night kissaten volume. The inherited WalkFloor remains the
    # collision authority; these surfaces create enclosure without a second floor.
    var dark_wood := Color("241710")
    var warm_wood := Color("4a2e1d")
    var paper := Color("e9d8b7")
    var amber := Color("ffb15a")
    var magenta := Color("ff4f9f")

    _box("CoffeeRearWall", Vector3(0.0, 2.15, 20.2), Vector3(13.0, 4.3, 0.28), dark_wood, true)
    _box("CoffeeLeftWall", Vector3(-6.5, 2.15, 15.0), Vector3(0.28, 4.3, 10.6), dark_wood, true)
    _box("CoffeeRightWall", Vector3(6.5, 2.15, 15.0), Vector3(0.28, 4.3, 10.6), dark_wood, true)
    _box("CoffeeThreshold", Vector3(0.0, 0.09, 9.7), Vector3(13.0, 0.18, 0.34), warm_wood, true)

    for x in [-5.8, -2.9, 0.0, 2.9, 5.8]:
        _box("CoffeePost_%s" % int(x * 10.0), Vector3(x, 2.15, 19.98), Vector3(0.18, 4.3, 0.18), warm_wood, false)

    for x in [-4.35, -1.45, 1.45, 4.35]:
        _box("Shoji_%s" % int(x * 10.0), Vector3(x, 2.15, 20.02), Vector3(2.55, 3.55, 0.06), paper, false, amber, 0.34)

    for z in [10.0, 12.6, 15.2, 17.8, 20.0]:
        _box("CeilingRib_%s" % int(z * 10.0), Vector3(0.0, 4.15, z), Vector3(13.0, 0.16, 0.22), warm_wood, false)

    for index in range(5):
        var x := -4.8 + float(index) * 2.4
        _box(
            "Lantern_%02d" % index,
            Vector3(x, 3.35, 10.25),
            Vector3(0.38, 0.62, 0.38),
            Color("3a1d18"),
            false,
            amber if index % 2 == 0 else magenta,
            2.2
        )

    _box("CoffeeSign", Vector3(0.0, 3.45, 9.82), Vector3(3.6, 0.54, 0.10), Color("151018"), false, magenta, 2.8)

func _warm_final_environment() -> void:
    var env_node := get_node_or_null("WorldEnvironment") as WorldEnvironment
    if env_node == null or env_node.environment == null:
        return
    env_node.environment.ambient_light_color = Color("80614f")
    env_node.environment.ambient_light_energy = 0.68
    env_node.environment.fog_light_color = Color("32202f")
    env_node.environment.fog_density = 0.010

func _vec3(value) -> Vector3:
    if value is Array and value.size() >= 3:
        return Vector3(float(value[0]), float(value[1]), float(value[2]))
    return Vector3.ZERO

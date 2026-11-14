extends Node3D
## Private preview of the Aramoor twin-tide archipelago. No remote models or auto-publication.
## Godot 4 Compatibility/WebGL2 first; native Vulkan is a separate renderer profile.
const MANIFEST_PATH := "res://game/world/aramoorArchipelagoV1.json"
const GENERATED_NAME := "GeneratedWorld"
@export var world_seed: int = 1711
@export var ghost_tide: bool = false
@export_range(0, 2, 1) var detail_tier: int = 1

var _report: Dictionary = {"status": "NOT_GENERATED"}
var _centers: Dictionary = {}
var _materials: Dictionary = {}

func _ready() -> void:
    build_world()
    var preview_camera := get_node_or_null("PreviewCamera") as Camera3D
    if preview_camera != null:
        preview_camera.look_at(Vector3(26.0, 0.0, 26.0), Vector3.UP)

func build_world() -> void:
    var previous := get_node_or_null(GENERATED_NAME)
    if previous != null:
        remove_child(previous)
        previous.free()
    _centers.clear()
    _materials.clear()
    _report = {"status": "HOLD_INVALID_MANIFEST", "crown": "STOP"}
    if not FileAccess.file_exists(MANIFEST_PATH):
        return
    var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(MANIFEST_PATH))
    if not parsed is Dictionary:
        return
    var data: Dictionary = parsed
    if data.get("schema", "") != "luhmOs.aramoorArchipelago.v1":
        return
    var zones: Variant = data.get("zones", [])
    var links: Variant = data.get("links", [])
    if not zones is Array or not links is Array:
        return
    if zones.size() != 9 or links.size() > 20:
        return
    var spacing := float(data.get("cellSize", 26))
    if spacing < 20.0 or spacing > 40.0:
        return
    var identities: Dictionary = {}
    for z in zones:
        if not z is Dictionary:
            return
        var zone: Dictionary = z
        var id := str(zone.get("id", ""))
        var grid: Variant = zone.get("grid", [])
        if id.is_empty() or identities.has(id) or not grid is Array or grid.size() != 2:
            return
        if absf(float(grid[0])) > 6.0 or absf(float(grid[1])) > 6.0:
            return
        identities[id] = true
        _centers[id] = Vector3(float(grid[0]) * spacing, 0.0, float(grid[1]) * spacing)
    for entry in links:
        if not entry is Array or entry.size() != 2:
            return
        if not identities.has(str(entry[0])) or not identities.has(str(entry[1])):
            return
        if str(entry[0]) == str(entry[1]):
            return
    var generated := Node3D.new()
    generated.name = GENERATED_NAME
    add_child(generated)
    _make_atmosphere(generated)
    _make_ocean(generated)
    var prop_total := 0
    var feature_signature := "%d:%s:%d" % [world_seed, str(ghost_tide), detail_tier]
    for i in range(zones.size()):
        var zone: Dictionary = zones[i]
        var id := str(zone["id"])
        var count := _make_zone(generated, zone, i)
        prop_total += count
        feature_signature += "|%s:%d" % [id, count]
    var bridge_count := 0
    for entry in links:
        var a: Vector3 = _centers[str(entry[0])]
        var b: Vector3 = _centers[str(entry[1])]
        _make_bridge(generated, a, b, bridge_count)
        bridge_count += 1
    _report = {
        "schema": "luhmOs.aramoorRuntimePreview.v1",
        "status": "GENERATED_GEOMETRY_CANDIDATE",
        "zoneCount": zones.size(),
        "bridgeCount": bridge_count,
        "decorationCount": prop_total,
        "artSocketCount": zones.size(),
        "worldSeed": world_seed,
        "worldState": "ghostTide" if ghost_tide else "livingTide",
        "renderProfile": "compatibilityWebGL2Safe",
        "shadowCasterCount": 1 if detail_tier >= 2 else 0,
        "fingerprint": feature_signature.sha256_text(),
        "sourcePdfIngested": false,
        "canonPromoted": false,
        "crown": "STOP"
    }

func set_tide(ghost: bool) -> void:
    ghost_tide = ghost
    build_world()

func set_seed(value: int) -> void:
    world_seed = clampi(value, 1, 2147483647)
    build_world()

func world_summary() -> Dictionary:
    return _report.duplicate(true)

func _make_atmosphere(stage: Node3D) -> void:
    var world_environment := WorldEnvironment.new()
    world_environment.name = "TwinTideAtmosphere"
    var atmosphere := Environment.new()
    atmosphere.background_mode = Environment.BG_COLOR
    atmosphere.background_color = Color("11142d") if ghost_tide else Color("3a5779")
    atmosphere.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
    atmosphere.ambient_light_color = Color("9984c7") if ghost_tide else Color("a7d7f6")
    atmosphere.ambient_light_energy = 0.6
    atmosphere.fog_enabled = true
    atmosphere.fog_density = 0.012
    atmosphere.fog_light_color = Color("55517e") if ghost_tide else Color("acc9d9")
    world_environment.environment = atmosphere
    stage.add_child(world_environment)
    var moon := DirectionalLight3D.new()
    moon.name = "SingleSunOrMoon"
    moon.rotation_degrees = Vector3(-48.0, 26.0, 0.0)
    moon.light_color = Color("c6a9f8") if ghost_tide else Color("ffdbc3")
    moon.light_energy = 0.85
    moon.shadow_enabled = detail_tier >= 2
    stage.add_child(moon)

func _make_ocean(stage: Node3D) -> void:
    var ocean := MeshInstance3D.new()
    ocean.name = "OceanPlane"
    var plane := PlaneMesh.new()
    plane.size = Vector2(110.0, 110.0)
    ocean.mesh = plane
    ocean.position = Vector3(26.0, -1.4, 26.0)
    ocean.material_override = _surface("#172445" if ghost_tide else "#1e6479", false)
    stage.add_child(ocean)

func _make_zone(stage: Node3D, zone: Dictionary, index: int) -> int:
    var id := str(zone["id"])
    var island := Node3D.new()
    island.name = "Zone_" + id
    island.position = _centers[id]
    island.set_meta("zoneId", id)
    island.set_meta("canonNpcSocket", str(zone.get("npc", "lum")))
    stage.add_child(island)
    var tone := str(zone.get("color", "#596477"))
    var accent := str(zone.get("accent", "#8ad9e2"))
    if ghost_tide:
        tone = "#484668"
    var ground := MeshInstance3D.new()
    ground.name = "IslandBase"
    var cylinder := CylinderMesh.new()
    cylinder.top_radius = 9.0
    cylinder.bottom_radius = 7.8
    cylinder.height = 1.5
    cylinder.radial_segments = 20
    ground.mesh = cylinder
    ground.material_override = _surface(tone, false)
    island.add_child(ground)
    var collision_body := StaticBody3D.new()
    collision_body.name = "IslandCollision"
    island.add_child(collision_body)
    var collision := CollisionShape3D.new()
    var collision_cylinder := CylinderShape3D.new()
    collision_cylinder.radius = 9.0
    collision_cylinder.height = 1.5
    collision.shape = collision_cylinder
    collision_body.add_child(collision)
    var art_socket := Marker3D.new()
    art_socket.name = "CanonArtSocket"
    art_socket.position = Vector3(0.0, 0.9, 0.0)
    island.add_child(art_socket)
    var npc_socket := Marker3D.new()
    npc_socket.name = "NpcSocket"
    npc_socket.position = Vector3(-2.2, 0.9, 1.1)
    island.add_child(npc_socket)
    var encounter_socket := Marker3D.new()
    encounter_socket.name = "EncounterSocket"
    encounter_socket.position = Vector3(2.4, 0.9, -1.2)
    island.add_child(encounter_socket)
    var beacon := MeshInstance3D.new()
    beacon.name = "TideBeacon"
    var beacon_mesh := CylinderMesh.new()
    beacon_mesh.top_radius = 0.42
    beacon_mesh.bottom_radius = 0.66
    beacon_mesh.height = 3.0
    beacon.mesh = beacon_mesh
    beacon.position = Vector3(0.0, 1.6, 0.0)
    beacon.material_override = _surface(accent, true)
    island.add_child(beacon)
    var lamp := OmniLight3D.new()
    lamp.name = "TideLantern"
    lamp.position = Vector3(0.0, 3.3, 0.0)
    lamp.light_color = Color(accent)
    lamp.omni_range = 8.0
    lamp.light_energy = 0.6
    lamp.shadow_enabled = false
    island.add_child(lamp)
    var rng := RandomNumberGenerator.new()
    rng.seed = world_seed + (index + 1) * 7919
    var count := 3 if detail_tier == 0 else (5 if detail_tier == 1 else 7)
    for i in range(count):
        var angle := TAU * float(i) / float(count) + rng.randf_range(-0.1, 0.1)
        var radius := rng.randf_range(5.0, 7.0)
        var position_on_island := Vector3(cos(angle) * radius, 1.05, sin(angle) * radius)
        var prop := MeshInstance3D.new()
        prop.name = "Scenery_%02d" % i
        var shape := SphereMesh.new()
        shape.radius = rng.randf_range(0.35, 0.8)
        shape.height = shape.radius * 2.0
        prop.mesh = shape
        prop.position = position_on_island
        prop.material_override = _surface(accent, true)
        island.add_child(prop)
    return count

func _make_bridge(stage: Node3D, a: Vector3, b: Vector3, index: int) -> void:
    var direction := b - a
    var body := StaticBody3D.new()
    body.name = "TideBridge_%02d" % index
    body.position = (a + b) * 0.5 + Vector3(0.0, 0.79, 0.0)
    body.rotation.y = atan2(direction.x, direction.z)
    stage.add_child(body)
    var extent := Vector3(2.5, 0.22, direction.length())
    var deck := MeshInstance3D.new()
    var mesh := BoxMesh.new()
    mesh.size = extent
    deck.mesh = mesh
    deck.material_override = _surface("#78658d" if ghost_tide else "#d7a98b", false)
    body.add_child(deck)
    var shape := CollisionShape3D.new()
    var box := BoxShape3D.new()
    box.size = extent
    shape.shape = box
    body.add_child(shape)

func _surface(color_text: String, emissive: bool) -> StandardMaterial3D:
    var key := color_text + (":lit" if emissive else ":base")
    if _materials.has(key):
        return _materials[key] as StandardMaterial3D
    var material := StandardMaterial3D.new()
    material.albedo_color = Color(color_text)
    material.metallic = 0.1 if emissive else 0.03
    material.roughness = 0.45 if emissive else 0.82
    if emissive:
        material.emission_enabled = true
        material.emission = Color(color_text)
        material.emission_energy_multiplier = 1.2
    _materials[key] = material
    return material

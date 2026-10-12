extends Node3D
# Original LuHm blockout stage, never evidence of finished model assets.
const AVATAR_SCENE := preload("res://scenes/GoddessAvatar.tscn")
const CHARACTER_IDS := ["lum", "urd", "belldandy", "skuld"]
const COLORS := [
    Color(0.08, 0.65, 0.64),
    Color(0.63, 0.13, 0.40),
    Color(0.80, 0.58, 0.35),
    Color(0.55, 0.60, 0.77)
]
var actors: Dictionary = {}

func _ready() -> void:
    var camera := Camera3D.new()
    camera.name = "LineupCamera"
    camera.position = Vector3(0, 3.3, 15.0)
    add_child(camera)
    camera.look_at(Vector3(0, 1.35, 0), Vector3.UP)
    camera.current = true
    var key_light := DirectionalLight3D.new()
    key_light.name = "LineupKeyLight"
    key_light.rotation_degrees = Vector3(-35, -25, 0)
    key_light.light_energy = 1.8
    add_child(key_light)

    for i in range(CHARACTER_IDS.size()):
        var character_id := String(CHARACTER_IDS[i])
        var station := Node3D.new()
        station.name = character_id + "Station"
        station.position = Vector3((float(i) - 1.5) * 2.65, 0.0, 0.0)
        add_child(station)
        var platform := MeshInstance3D.new()
        platform.name = "StageOnlyPodium"
        var disc := CylinderMesh.new()
        disc.top_radius = 0.90
        disc.bottom_radius = 0.98
        disc.height = 0.16
        platform.mesh = disc
        var material := StandardMaterial3D.new()
        material.albedo_color = COLORS[i]
        material.metallic = 0.6
        material.roughness = 0.4
        platform.material_override = material
        station.add_child(platform)
        var avatar := AVATAR_SCENE.instantiate() as Node3D
        avatar.name = character_id + "Avatar"
        avatar.set("character_id", character_id)
        avatar.set("assemble_on_ready", true)
        station.add_child(avatar)
        actors[character_id] = avatar
        var body_socket: Node3D = avatar.get_node("BodySocket")
        var available := body_socket.get_child_count() > 0
        var sign := Label3D.new()
        sign.name = "StatusLabel"
        sign.text = character_id.to_upper() + (" / LUM PHASE 2 CANDIDATE" if available else " / BODY UNASSIGNED")
        sign.position = Vector3(0, 2.52, 0)
        sign.font_size = 24
        sign.pixel_size = 0.006
        station.add_child(sign)

func lineup_receipts() -> Dictionary:
    var receipts: Dictionary = {}
    for character_id in CHARACTER_IDS:
        var avatar = actors.get(character_id)
        if avatar != null and is_instance_valid(avatar):
            receipts[character_id] = avatar.runtime_summary()
    return receipts

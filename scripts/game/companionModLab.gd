extends Node3D
const STATE := preload("res://scripts/game/companionAffinityState.gd")
const SOURCE := "res://game/demo/originalCompanionProfilesV1.json"
var companions: Array = []
var selected := 0
var status: Label
var feedback: Label
func _ready() -> void:
    var raw = JSON.parse_string(FileAccess.get_file_as_string(SOURCE))
    if not raw is Dictionary or raw.get("schema") != "luhmOs.originalCompanionProfiles.v1":
        push_error("COMPANION_LAB_NO_CANON")
        return
    var rows = raw.get("companions", [])
    if not rows is Array or rows.size() != 3:
        push_error("COMPANION_LAB_ROSTER_RED")
        return
    for row in rows:
        if not row is Dictionary:
            push_error("COMPANION_LAB_INVALID_ROW")
            return
        var c = STATE.new()
        if not c.configure(row):
            push_error("COMPANION_LAB_INVALID_PROFILE")
            return
        companions.append({"state":c,"color":Color("#"+str(row.get("hexColor","999999")))})
    _stage()
    _controls()
    _status("Select a companion.")

func _mesh(n: String, mesh: Mesh, color: Color, pos: Vector3) -> void:
    var item := MeshInstance3D.new()
    item.name = n
    item.mesh = mesh
    var mat := StandardMaterial3D.new()
    mat.albedo_color = color
    mat.metallic = 0.2
    item.material_override = mat
    item.position = pos
    add_child(item)

func _stage() -> void:
    var env_node := WorldEnvironment.new()
    var env := Environment.new()
    env.background_mode = Environment.BG_COLOR
    env.background_color = Color("#090c18")
    env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
    env.ambient_light_color = Color("#343556")
    env_node.environment = env
    add_child(env_node)
    var camera := Camera3D.new()
    camera.position = Vector3(0, 3.1, 8.4)
    add_child(camera)
    camera.look_at(Vector3(0, 1.2, 0), Vector3.UP)
    camera.current = true
    var light := DirectionalLight3D.new()
    light.rotation_degrees = Vector3(-55, 18, 0)
    add_child(light)
    var floor_mesh := BoxMesh.new()
    floor_mesh.size = Vector3(9, 0.2, 6)
    _mesh("Floor", floor_mesh, Color("#18182b"), Vector3(0,-0.1,0))
    for i in range(companions.size()):
        var x := (float(i)-1.0) * 2.55
        var tint: Color = companions[i]["color"]
        var torso := CapsuleMesh.new()
        torso.radius = 0.43
        torso.height = 1.8
        _mesh("OriginalCompanion%d" % i, torso, tint, Vector3(x,1.25,0))
        var head := SphereMesh.new()
        head.radius = 0.39
        head.height = 0.78
        _mesh("Face%d" % i, head, tint.lightened(0.25), Vector3(x,2.22,0))

func _controls() -> void:
    var hud := CanvasLayer.new()
    add_child(hud)
    var frame := MarginContainer.new()
    frame.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    frame.add_theme_constant_override("margin_left",20)
    frame.add_theme_constant_override("margin_right",20)
    frame.add_theme_constant_override("margin_top",18)
    frame.add_theme_constant_override("margin_bottom",18)
    hud.add_child(frame)
    var column := VBoxContainer.new()
    frame.add_child(column)
    var title := Label.new()
    title.text = "LUHM | COMPANION MOD LAB | GODOT 4"
    column.add_child(title)
    var roster := HBoxContainer.new()
    column.add_child(roster)
    for i in range(companions.size()):
        var btn := Button.new()
        btn.text = companions[i]["state"].display_name
        btn.custom_minimum_size = Vector2(90,55)
        var pick := i
        btn.pressed.connect(func(): _select(pick))
        roster.add_child(btn)
    status = Label.new()
    column.add_child(status)
    feedback = Label.new()
    feedback.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    column.add_child(feedback)
    var spacer := Control.new()
    spacer.size_flags_vertical = Control.SIZE_EXPAND_FILL
    column.add_child(spacer)
    var actions := HBoxContainer.new()
    column.add_child(actions)
    for event_id in ["talk","help","explore","flirtElsewhere"]:
        var btn := Button.new()
        btn.text = {"talk":"TALK","help":"HELP","explore":"EXPLORE","flirtElsewhere":"JEALOUSY"}[event_id]
        btn.custom_minimum_size = Vector2(80,58)
        btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
        var bound: String = event_id
        btn.pressed.connect(func(): apply_companion_event(bound))
        actions.add_child(btn)
    var back := Button.new()
    back.text = "BACK TO CATHEDRAL"
    back.custom_minimum_size = Vector2(0,55)
    back.pressed.connect(func(): get_tree().change_scene_to_file("res://scenes/Main.tscn"))
    column.add_child(back)

func _select(i: int) -> void:
    if i >= 0 and i < companions.size():
        selected = i
        _status("Companion selected.")

func apply_companion_event(event_id: String) -> Dictionary:
    if companions.is_empty():
        return {"accepted":false}
    var result: Dictionary = companions[selected]["state"].apply_event(event_id)
    if result.get("accepted",false):
        _status(str(result["reaction"]))
    return result

func _status(message: String) -> void:
    if companions.is_empty() or status == null or feedback == null:
        return
    var c = companions[selected]["state"]
    var stats: Dictionary = c.stats
    status.text = "%s | TRUST %d / AFFECTION %d / JEALOUSY %d" % [c.display_name,stats["trust"],stats["affection"],stats["jealousy"]]
    feedback.text = message

extends Node3D
## LuHm-OS original story hub preview. Procedural stand-in geometry only.
## No commercial assets, network provider calls, or autonomy.
const SOURCE := "res://game/studio/nightglassHubV1.json"
var manuscript: Dictionary = {}
var activeSceneId := ""
var worldGeometry: Node3D
var camera: Camera3D
var sceneLabel: Label
var speakerLabel: Label
var storyLabel: Label
var choicesRoot: VBoxContainer
var destinationButton: Button
var phaseLight: OmniLight3D

func _ready() -> void:
    var parsed = JSON.parse_string(FileAccess.get_file_as_string(SOURCE))
    if not parsed is Dictionary:
        push_error("NIGHTGLASS_SOURCE_MISSING")
        return
    if parsed.get("schema") != "luhmOs.creatorStudioWorld.v1" or parsed.get("product") != "LuHm-OS":
        push_error("NIGHTGLASS_SOURCE_REJECTED")
        return
    manuscript = parsed
    _build_3d()
    _build_hud()
    _enter_scene("nightglassBarHub")

func _build_3d() -> void:
    var environmentNode := WorldEnvironment.new()
    var environment := Environment.new()
    environment.background_mode = Environment.BG_COLOR
    environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
    environment.ambient_light_color = Color("#77738c")
    environmentNode.environment = environment
    add_child(environmentNode)
    camera = Camera3D.new()
    add_child(camera)
    camera.current = true
    phaseLight = OmniLight3D.new()
    phaseLight.position = Vector3(1, 5.5, 1)
    phaseLight.omni_range = 20.0
    phaseLight.light_energy = 2.1
    add_child(phaseLight)
    worldGeometry = Node3D.new()
    worldGeometry.name = "ProceduralScene"
    add_child(worldGeometry)

func _make_box(nodeName: String, shape: Vector3, center: Vector3, tint: Color) -> void:
    var meshNode := MeshInstance3D.new()
    meshNode.name = nodeName
    var mesh := BoxMesh.new()
    mesh.size = shape
    meshNode.mesh = mesh
    var material := StandardMaterial3D.new()
    material.albedo_color = tint
    material.metallic = 0.15
    material.roughness = 0.6
    meshNode.material_override = material
    meshNode.position = center
    worldGeometry.add_child(meshNode)

func _make_ball(nodeName: String, radius: float, center: Vector3, tint: Color) -> void:
    var meshNode := MeshInstance3D.new()
    meshNode.name = nodeName
    var sphere := SphereMesh.new()
    sphere.radius = radius
    sphere.height = radius * 2.0
    meshNode.mesh = sphere
    var material := StandardMaterial3D.new()
    material.albedo_color = tint
    material.emission_enabled = true
    material.emission = tint * 0.25
    meshNode.material_override = material
    meshNode.position = center
    worldGeometry.add_child(meshNode)

func _build_hud() -> void:
    var layer := CanvasLayer.new()
    add_child(layer)
    var layout := MarginContainer.new()
    layout.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    layout.add_theme_constant_override("margin_left", 20)
    layout.add_theme_constant_override("margin_right", 20)
    layout.add_theme_constant_override("margin_top", 16)
    layout.add_theme_constant_override("margin_bottom", 16)
    layer.add_child(layout)
    var column := VBoxContainer.new()
    column.add_theme_constant_override("separation", 9)
    layout.add_child(column)
    sceneLabel = _label("LuHm-OS · NIGHTGLASS", 25)
    column.add_child(sceneLabel)
    column.add_child(_label("ORIGINAL SOURCE PREVIEW · PROPOSED · CAST STOP", 14))
    var switchRow := HBoxContainer.new()
    column.add_child(switchRow)
    var barButton := Button.new()
    barButton.text = "NIGHTGLASS BAR"
    barButton.custom_minimum_size = Vector2(180, 48)
    barButton.pressed.connect(func(): _enter_scene("nightglassBarHub"))
    switchRow.add_child(barButton)
    var shoreButton := Button.new()
    shoreButton.text = "ECHO SHORE"
    shoreButton.custom_minimum_size = Vector2(160, 48)
    shoreButton.pressed.connect(func(): _enter_scene("echoShore"))
    switchRow.add_child(shoreButton)
    var companionButton := Button.new()
    companionButton.text = "COMPANION LAB"
    companionButton.custom_minimum_size = Vector2(180, 48)
    companionButton.pressed.connect(func(): get_tree().change_scene_to_file("res://scenes/CompanionModLab.tscn"))
    switchRow.add_child(companionButton)
    var grow := Control.new()
    grow.size_flags_vertical = Control.SIZE_EXPAND_FILL
    column.add_child(grow)
    var dialoguePanel := PanelContainer.new()
    dialoguePanel.custom_minimum_size = Vector2(0, 200)
    column.add_child(dialoguePanel)
    var dialogueColumn := VBoxContainer.new()
    dialogueColumn.add_theme_constant_override("separation", 7)
    dialoguePanel.add_child(dialogueColumn)
    speakerLabel = _label("Lum", 21)
    dialogueColumn.add_child(speakerLabel)
    storyLabel = _label("", 19)
    storyLabel.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    dialogueColumn.add_child(storyLabel)
    choicesRoot = VBoxContainer.new()
    dialogueColumn.add_child(choicesRoot)
    destinationButton = Button.new()
    destinationButton.custom_minimum_size = Vector2(0, 48)
    destinationButton.pressed.connect(_travel)
    column.add_child(destinationButton)
    var returnButton := Button.new()
    returnButton.text = "RETURN TO FIRST NIGHT"
    returnButton.custom_minimum_size = Vector2(0, 42)
    returnButton.pressed.connect(func(): get_tree().change_scene_to_file("res://scenes/Main.tscn"))
    column.add_child(returnButton)

func _label(value: String, size: int) -> Label:
    var item := Label.new()
    item.text = value
    item.add_theme_font_size_override("font_size", size)
    item.add_theme_color_override("font_color", Color("#f7eade"))
    item.add_theme_color_override("font_shadow_color", Color("#14101d"))
    return item

func _scene(sceneId: String) -> Dictionary:
    for candidate in manuscript.get("scenes", []):
        if candidate is Dictionary and candidate.get("sceneId") == sceneId:
            return candidate
    return {}

func _enter_scene(sceneId: String) -> void:
    var sceneData: Dictionary = _scene(sceneId)
    if sceneData.is_empty():
        return
    activeSceneId = sceneId
    for previous in worldGeometry.get_children():
        worldGeometry.remove_child(previous)
        previous.free()
    var palette: Dictionary = sceneData.get("palette", {})
    var floorTint := Color("#" + String(palette.get("floor", "30273b")))
    var glowTint := Color("#" + String(palette.get("light", "d18a67")))
    phaseLight.light_color = glowTint
    var currentEnvironment := get_node_or_null("WorldEnvironment") as WorldEnvironment
    if currentEnvironment != null and currentEnvironment.environment != null:
        currentEnvironment.environment.background_color = Color("#" + String(palette.get("sky", "10112c")))
    _make_box("WorldFloor", Vector3(22, 0.25, 18), Vector3(0, -0.15, 0), floorTint)
    if sceneId == "nightglassBarHub":
        _draw_bar(glowTint)
    else:
        _draw_shore(glowTint)
    var view: Array = sceneData.get("camera", [0, 4, 10])
    camera.position = Vector3(float(view[0]), float(view[1]), float(view[2]))
    camera.look_at(Vector3(0, 1.1, 0), Vector3.UP)
    sceneLabel.text = "LuHm-OS · " + String(sceneData.get("displayName", "Unknown"))
    var other: Dictionary = _scene(String(sceneData.get("destination", "")))
    destinationButton.text = "TRAVEL TO " + String(other.get("displayName", "UNKNOWN")).to_upper()
    _show_line(String(sceneData.get("spawnDialogueId", "")))

func _draw_bar(glow: Color) -> void:
    _make_box("BarCounter", Vector3(9, 1.15, 1.25), Vector3(0, 0.55, -2.2), Color("#54374b"))
    _make_box("BarFrontTrim", Vector3(9.2, 0.14, 1.5), Vector3(0, 1.15, -2.2), Color("#b38c76"))
    for i in range(4):
        var x := -3.2 + float(i) * 2.1
        _make_box("BarStool%d" % i, Vector3(0.7, 0.65, 0.7), Vector3(x, 0.42, -0.15), Color("#7c5268"))
        _make_box("BarLampStand%d" % i, Vector3(0.12, 2.6, 0.12), Vector3(x, 2.6, -3.4), Color("#483e52"))
        _make_ball("BarLantern%d" % i, 0.26, Vector3(x, 3.7, -3.4), glow)
    _make_box("VelvetBoothLeft", Vector3(2.4, 1, 1.4), Vector3(-7, 0.55, 0), Color("#743f5c"))
    _make_box("VelvetBoothRight", Vector3(2.4, 1, 1.4), Vector3(7, 0.55, 0), Color("#743f5c"))
    _make_ball("MidnightMoon", 0.78, Vector3(0, 5.9, -7), Color("#b0a5df"))

func _draw_shore(glow: Color) -> void:
    _make_box("MoonlitTide", Vector3(19, 0.07, 11), Vector3(0, -0.03, -2.8), Color("#286277"))
    _make_box("CoastalWalk", Vector3(5.5, 0.14, 11), Vector3(0, 0.05, 1.1), Color("#a19c89"))
    for i in range(5):
        var x := (float(i) - 2.0) * 3.0
        _make_box("SeaPillar%d" % i, Vector3(0.8, 1.5 + float(i % 3), 0.8), Vector3(x, 0.8, -4.0), Color("#70758d"))
    _make_ball("EchoMoon", 1.1, Vector3(0, 6.3, -7), Color("#b6cbd4"))
    _make_ball("TideSigil", 0.55, Vector3(0, 0.8, -0.9), glow)

func _show_line(lineId: String) -> void:
    for child in choicesRoot.get_children():
        choicesRoot.remove_child(child)
        child.free()
    for row in manuscript.get("dialogue", []):
        if not row is Dictionary:
            continue
        if row.get("lineId") != lineId or row.get("sceneId") != activeSceneId:
            continue
        speakerLabel.text = String(row.get("speakerId", "Unknown"))
        storyLabel.text = String(row.get("text", ""))
        for choice in row.get("choices", []):
            if not choice is Dictionary:
                continue
            var nextId := String(choice.get("nextLineId", ""))
            var button := Button.new()
            button.text = String(choice.get("label", "Continue"))
            button.custom_minimum_size = Vector2(0, 43)
            button.pressed.connect(func(): _show_line(nextId))
            choicesRoot.add_child(button)
        return
    speakerLabel.text = "UNAVAILABLE"
    storyLabel.text = "Dialogue link missing. Check the source validator."

func _travel() -> void:
    var sceneData: Dictionary = _scene(activeSceneId)
    _enter_scene(String(sceneData.get("destination", "")))

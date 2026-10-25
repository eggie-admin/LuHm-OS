extends Node3D
## Additive public-safe inspection floor. No private art, provider calls or writes.
const GoddessScene := preload("res://scenes/GoddessAvatar.tscn")
const CharacterIds := ["proxy", "lum", "urd", "belldandy", "skuld"]
var actor: Node3D
var camera: Camera3D
var keyLight: DirectionalLight3D
var player: AnimationPlayer
var players: Array[AnimationPlayer] = []
var materialMeshes: Array[MeshInstance3D] = []
var originalOverrides: Array = []
var statusLabel: Label
var clipSelect: OptionButton
var timeSlider: HSlider
var playButton: Button
var selectedId := "proxy"
var selectedClip := ""
var running := false
var clipTime := 0.0
var speed := 1.0
var yaw := 0.0
var pitch := 0.12
var distance := 4.8
var focusPoint := Vector3(0, 1.05, 0)
var dragging := false
var touches: Dictionary = {}
var pinchDistance := 0.0
var controls: Control
var lastReceipt: Dictionary = {}

func _ready() -> void:
    _buildStage()
    _buildControls()
    selectCharacter(0)
    _updateCamera()

func _buildStage() -> void:
    var world := WorldEnvironment.new()
    var environment := Environment.new()
    environment.background_mode = Environment.BG_COLOR
    environment.background_color = Color("101421")
    environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
    environment.ambient_light_color = Color("b6c3dc")
    environment.ambient_light_energy = 0.55
    world.environment = environment
    add_child(world)
    keyLight = DirectionalLight3D.new()
    keyLight.rotation_degrees = Vector3(-40, -25, 0)
    keyLight.light_energy = 1.6
    add_child(keyLight)
    camera = Camera3D.new()
    camera.current = true
    add_child(camera)
    var floorMesh := MeshInstance3D.new()
    var cylinder := CylinderMesh.new()
    cylinder.top_radius = 1.3
    cylinder.bottom_radius = 1.3
    cylinder.height = 0.05
    floorMesh.mesh = cylinder
    var material := StandardMaterial3D.new()
    material.albedo_color = Color("28364b")
    floorMesh.material_override = material
    add_child(floorMesh)

func _buildControls() -> void:
    var canvas := CanvasLayer.new()
    add_child(canvas)
    controls = Control.new()
    controls.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    controls.mouse_filter = Control.MOUSE_FILTER_IGNORE
    canvas.add_child(controls)
    var panel := PanelContainer.new()
    panel.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
    panel.offset_top = -205
    controls.add_child(panel)
    var rows := VBoxContainer.new()
    panel.add_child(rows)
    var scroll := ScrollContainer.new()
    scroll.custom_minimum_size.y = 47
    scroll.vertical_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
    rows.add_child(scroll)
    var top := HBoxContainer.new()
    scroll.add_child(top)
    var character := OptionButton.new()
    character.custom_minimum_size = Vector2(135, 44)
    for id in CharacterIds:
        character.add_item("Technical proxy" if id == "proxy" else String(id).capitalize())
    character.item_selected.connect(selectCharacter)
    top.add_child(character)
    for preset in ["Front", "Side", "Back", "3/4", "Reset"]:
        _button(top, preset, cameraPreset.bind(preset))
    _button(top, "Clay", setClay.bind(true))
    _button(top, "Materials", setClay.bind(false))
    _button(top, "Light", cycleLighting)
    _button(top, "Review JSON", exportReview)
    _button(top, "Frame PNG", captureFrame)
    _button(top, "Exit", func(): get_tree().change_scene_to_file("res://scenes/Main.tscn"))
    var playbackScroll := ScrollContainer.new()
    playbackScroll.custom_minimum_size.y = 47
    playbackScroll.vertical_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
    rows.add_child(playbackScroll)
    var playback := HBoxContainer.new()
    playbackScroll.add_child(playback)
    clipSelect = OptionButton.new()
    clipSelect.custom_minimum_size = Vector2(160, 44)
    clipSelect.item_selected.connect(selectClip)
    playback.add_child(clipSelect)
    playButton = _button(playback, "Play", togglePlayback)
    _button(playback, "− frame", stepFrame.bind(-1.0))
    _button(playback, "+ frame", stepFrame.bind(1.0))
    var speedSelect := OptionButton.new()
    for value in [0.25, 0.5, 1.0, 1.5]:
        speedSelect.add_item(str(value) + "×")
    speedSelect.selected = 2
    speedSelect.item_selected.connect(func(index: int): speed = [0.25, 0.5, 1.0, 1.5][index])
    playback.add_child(speedSelect)
    timeSlider = HSlider.new()
    timeSlider.step = 0.001
    timeSlider.custom_minimum_size.y = 30
    timeSlider.value_changed.connect(seekClip)
    rows.add_child(timeSlider)
    statusLabel = Label.new()
    statusLabel.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    statusLabel.custom_minimum_size.y = 62
    rows.add_child(statusLabel)
    var help := Label.new()
    help.text = "3D INSPECTOR · drag to orbit · wheel/pinch to zoom · controls scroll sideways"
    help.position = Vector2(12, 10)
    help.mouse_filter = Control.MOUSE_FILTER_IGNORE
    controls.add_child(help)

func _button(parent: Node, text: String, action: Callable) -> Button:
    var button := Button.new()
    button.text = text
    button.custom_minimum_size = Vector2(64, 44)
    button.pressed.connect(action)
    parent.add_child(button)
    return button

func selectCharacter(index: int) -> void:
    if index < 0 or index >= CharacterIds.size():
        return
    running = false
    clipTime = 0.0
    selectedClip = ""
    players.clear()
    materialMeshes.clear()
    originalOverrides.clear()
    if is_instance_valid(actor):
        remove_child(actor)
        actor.queue_free()
    selectedId = CharacterIds[index]
    if selectedId == "proxy":
        actor = _makeProxy()
        add_child(actor)
    else:
        actor = GoddessScene.instantiate()
        actor.set("character_id", selectedId)
        actor.set("assemble_on_ready", true)
        add_child(actor)
        for tree in actor.find_children("*", "AnimationTree", true, false):
            tree.active = false
    for node in actor.find_children("*", "AnimationPlayer", true, false):
        var animationPlayer := node as AnimationPlayer
        animationPlayer.stop()
        players.append(animationPlayer)
    for node in actor.find_children("*", "MeshInstance3D", true, false):
        materialMeshes.append(node as MeshInstance3D)
        originalOverrides.append(node.material_override)
    clipSelect.clear()
    for playerIndex in players.size():
        for clip in players[playerIndex].get_animation_list():
            if String(clip) == "RESET":
                continue
            clipSelect.add_item(String(clip))
            clipSelect.set_item_metadata(clipSelect.item_count - 1, {"player": playerIndex, "clip": String(clip)})
    player = null
    clipSelect.disabled = clipSelect.item_count == 0
    timeSlider.editable = clipSelect.item_count > 0
    playButton.disabled = clipSelect.item_count == 0
    playButton.text = "Play"
    if clipSelect.item_count > 0:
        selectClip(0)
    else:
        timeSlider.set_value_no_signal(0)
    _status()

func _makeProxy() -> Node3D:
    var root := Node3D.new()
    root.name = "TechnicalProxy"
    var body := MeshInstance3D.new()
    body.name = "Body"
    var capsule := CapsuleMesh.new()
    capsule.radius = 0.28
    capsule.height = 1.0
    body.mesh = capsule
    body.position.y = 0.95
    root.add_child(body)
    var head := MeshInstance3D.new()
    head.mesh = SphereMesh.new()
    head.scale = Vector3.ONE * 0.35
    head.position.y = 1.7
    root.add_child(head)
    var arm := MeshInstance3D.new()
    arm.name = "Arm"
    arm.mesh = BoxMesh.new()
    arm.scale = Vector3(0.15, 0.65, 0.15)
    arm.position = Vector3(0.5, 1.25, 0)
    root.add_child(arm)
    var proxyPlayer := AnimationPlayer.new()
    proxyPlayer.name = "AnimationPlayer"
    root.add_child(proxyPlayer)
    var library := AnimationLibrary.new()
    for clip in ["diagnosticIdle", "diagnosticTurn", "diagnosticWave"]:
        var animation := Animation.new()
        animation.length = 2.0
        animation.loop_mode = Animation.LOOP_LINEAR
        var track := animation.add_track(Animation.TYPE_VALUE)
        animation.track_set_path(track, NodePath("Body:position:y" if clip == "diagnosticIdle" else "Arm:rotation:z" if clip == "diagnosticWave" else ".:rotation:y"))
        animation.track_insert_key(track, 0, 0.95 if clip == "diagnosticIdle" else 0.0)
        animation.track_insert_key(track, 1, 1.02 if clip == "diagnosticIdle" else -1.1 if clip == "diagnosticWave" else PI)
        animation.track_insert_key(track, 2, 0.95 if clip == "diagnosticIdle" else 0.0 if clip == "diagnosticWave" else TAU)
        library.add_animation(clip, animation)
    proxyPlayer.add_animation_library("", library)
    return root

func selectClip(index: int) -> void:
    if index < 0 or index >= clipSelect.item_count:
        return
    for item in players:
        item.stop()
    var binding: Dictionary = clipSelect.get_item_metadata(index)
    player = players[binding["player"]]
    selectedClip = binding["clip"]
    clipTime = 0.0
    running = false
    playButton.text = "Play"
    timeSlider.max_value = player.get_animation(selectedClip).length
    seekClip(0)

func seekClip(value: float) -> void:
    if not is_instance_valid(player) or selectedClip.is_empty():
        return
    clipTime = clampf(value, 0, timeSlider.max_value)
    player.play(selectedClip)
    player.seek(clipTime, true)
    player.pause()
    timeSlider.set_value_no_signal(clipTime)

func togglePlayback() -> void:
    if not is_instance_valid(player):
        return
    running = not running
    playButton.text = "Pause" if running else "Play"

func stepFrame(direction: float) -> void:
    running = false
    playButton.text = "Play"
    seekClip(clipTime + direction / 30.0)

func _process(delta: float) -> void:
    if running and is_instance_valid(player) and timeSlider.max_value > 0:
        seekClip(fmod(clipTime + minf(delta, 0.1) * speed, timeSlider.max_value))

func cameraPreset(preset: String) -> void:
    yaw = {"Front": 0.0, "Side": PI / 2.0, "Back": PI, "3/4": PI / 4.0, "Reset": 0.0}.get(preset, 0.0)
    pitch = 0.12
    distance = 4.8
    _updateCamera()

func _updateCamera() -> void:
    camera.position = focusPoint + Vector3(sin(yaw) * cos(pitch), sin(pitch), cos(yaw) * cos(pitch)) * distance
    camera.look_at(focusPoint)

func _unhandled_input(event: InputEvent) -> void:
    if event is InputEventMouseButton:
        if event.button_index == MOUSE_BUTTON_LEFT:
            dragging = event.pressed
        if event.pressed and event.button_index in [MOUSE_BUTTON_WHEEL_UP, MOUSE_BUTTON_WHEEL_DOWN]:
            distance = clampf(distance * (0.9 if event.button_index == MOUSE_BUTTON_WHEEL_UP else 1.1), 1.5, 12.0)
    elif event is InputEventMouseMotion and dragging:
        yaw -= event.relative.x * 0.008
        pitch = clampf(pitch + event.relative.y * 0.008, -0.8, 1.1)
    elif event is InputEventScreenTouch:
        if event.pressed:
            touches[event.index] = event.position
        else:
            touches.erase(event.index)
        pinchDistance = 0.0
    elif event is InputEventScreenDrag:
        touches[event.index] = event.position
        if touches.size() == 1:
            yaw -= event.relative.x * 0.008
            pitch = clampf(pitch + event.relative.y * 0.008, -0.8, 1.1)
        elif touches.size() == 2:
            var points := touches.values()
            var gap: float = points[0].distance_to(points[1])
            if pinchDistance > 0 and gap > 0:
                distance = clampf(distance * pinchDistance / gap, 1.5, 12.0)
            pinchDistance = gap
    _updateCamera()

func _input(event: InputEvent) -> void:
    # Release ownership even when the pointer/finger ends above a UI control.
    if event is InputEventMouseButton and not event.pressed:
        dragging = false
    if event is InputEventScreenTouch and not event.pressed:
        touches.erase(event.index)
        pinchDistance = 0.0

func setClay(enabled: bool) -> void:
    var clay := StandardMaterial3D.new()
    clay.albedo_color = Color("a7a9b3")
    clay.roughness = 0.8
    for index in materialMeshes.size():
        materialMeshes[index].material_override = clay if enabled else originalOverrides[index]

func cycleLighting() -> void:
    keyLight.light_color = Color("be98ff") if keyLight.light_color == Color.WHITE else Color.WHITE

func reviewReceipt() -> Dictionary:
    var skeletons := actor.find_children("*", "Skeleton3D", true, false)
    var bones := 0
    for item in skeletons:
        bones += item.get_bone_count()
    return {"schema": "luhmOs.characterInspection.v1", "characterId": selectedId,
        "assetState": "ORIGINAL_TECHNICAL_PROXY" if selectedId == "proxy" else "MOUNTED_SOURCE_CANDIDATE" if not materialMeshes.is_empty() else "BODY_UNASSIGNED",
        "meshCount": materialMeshes.size(), "boneCount": bones, "clipCount": clipSelect.item_count,
        "animation": selectedClip, "seconds": clipTime, "speed": speed,
        "camera": {"yaw": yaw, "pitch": pitch, "distance": distance},
        "godotVersion": Engine.get_version_info().get("string", "unknown"),
        "privateAssetsUploaded": false, "serverWrites": false, "canonApproved": false,
        "deviceAcceptance": "UNVERIFIED", "physicsSimulation": "NOT_IMPLEMENTED"}

func _status() -> void:
    var receipt := reviewReceipt()
    statusLabel.text = "%s · %s · %d meshes · %d bones · %d clips\nSession only; no private uploads. Hair physics and rig editing are not implemented." % [selectedId.to_upper(), receipt["assetState"], receipt["meshCount"], receipt["boneCount"], receipt["clipCount"]]

func exportReview() -> void:
    lastReceipt = reviewReceipt()
    if OS.has_feature("web"):
        JavaScriptBridge.download_buffer(JSON.stringify(lastReceipt, "  ").to_utf8_buffer(), "character-inspection.json", "application/json")
    else:
        var file := FileAccess.open("user://character-inspection.json", FileAccess.WRITE)
        if file != null:
            file.store_string(JSON.stringify(lastReceipt, "  "))
    statusLabel.text = "Review JSON export requested. This does not approve Canon or save to the server."

func captureFrame() -> void:
    controls.visible = false
    await RenderingServer.frame_post_draw
    var image := get_viewport().get_texture().get_image()
    controls.visible = true
    if OS.has_feature("web"):
        JavaScriptBridge.download_buffer(image.save_png_to_buffer(), "character-inspection.png", "image/png")
    else:
        image.save_png("user://character-inspection.png")

extends CanvasLayer

signal world_requested
signal backend_requested
signal move_axis_changed(axis: Vector2)

var backend_root: Control
var world_root: Control
var dialogue_label: Label
var status_label: Label
var _touch_axis := Vector2.ZERO

func _ready() -> void:
    _build_backend()
    _build_world_hud()
    show_backend()

func _build_backend() -> void:
    backend_root = Control.new()
    backend_root.name = "BackendCathedral"
    backend_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    add_child(backend_root)

    var shade := ColorRect.new()
    shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    shade.color = Color(0.025, 0.02, 0.06, 0.93)
    backend_root.add_child(shade)

    var panel := VBoxContainer.new()
    panel.anchor_left = 0.12
    panel.anchor_right = 0.88
    panel.anchor_top = 0.22
    panel.anchor_bottom = 0.74
    panel.add_theme_constant_override("separation", 24)
    backend_root.add_child(panel)

    var title := Label.new()
    title.text = "LUHM OS // BACKEND CATHEDRAL"
    title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    title.add_theme_font_size_override("font_size", 42)
    panel.add_child(title)

    var sub := Label.new()
    sub.text = "NATIVE GODOT SYSTEM COCKPIT · HUMAN CROWN GATE"
    sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    sub.add_theme_font_size_override("font_size", 19)
    panel.add_child(sub)

    var line := Label.new()
    line.text = "Godot 4 hard-architecture dry run\nNeon Riverwalk game runtime isolated behind the Crown."
    line.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    line.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    line.add_theme_font_size_override("font_size", 25)
    panel.add_child(line)

    var enter := Button.new()
    enter.text = "ENTER NEON RIVERWALK"
    enter.custom_minimum_size = Vector2(0.0, 104.0)
    enter.add_theme_font_size_override("font_size", 30)
    enter.pressed.connect(func(): world_requested.emit())
    panel.add_child(enter)

func _build_world_hud() -> void:
    world_root = Control.new()
    world_root.name = "WorldHud"
    world_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    add_child(world_root)

    var backend := Button.new()
    backend.text = "⬡ BACKEND"
    backend.anchor_left = 0.02
    backend.anchor_right = 0.25
    backend.anchor_top = 0.02
    backend.anchor_bottom = 0.07
    backend.add_theme_font_size_override("font_size", 22)
    backend.pressed.connect(func(): backend_requested.emit())
    world_root.add_child(backend)

    status_label = Label.new()
    status_label.text = "NEON RIVERWALK // CROWN AMBER CANDIDATE"
    status_label.anchor_left = 0.28
    status_label.anchor_right = 0.96
    status_label.anchor_top = 0.02
    status_label.anchor_bottom = 0.07
    status_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
    status_label.add_theme_font_size_override("font_size", 21)
    world_root.add_child(status_label)

    dialogue_label = Label.new()
    dialogue_label.anchor_left = 0.08
    dialogue_label.anchor_right = 0.92
    dialogue_label.anchor_top = 0.64
    dialogue_label.anchor_bottom = 0.73
    dialogue_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    dialogue_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
    dialogue_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    dialogue_label.add_theme_font_size_override("font_size", 30)
    dialogue_label.add_theme_color_override("font_color", Color("f8eff8"))
    dialogue_label.add_theme_color_override("font_outline_color", Color("120914"))
    dialogue_label.add_theme_constant_override("outline_size", 9)
    dialogue_label.visible = false
    world_root.add_child(dialogue_label)

    _dpad_button("▲", Vector2(0.0, -1.0), 0.08, 0.78)
    _dpad_button("◀", Vector2(-1.0, 0.0), 0.03, 0.86)
    _dpad_button("▼", Vector2(0.0, 1.0), 0.08, 0.86)
    _dpad_button("▶", Vector2(1.0, 0.0), 0.13, 0.86)

    var camera_hint := Label.new()
    camera_hint.text = "DRAG RIGHT SIDE · CAMERA"
    camera_hint.anchor_left = 0.55
    camera_hint.anchor_right = 0.95
    camera_hint.anchor_top = 0.90
    camera_hint.anchor_bottom = 0.95
    camera_hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
    camera_hint.add_theme_font_size_override("font_size", 18)
    camera_hint.modulate = Color(1, 1, 1, 0.66)
    world_root.add_child(camera_hint)

func _dpad_button(glyph: String, axis: Vector2, left_anchor: float, top_anchor: float) -> void:
    var button := Button.new()
    button.text = glyph
    button.anchor_left = left_anchor
    button.anchor_right = left_anchor + 0.045
    button.anchor_top = top_anchor
    button.anchor_bottom = top_anchor + 0.08
    button.offset_left = 0.0
    button.offset_right = 0.0
    button.offset_top = 0.0
    button.offset_bottom = 0.0
    button.add_theme_font_size_override("font_size", 36)
    button.button_down.connect(func(): _set_touch_axis(axis))
    button.button_up.connect(func(): _set_touch_axis(Vector2.ZERO))
    world_root.add_child(button)

func _set_touch_axis(axis: Vector2) -> void:
    _touch_axis = axis
    move_axis_changed.emit(_touch_axis)

func show_backend() -> void:
    _set_touch_axis(Vector2.ZERO)
    backend_root.visible = true
    world_root.visible = false
    clear_dialogue()

func show_world() -> void:
    backend_root.visible = false
    world_root.visible = true

func show_dialogue(text: String) -> void:
    dialogue_label.text = text
    dialogue_label.visible = not text.is_empty()

func clear_dialogue() -> void:
    if dialogue_label != null:
        dialogue_label.text = ""
        dialogue_label.visible = false

func set_status(text: String) -> void:
    if status_label != null:
        status_label.text = text

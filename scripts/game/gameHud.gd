extends CanvasLayer

signal world_requested
signal backend_requested
signal move_axis_changed(axis: Vector2)

const AUDIT_WORKFLOW_PATH := "res://doctrine/DOCUMENT_MUTATION_AUDIT_WORKFLOW.json"
const AUDIT_SEAL_PATH := "res://doctrine/DOCUMENT_MUTATION_AUDIT_SEAL_20260926.json"

var backend_root: Control
var world_root: Control
var dialogue_label: Label
var status_label: Label
var _touch_axis := Vector2.ZERO
var _scroll: ScrollContainer
var _panel: VBoxContainer
var _back: Button
var _hint: Label
var _audit_switch: CheckButton
var _audit_panel: Label
var _pads: Array[Button] = []
var _axes: Array[Vector2] = [Vector2.UP, Vector2.LEFT, Vector2.DOWN, Vector2.RIGHT]
var _touch_owner := -1
var _touch_button := -1
var _safe := Rect2()

func _ready() -> void:
    _build_backend()
    _build_world_hud()
    get_viewport().size_changed.connect(_refresh_layout)
    show_backend()
    _refresh_layout()

func _label(text: String, font_size: int) -> Label:
    var item := Label.new()
    item.text = text
    item.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    item.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    item.add_theme_font_size_override("font_size", font_size)
    item.add_theme_color_override("font_color", Color("d8eee9"))
    item.mouse_filter = Control.MOUSE_FILTER_IGNORE
    return item

func _build_backend() -> void:
    backend_root = Control.new()
    backend_root.name = "BackendCathedral"
    backend_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    add_child(backend_root)
    var shade := ColorRect.new()
    shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    shade.color = Color(0.018, 0.035, 0.055, 0.78)
    shade.mouse_filter = Control.MOUSE_FILTER_IGNORE
    backend_root.add_child(shade)
    _scroll = ScrollContainer.new()
    _scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
    backend_root.add_child(_scroll)
    _panel = VBoxContainer.new()
    _panel.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    _panel.add_theme_constant_override("separation", 24)
    _scroll.add_child(_panel)
    _panel.add_child(_label("L U H M   /   O S", 48))
    _panel.add_child(_label("C A T H E D R A L   •   0 1", 22))
    _panel.add_child(_label("DETROIT AFTER DARK\nThe river remembers. Lum is waiting.", 26))

    var enter := Button.new()
    enter.name = "EnterWorld"
    enter.text = "ENTER THE RIVERWALK   →"
    enter.custom_minimum_size = Vector2(0, 88)
    enter.add_theme_font_size_override("font_size", 24)
    enter.pressed.connect(func(): world_requested.emit())
    _skin_button(enter, true)
    _panel.add_child(enter)

    _audit_switch = CheckButton.new()
    _audit_switch.name = "AuditSealSwitch"
    _audit_switch.text = "AUDIT / SEAL · READ ONLY"
    _audit_switch.custom_minimum_size = Vector2(0, 88)
    _audit_switch.add_theme_font_size_override("font_size", 22)
    _audit_switch.focus_mode = Control.FOCUS_NONE
    _audit_switch.toggled.connect(_set_audit_panel)
    _panel.add_child(_audit_switch)

    _audit_panel = _label("", 19)
    _audit_panel.name = "AuditSealStatus"
    _audit_panel.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
    _audit_panel.visible = false
    _panel.add_child(_audit_panel)

func _build_world_hud() -> void:
    world_root = Control.new()
    world_root.name = "WorldHud"
    world_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    world_root.mouse_filter = Control.MOUSE_FILTER_IGNORE
    add_child(world_root)
    _back = Button.new()
    _back.text = "‹  CATHEDRAL"
    _back.add_theme_font_size_override("font_size", 22)
    _back.pressed.connect(func(): backend_requested.emit())
    _skin_button(_back)
    world_root.add_child(_back)
    status_label = _label("PROFESSOR  /  CROWN · AMBER", 20)
    world_root.add_child(status_label)
    dialogue_label = _label("", 28)
    dialogue_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
    dialogue_label.add_theme_color_override("font_outline_color", Color("120914"))
    dialogue_label.add_theme_constant_override("outline_size", 8)
    dialogue_label.visible = false
    world_root.add_child(dialogue_label)
    var glyphs := ["▲", "◀", "▼", "▶"]
    for i in range(4):
        var button := Button.new()
        button.text = glyphs[i]
        button.add_theme_font_size_override("font_size", 30)
        button.focus_mode = Control.FOCUS_NONE
        button.button_down.connect(func(): _set_touch_axis(_axes[i]))
        button.button_up.connect(func(): _set_touch_axis(Vector2.ZERO))
        _skin_button(button)
        world_root.add_child(button)
        _pads.append(button)
    _hint = _label("DRAG RIGHT\nCAMERA", 20)
    world_root.add_child(_hint)

func _load_json(path: String) -> Dictionary:
    if not FileAccess.file_exists(path):
        return {}
    var file := FileAccess.open(path, FileAccess.READ)
    if file == null:
        return {}
    var parsed = JSON.parse_string(file.get_as_text())
    if parsed is Dictionary:
        return parsed
    return {}

func _audit_summary() -> String:
    var workflow := _load_json(AUDIT_WORKFLOW_PATH)
    var seal := _load_json(AUDIT_SEAL_PATH)
    var workflow_status := str(workflow.get("status", "UNKNOWN"))
    var seal_status := str(seal.get("status", "UNKNOWN"))
    var source_law := str(workflow.get("source_law", "SOURCE LAW UNKNOWN"))
    var runtime_status := "UNKNOWN"
    var release_status := "UNKNOWN"
    var gate_scope = seal.get("gate_scope", {})
    if gate_scope is Dictionary:
        runtime_status = str(gate_scope.get("runtime", "UNKNOWN"))
        release_status = str(gate_scope.get("release", "UNKNOWN"))
    return "DOC WORKFLOW · %s\nSEAL · %s\nRUNTIME · %s\nRELEASE · %s\nREAD-ONLY COCKPIT VIEW\n%s" % [workflow_status, seal_status, runtime_status, release_status, source_law]

func _set_audit_panel(enabled: bool) -> void:
    if _audit_panel == null:
        return
    if enabled:
        _audit_panel.text = _audit_summary()
    _audit_panel.visible = enabled

func _notification(what: int) -> void:
    if what == NOTIFICATION_APPLICATION_FOCUS_OUT or what == NOTIFICATION_APPLICATION_PAUSED:
        release_touch()

func _input(event: InputEvent) -> void:
    if world_root == null or not world_root.visible:
        return
    if event is InputEventScreenTouch:
        if not event.pressed and event.index == _touch_owner:
            release_touch()
            get_viewport().set_input_as_handled()
        elif event.pressed:
            for i in range(_pads.size()):
                if _pads[i].get_global_rect().has_point(event.position):
                    if _touch_owner == -1:
                        _touch_owner = event.index
                        _touch_button = i
                        _set_touch_axis(_axes[i])
                    get_viewport().set_input_as_handled()
                    return
    elif event is InputEventScreenDrag and event.index == _touch_owner:
        var inside := _pads[_touch_button].get_global_rect().has_point(event.position)
        _set_touch_axis(_axes[_touch_button] if inside else Vector2.ZERO)
        get_viewport().set_input_as_handled()

func release_touch() -> void:
    _touch_owner = -1
    _touch_button = -1
    _set_touch_axis(Vector2.ZERO)

func _refresh_layout() -> void:
    var visible := get_viewport().get_visible_rect()
    var safe := visible
    if OS.has_feature("android"):
        var screen_safe := Rect2(DisplayServer.get_display_safe_area())
        if screen_safe.has_area():
            safe = (get_viewport().get_screen_transform().affine_inverse() * screen_safe).intersection(visible)
    apply_layout(visible.size, safe)

func apply_layout(view_size: Vector2, safe: Rect2) -> void:
    release_touch()
    var bounds := Rect2(Vector2.ZERO, view_size)
    _safe = safe.intersection(bounds)
    if not _safe.has_area():
        _safe = bounds
    var area := _safe.grow(-24.0)
    _scroll.position = area.position
    _scroll.size = area.size
    _back.position = area.position
    _back.size = Vector2(190, 72)
    status_label.position = area.position + Vector2(206, 0)
    status_label.size = Vector2(maxf(area.size.x - 206, 1), 72)
    var step := 88.0
    var origin := Vector2(area.position.x, area.end.y - step * 2.0)
    var cells := [Vector2(1, 0), Vector2(0, 1), Vector2(1, 1), Vector2(2, 1)]
    for i in range(_pads.size()):
        _pads[i].position = origin + cells[i] * step
        _pads[i].size = Vector2(80, 80)
    dialogue_label.position = Vector2(area.position.x, area.end.y - 320)
    dialogue_label.size = Vector2(area.size.x, 128)
    _hint.position = Vector2(area.end.x - 210, area.end.y - 96)
    _hint.size = Vector2(210, 88)

func layout_controls() -> Array[Control]:
    var result: Array[Control] = [_back, status_label, dialogue_label, _hint]
    for button in _pads:
        result.append(button)
    return result

func _set_touch_axis(axis: Vector2) -> void:
    _touch_axis = axis
    move_axis_changed.emit(axis)

func show_backend() -> void:
    release_touch()
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

func _skin_button(button: Button, primary: bool = false) -> void:
    for state in ["normal", "hover", "pressed", "focus"]:
        var skin := StyleBoxFlat.new()
        skin.bg_color = Color("123e46") if primary else Color("10232ee8")
        if state == "pressed":
            skin.bg_color = Color("28616a")
        skin.border_color = Color("73efcf") if primary else Color("487c86")
        skin.set_border_width_all(2 if primary else 1)
        skin.set_corner_radius_all(12)
        skin.content_margin_left = 18
        skin.content_margin_right = 18
        button.add_theme_stylebox_override(state, skin)
    button.add_theme_color_override("font_color", Color("e4fff4"))
    button.add_theme_color_override("font_pressed_color", Color.WHITE)

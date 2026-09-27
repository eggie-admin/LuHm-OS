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
var _dialogue_shell: PanelContainer
var _scroll: ScrollContainer
var _panel: VBoxContainer
var _back: Button
var _quest: Button
var _map: Button
var _context: Button
var _lum: Button
var _lum_menu: PanelContainer
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
    item.mouse_filter = Control.MOUSE_FILTER_IGNORE
    return item

func _panel_style(fill: Color, border: Color, radius: int = 16, border_width: int = 1) -> StyleBoxFlat:
    var style := StyleBoxFlat.new()
    style.bg_color = fill
    style.border_color = border
    style.border_width_left = border_width
    style.border_width_top = border_width
    style.border_width_right = border_width
    style.border_width_bottom = border_width
    style.corner_radius_top_left = radius
    style.corner_radius_top_right = radius
    style.corner_radius_bottom_left = radius
    style.corner_radius_bottom_right = radius
    return style

func _dress_button(button: Button, accent: Color, compact: bool = false) -> void:
    button.focus_mode = Control.FOCUS_NONE
    button.add_theme_color_override("font_color", Color("f7eef8"))
    button.add_theme_color_override("font_hover_color", Color.WHITE)
    button.add_theme_font_size_override("font_size", 16 if compact else 19)
    button.add_theme_stylebox_override("normal", _panel_style(Color(0.035, 0.025, 0.07, 0.82), Color(accent, 0.65), 14, 1))
    button.add_theme_stylebox_override("hover", _panel_style(Color(0.075, 0.045, 0.12, 0.94), Color(accent, 0.95), 14, 2))
    button.add_theme_stylebox_override("pressed", _panel_style(Color(0.12, 0.05, 0.14, 0.98), accent, 14, 2))

func _build_backend() -> void:
    backend_root = Control.new()
    backend_root.name = "BackendCathedral"
    backend_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    add_child(backend_root)

    var shade := ColorRect.new()
    shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    shade.color = Color(0.018, 0.012, 0.045, 0.96)
    shade.mouse_filter = Control.MOUSE_FILTER_IGNORE
    backend_root.add_child(shade)

    _scroll = ScrollContainer.new()
    _scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
    backend_root.add_child(_scroll)

    _panel = VBoxContainer.new()
    _panel.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    _panel.add_theme_constant_override("separation", 20)
    _scroll.add_child(_panel)
    _panel.add_child(_label("LUHM OS // CATHEDRAL", 34))
    _panel.add_child(_label("PROFESSOR HOLDS THE CROWN", 20))
    _panel.add_child(_label("Cathedral Oni Atelier\nGodot runtime candidate · AMBER", 24))

    var enter := Button.new()
    enter.name = "EnterWorld"
    enter.text = "ENTER ONI ATELIER"
    enter.custom_minimum_size = Vector2(0, 82)
    _dress_button(enter, Color("ff4fa3"))
    enter.pressed.connect(func(): world_requested.emit())
    _panel.add_child(enter)

    _audit_switch = CheckButton.new()
    _audit_switch.name = "AuditSealSwitch"
    _audit_switch.text = "AUDIT / SEAL · READ ONLY"
    _audit_switch.custom_minimum_size = Vector2(0, 72)
    _audit_switch.add_theme_font_size_override("font_size", 19)
    _audit_switch.focus_mode = Control.FOCUS_NONE
    _audit_switch.toggled.connect(_set_audit_panel)
    _panel.add_child(_audit_switch)

    _audit_panel = _label("", 17)
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
    _back.text = "CATHEDRAL"
    _dress_button(_back, Color("5fe7ff"), true)
    _back.pressed.connect(func(): backend_requested.emit())
    world_root.add_child(_back)

    _quest = Button.new()
    _quest.text = "◇"
    _quest.tooltip_text = "Quest sigil"
    _dress_button(_quest, Color("ff4fa3"), true)
    _quest.pressed.connect(func(): show_dialogue("QUEST // Reach Lum at the altar. The atelier is the active world milestone."))
    world_root.add_child(_quest)

    _map = Button.new()
    _map.text = "⌖"
    _map.tooltip_text = "Map ping"
    _dress_button(_map, Color("5fe7ff"), true)
    _map.pressed.connect(func(): show_dialogue("MAP // Cathedral nave · Oni Atelier · Riverwalk threshold."))
    world_root.add_child(_map)

    status_label = _label("CROWN · AMBER", 16)
    status_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
    status_label.add_theme_color_override("font_color", Color("d8c8e8"))
    world_root.add_child(status_label)

    _context = Button.new()
    _context.text = "INTERACT"
    _dress_button(_context, Color("ff4fa3"), true)
    _context.pressed.connect(func(): show_dialogue("ATELIER // Context action is bounded to the current world surface."))
    world_root.add_child(_context)

    _lum = Button.new()
    _lum.text = "LUM"
    _lum.tooltip_text = "Lum micro menu"
    _dress_button(_lum, Color("ff4fa3"))
    _lum.pressed.connect(_toggle_lum_menu)
    world_root.add_child(_lum)

    _lum_menu = PanelContainer.new()
    _lum_menu.visible = false
    _lum_menu.add_theme_stylebox_override("panel", _panel_style(Color(0.025, 0.018, 0.06, 0.96), Color("ff4fa3"), 18, 2))
    world_root.add_child(_lum_menu)
    var lum_stack := VBoxContainer.new()
    lum_stack.add_theme_constant_override("separation", 8)
    _lum_menu.add_child(lum_stack)
    var lum_title := _label("LUM // MICRO MENU", 16)
    lum_title.add_theme_color_override("font_color", Color("ff9dce"))
    lum_stack.add_child(lum_title)
    for spec in [
        ["PET", "Lum: Atelier systems are listening. No game state grants admin authority."],
        ["QUEST", "QUEST // Cross the nave and inspect the altar forge."],
    ]:
        var action := Button.new()
        action.text = str(spec[0])
        _dress_button(action, Color("5fe7ff"), true)
        var message := str(spec[1])
        action.pressed.connect(func(): show_dialogue(message))
        lum_stack.add_child(action)
    var crown := Button.new()
    crown.text = "CROWN"
    _dress_button(crown, Color("ff4fa3"), true)
    crown.pressed.connect(func():
        _lum_menu.visible = false
        backend_requested.emit()
    )
    lum_stack.add_child(crown)

    _dialogue_shell = PanelContainer.new()
    _dialogue_shell.visible = false
    _dialogue_shell.mouse_filter = Control.MOUSE_FILTER_IGNORE
    _dialogue_shell.add_theme_stylebox_override("panel", _panel_style(Color(0.018, 0.012, 0.045, 0.92), Color("5fe7ff"), 16, 1))
    world_root.add_child(_dialogue_shell)
    dialogue_label = _label("", 22)
    dialogue_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
    dialogue_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
    dialogue_label.add_theme_color_override("font_color", Color("f5ecf7"))
    dialogue_label.add_theme_constant_override("outline_size", 0)
    _dialogue_shell.add_child(dialogue_label)

    var glyphs := ["▲", "◀", "▼", "▶"]
    for i in range(4):
        var button := Button.new()
        button.text = glyphs[i]
        _dress_button(button, Color("5fe7ff"), true)
        button.modulate.a = 0.78
        button.button_down.connect(func(): _set_touch_axis(_axes[i]))
        button.button_up.connect(func(): _set_touch_axis(Vector2.ZERO))
        world_root.add_child(button)
        _pads.append(button)

    _hint = _label("DRAG RIGHT · CAMERA", 13)
    _hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
    _hint.add_theme_color_override("font_color", Color(0.82, 0.78, 0.9, 0.78))
    world_root.add_child(_hint)

func _toggle_lum_menu() -> void:
    _lum_menu.visible = not _lum_menu.visible

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
        if _lum_menu != null:
            _lum_menu.visible = false

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
    var area := _safe.grow(-18.0)

    _scroll.position = area.position
    _scroll.size = area.size

    _quest.position = area.position
    _quest.size = Vector2(54, 54)
    _map.position = area.position + Vector2(62, 0)
    _map.size = Vector2(54, 54)
    status_label.position = area.position + Vector2(128, 4)
    status_label.size = Vector2(maxf(area.size.x - 272, 1), 46)
    _back.position = Vector2(area.end.x - 128, area.position.y)
    _back.size = Vector2(128, 54)

    var pad_step := 62.0
    var pad_origin := Vector2(area.position.x, area.end.y - pad_step * 2.0)
    var cells := [Vector2(1, 0), Vector2(0, 1), Vector2(1, 1), Vector2(2, 1)]
    for i in range(_pads.size()):
        _pads[i].position = pad_origin + cells[i] * pad_step
        _pads[i].size = Vector2(56, 56)

    _lum.size = Vector2(82, 82)
    _lum.position = Vector2(area.end.x - 82, area.end.y - 82)
    _context.size = Vector2(132, 54)
    _context.position = Vector2(area.end.x - 224, area.end.y - 68)
    _hint.position = Vector2(area.end.x - 244, area.end.y - 116)
    _hint.size = Vector2(244, 28)

    _lum_menu.size = Vector2(minf(220.0, area.size.x * 0.58), 210)
    _lum_menu.position = Vector2(area.end.x - _lum_menu.size.x, area.end.y - 304)

    _dialogue_shell.position = Vector2(area.position.x, area.end.y - 238)
    _dialogue_shell.size = Vector2(area.size.x, 92)

func layout_controls() -> Array[Control]:
    var result: Array[Control] = [_back, _quest, _map, status_label, _context, _lum, _lum_menu, _dialogue_shell, _hint]
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
    if _lum_menu != null:
        _lum_menu.visible = false

func show_world() -> void:
    backend_root.visible = false
    world_root.visible = true

func show_dialogue(text: String) -> void:
    dialogue_label.text = text
    _dialogue_shell.visible = not text.is_empty()

func clear_dialogue() -> void:
    if dialogue_label != null:
        dialogue_label.text = ""
    if _dialogue_shell != null:
        _dialogue_shell.visible = false

func set_status(text: String) -> void:
    if status_label != null:
        status_label.text = text

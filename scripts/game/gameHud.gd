extends CanvasLayer

signal world_requested
signal rehearsal_requested
signal backend_requested
signal world_destination_requested(worldId: String)
signal lum_talk_requested
signal interact_requested
signal move_axis_changed(axis: Vector2)

const CURRENT_SOURCE_TRUTH_PATH := "res://doctrine/currentSourceTruthV3.json"
const GAMEPLAY_CONTRACT_PATH := "res://doctrine/gameplayVerticalSliceV1.json"
const CHARACTER_CANON_PATH := "res://game/canon/CHARACTER_CANON_V1.json"
const COVENANT_PATH := "res://doctrine/everlastingCovenantV1.json"

var backend_root: Control
var world_root: Control
var dialogue_label: Label
var status_label: Label
var quest_label: Label
var summon_card: PanelContainer
var summon_name_label: Label
var summon_state_label: Label
var _summon_timer: Timer
var _touch_axis := Vector2.ZERO
var _scroll: ScrollContainer
var _panel: VBoxContainer
var _back: Button
var _hint: Label
var _world_buttons: Array[Button] = []
var _talk: Button
var _interact: Button
var _interaction_tween: Tween
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

func _build_backend() -> void:
    backend_root = Control.new()
    backend_root.name = "BackendCathedral"
    backend_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    add_child(backend_root)
    var shade := ColorRect.new()
    shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    shade.color = Color(0.025, 0.02, 0.06, 0.93)
    shade.mouse_filter = Control.MOUSE_FILTER_IGNORE
    backend_root.add_child(shade)
    _scroll = ScrollContainer.new()
    _scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
    backend_root.add_child(_scroll)
    _panel = VBoxContainer.new()
    _panel.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    _panel.add_theme_constant_override("separation", 24)
    _scroll.add_child(_panel)
    _panel.add_child(_label("LUHM OS // CATHEDRAL", 34))
    _panel.add_child(_label("PROFESSOR HOLDS THE CROWN", 22))
    _panel.add_child(_label("Lum · Urd · Belldandy · Skuld\nGodot 4 · OperationTitan7", 26))

    var enter := Button.new()
    enter.name = "EnterWorld"
    enter.text = "ENTER NEON RIVERWALK"
    enter.custom_minimum_size = Vector2(0, 88)
    enter.add_theme_font_size_override("font_size", 24)
    enter.pressed.connect(func(): world_requested.emit())
    _panel.add_child(enter)

    var rehearsal := Button.new()
    rehearsal.name = "GoddessRehearsal"
    rehearsal.text = "MEET THE FOUR GODDESSES · REHEARSAL"
    rehearsal.custom_minimum_size = Vector2(0, 76)
    rehearsal.add_theme_font_size_override("font_size", 21)
    rehearsal.pressed.connect(func(): rehearsal_requested.emit())
    _panel.add_child(rehearsal)

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
    _back.text = "CATHEDRAL"
    _back.add_theme_font_size_override("font_size", 22)
    _back.pressed.connect(func(): backend_requested.emit())
    world_root.add_child(_back)
    status_label = _label("SOURCE · PROPOSED GAMEPLAY", 22)
    world_root.add_child(status_label)
    quest_label = _label("FIRST NIGHT CIRCUIT", 19)
    quest_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
    world_root.add_child(quest_label)
    dialogue_label = _label("", 28)
    dialogue_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
    dialogue_label.add_theme_color_override("font_outline_color", Color("120914"))
    dialogue_label.add_theme_constant_override("outline_size", 8)
    dialogue_label.visible = false
    world_root.add_child(dialogue_label)

    summon_card = PanelContainer.new()
    summon_card.name = "OniSummonCard"
    summon_card.visible = false
    summon_card.mouse_filter = Control.MOUSE_FILTER_IGNORE
    world_root.add_child(summon_card)
    var summon_stack := VBoxContainer.new()
    summon_stack.add_theme_constant_override("separation", 6)
    summon_card.add_child(summon_stack)
    summon_name_label = _label("ONI REQUEST", 24)
    summon_name_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
    summon_stack.add_child(summon_name_label)
    summon_state_label = _label("ROUTING ONLY · NO WORKER STARTED", 16)
    summon_state_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
    summon_stack.add_child(summon_state_label)
    _summon_timer = Timer.new()
    _summon_timer.one_shot = true
    _summon_timer.wait_time = 3.2
    _summon_timer.timeout.connect(func(): summon_card.visible = false)
    add_child(_summon_timer)

    var glyphs := ["▲", "◀", "▼", "▶"]
    for i in range(4):
        var button := Button.new()
        button.text = glyphs[i]
        button.add_theme_font_size_override("font_size", 30)
        button.focus_mode = Control.FOCUS_NONE
        button.button_down.connect(func(): _set_touch_axis(_axes[i]))
        button.button_up.connect(func(): _set_touch_axis(Vector2.ZERO))
        world_root.add_child(button)
        _pads.append(button)
    var destinations := [["RIVERWALK", "neonRiverwalk"], ["CATHEDRAL", "cathedral"], ["COFFEE HOUSE", "lumCoffeeHouse"]]
    for destination in destinations:
        var world_button := Button.new()
        world_button.text = destination[0]
        world_button.focus_mode = Control.FOCUS_NONE
        world_button.pressed.connect(func(): world_destination_requested.emit(destination[1]))
        world_root.add_child(world_button)
        _world_buttons.append(world_button)
    _talk = Button.new()
    _talk.text = "TALK TO LUM"
    _talk.focus_mode = Control.FOCUS_NONE
    _talk.pressed.connect(func(): lum_talk_requested.emit())
    world_root.add_child(_talk)
    _interact = Button.new()
    _interact.text = "INTERACT"
    _interact.disabled = true
    _interact.focus_mode = Control.FOCUS_NONE
    _interact.pressed.connect(func(): interact_requested.emit())
    world_root.add_child(_interact)
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
    var source_truth := _load_json(CURRENT_SOURCE_TRUTH_PATH)
    var gameplay := _load_json(GAMEPLAY_CONTRACT_PATH)
    var canon := _load_json(CHARACTER_CANON_PATH)
    var covenant := _load_json(COVENANT_PATH)

    var characters = canon.get("characters", {})
    var character_count := (characters as Dictionary).size() if characters is Dictionary else 0
    var working_lane = source_truth.get("workingDoctrineLane", {})
    var lane_status := str((working_lane as Dictionary).get("status", "UNKNOWN")) if working_lane is Dictionary else "UNKNOWN"

    return "SOURCE TRUTH · %s\nGAMEPLAY · %s\nQUEST LOOP · FIRST NIGHT CIRCUIT\nCHARACTER CANON · %s ENTRIES\nCOVENANT · %s\nWORKING LANE · %s\nINSTALL BOUNDARY · %s\nCROWN · %s" % [
        str(source_truth.get("status", "UNKNOWN")),
        str(gameplay.get("status", "UNKNOWN")),
        character_count,
        str(covenant.get("status", "UNKNOWN")),
        lane_status,
        str(gameplay.get("installBoundary", "UNKNOWN")),
        str(gameplay.get("crownStatus", "UNKNOWN"))
    ]

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
    quest_label.position = area.position + Vector2(0, 216)
    quest_label.size = Vector2(area.size.x, 72)
    # Keep dialogue below the quest row and above touch controls in landscape.
    # The old fixed 128px card overlapped the quest at 720px viewport height.
    var dialogue_top := maxf(area.position.y + 292.0, area.end.y - 320.0)
    dialogue_label.position = Vector2(area.position.x, dialogue_top)
    dialogue_label.size = Vector2(area.size.x, maxf(0.0, minf(112.0, area.end.y - 196.0 - dialogue_top)))
    var summon_width := minf(420.0, area.size.x)
    summon_card.position = Vector2(area.position.x + maxf((area.size.x - summon_width) * 0.5, 0.0), area.end.y - 452.0)
    summon_card.size = Vector2(summon_width, 104)
    var world_width := minf(150.0, maxf((area.size.x - 24.0) / 4.0, 92.0))
    for i in range(_world_buttons.size()):
        _world_buttons[i].position = area.position + Vector2(i * (world_width + 6.0), 78)
        _world_buttons[i].size = Vector2(world_width, 62)
    _talk.position = area.position + Vector2(0, 146)
    _talk.size = Vector2(world_width * 1.25, 62)
    _interact.position = area.position + Vector2(world_width * 1.25 + 8.0, 146)
    _interact.size = Vector2(maxf(world_width * 1.4, 132.0), 62)
    _hint.position = Vector2(area.end.x - 210, area.end.y - 96)
    _hint.size = Vector2(210, 88)

func layout_controls() -> Array[Control]:
    var result: Array[Control] = [_back, status_label, quest_label, dialogue_label, _hint, _talk, _interact]
    result.append_array(_world_buttons)
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
    if summon_card != null:
        summon_card.visible = false
    clear_dialogue()

func show_world() -> void:
    backend_root.visible = false
    world_root.visible = true

func show_oni_request(name: String) -> void:
    var safe_name := name.strip_edges().left(32)
    if safe_name.is_empty():
        safe_name = "UNKNOWN"
    summon_name_label.text = "ONI REQUEST // " + safe_name.to_upper()
    summon_state_label.text = "ROUTING ONLY · NO WORKER STARTED"
    summon_card.visible = true
    if _summon_timer != null:
        _summon_timer.start()
    set_status("ONI REQUEST · %s · ROUTING ONLY" % safe_name.to_upper())

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


func set_interaction_prompt(prompt_value: String, available: bool) -> void:
    if _interact == null:
        return
    _interact.disabled = not available
    _interact.text = prompt_value.to_upper() if available and not prompt_value.is_empty() else "INTERACT"

func nudge_interaction() -> void:
    if _interact == null or _interact.disabled:
        return
    if _interaction_tween != null and _interaction_tween.is_valid():
        _interaction_tween.kill()
    _interact.pivot_offset = _interact.size * 0.5
    _interact.scale = Vector2.ONE
    _interaction_tween = create_tween()
    _interaction_tween.set_trans(Tween.TRANS_BACK)
    _interaction_tween.set_ease(Tween.EASE_OUT)
    _interaction_tween.tween_property(_interact, "scale", Vector2.ONE * 1.10, 0.12)
    _interaction_tween.tween_property(_interact, "scale", Vector2.ONE, 0.18)
    _interaction_tween.tween_property(_interact, "scale", Vector2.ONE * 1.06, 0.10)
    _interaction_tween.tween_property(_interact, "scale", Vector2.ONE, 0.16)

func set_quest(title: String, objective: String, current_step: int, total_steps: int) -> void:
    if quest_label == null:
        return
    quest_label.text = "%s · %d/%d\n%s" % [title.to_upper(), current_step, total_steps, objective]


func set_fast_travel_enabled(enabled: bool) -> void:
    for button in _world_buttons:
        button.disabled = not enabled
        button.tooltip_text = "Complete First Night Circuit to unlock fast travel." if not enabled else "Fast travel"

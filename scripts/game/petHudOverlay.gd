extends CanvasLayer
class_name PetHudOverlay

const PixelSitterScript := preload("res://scripts/game/pixelSitter.gd")

var controller: PetWindowController
var root: Control
var strip: HBoxContainer
var bubble: PanelContainer
var sitter: PixelSitter
var bubble_label: Label
var _message_timer := 0.0

func configure(value: PetWindowController) -> void:
    controller = value
    if is_inside_tree():
        _wire_controller()

func _ready() -> void:
    layer = 90
    _build_ui()
    _wire_controller()
    get_viewport().size_changed.connect(_layout)
    _layout()

func _build_ui() -> void:
    root = Control.new()
    root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    root.mouse_filter = Control.MOUSE_FILTER_IGNORE
    add_child(root)

    strip = HBoxContainer.new()
    strip.name = "PetWinampStrip"
    strip.add_theme_constant_override("separation", 6)
    strip.mouse_filter = Control.MOUSE_FILTER_PASS
    root.add_child(strip)

    var title := Label.new()
    title.text = "👑 LUM PET"
    title.add_theme_font_size_override("font_size", 18)
    strip.add_child(title)

    _button("FULL", PetWindowController.Mode.FULLSCREEN)
    _button("MINI", PetWindowController.Mode.MINI_PLAYER)
    _button("PET", PetWindowController.Mode.PET_INSPECT)
    _button("CHAT", PetWindowController.Mode.CHAT_HEAD)
    _button("BG", PetWindowController.Mode.BACKGROUND)
    _button("X", PetWindowController.Mode.EXITING)

    bubble = PanelContainer.new()
    bubble.name = "PetBubble"
    bubble.mouse_filter = Control.MOUSE_FILTER_STOP
    root.add_child(bubble)

    var box := VBoxContainer.new()
    box.add_theme_constant_override("separation", 4)
    bubble.add_child(box)

    sitter = PixelSitterScript.new() as PixelSitter
    sitter.name = "LumPixelSitter"
    sitter.gui_input.connect(_on_sitter_input)
    box.add_child(sitter)

    bubble_label = Label.new()
    bubble_label.text = "LUM // IDLE"
    bubble_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    bubble_label.add_theme_font_size_override("font_size", 14)
    box.add_child(bubble_label)

func _button(label_text: String, target_mode: int) -> void:
    var b := Button.new()
    b.text = label_text
    b.focus_mode = Control.FOCUS_NONE
    b.custom_minimum_size = Vector2(64, 46)
    b.pressed.connect(func(): _request(target_mode))
    strip.add_child(b)

func _wire_controller() -> void:
    if controller == null:
        return
    if not controller.mode_changed.is_connected(_on_mode_changed):
        controller.mode_changed.connect(_on_mode_changed)
    if not controller.android_bubble_requested.is_connected(_on_android_bubble):
        controller.android_bubble_requested.connect(_on_android_bubble)
    if not controller.android_background_requested.is_connected(_on_android_background):
        controller.android_background_requested.connect(_on_android_background)

func _request(target_mode: int) -> void:
    if controller == null:
        return
    controller.request_mode(target_mode)

func _on_mode_changed(mode_name: String) -> void:
    bubble_label.text = "LUM // " + mode_name
    match mode_name:
        "FULLSCREEN":
            strip.visible = true
            bubble.visible = true
            sitter.set_mood("IDLE")
        "MINI_PLAYER":
            strip.visible = true
            bubble.visible = false
        "PET_INSPECT":
            strip.visible = true
            bubble.visible = true
            sitter.set_mood("ALERT")
        "CHAT_HEAD":
            strip.visible = false
            bubble.visible = true
            sitter.set_mood("IDLE")
        "BACKGROUND":
            strip.visible = false
            bubble.visible = true
            sitter.set_mood("SLEEP")
        "EXITING":
            strip.visible = false
            bubble.visible = false
    _layout()

func _on_android_bubble() -> void:
    _flash("APP BUBBLE // native system bubble adapter pending")

func _on_android_background() -> void:
    _flash("BACKGROUND READY // Android owns process lifetime")

func _on_sitter_input(event: InputEvent) -> void:
    if event is InputEventMouseButton and event.pressed:
        sitter.set_mood("ALERT")
        _flash("♥ PET LUM")
    elif event is InputEventScreenTouch and event.pressed:
        sitter.set_mood("ALERT")
        _flash("♥ PET LUM")

func _flash(text: String) -> void:
    bubble_label.text = text
    _message_timer = 2.4

func _process(delta: float) -> void:
    if _message_timer > 0.0:
        _message_timer -= delta
        if _message_timer <= 0.0 and controller != null:
            _on_mode_changed(controller.mode_label(controller.mode))

func _layout() -> void:
    if root == null:
        return
    var visible := get_viewport().get_visible_rect()
    var safe := visible
    if OS.has_feature("android"):
        var screen_safe := Rect2(DisplayServer.get_display_safe_area())
        if screen_safe.has_area():
            safe = (get_viewport().get_screen_transform().affine_inverse() * screen_safe).intersection(visible)
    if not safe.has_area():
        safe = visible

    strip.position = Vector2(safe.position.x + 12, safe.end.y - 62)
    strip.size = Vector2(maxf(safe.size.x - 24, 1), 50)

    var bubble_size := Vector2(170, 190)
    bubble.size = bubble_size
    bubble.position = Vector2(safe.end.x - bubble_size.x - 12, safe.position.y + 84)

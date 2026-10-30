extends CanvasLayer
## K9000 macOS native cockpit candidate.
## Shared Godot world remains the engine; this desktop shell does not claim
## UVC capture, cloud inference, private art, or release authority.
signal world_requested

const BACKGROUND := Color("#080711")
const PANEL := Color("#181327")
const MUTED := Color("#b9a9c8")
const PINK := Color("#ff48ab")
const CYAN := Color("#73dfff")

func _ready() -> void:
    layer = 100
    _build_cockpit()

func _make_label(text: String, size: int, ink: Color) -> Label:
    var label := Label.new()
    label.text = text
    label.add_theme_font_size_override("font_size", size)
    label.add_theme_color_override("font_color", ink)
    label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    return label

func _panel() -> PanelContainer:
    var panel := PanelContainer.new()
    var style := StyleBoxFlat.new()
    style.bg_color = PANEL
    style.border_color = Color("#9b4b8a")
    style.border_width_left = 1
    style.border_width_top = 1
    style.border_width_right = 1
    style.border_width_bottom = 1
    style.corner_radius_top_left = 14
    style.corner_radius_top_right = 14
    style.corner_radius_bottom_left = 14
    style.corner_radius_bottom_right = 14
    style.content_margin_left = 22.0
    style.content_margin_right = 22.0
    style.content_margin_top = 17.0
    style.content_margin_bottom = 17.0
    panel.add_theme_stylebox_override("panel", style)
    return panel

func _build_cockpit() -> void:
    var root := Control.new()
    add_child(root)
    root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    root.mouse_filter = Control.MOUSE_FILTER_STOP

    var background := ColorRect.new()
    root.add_child(background)
    background.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    background.color = BACKGROUND
    background.mouse_filter = Control.MOUSE_FILTER_IGNORE

    var inset := MarginContainer.new()
    root.add_child(inset)
    inset.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    inset.add_theme_constant_override("margin_left", 28)
    inset.add_theme_constant_override("margin_right", 28)
    inset.add_theme_constant_override("margin_top", 22)
    inset.add_theme_constant_override("margin_bottom", 22)

    var stack := VBoxContainer.new()
    stack.add_theme_constant_override("separation", 19)
    inset.add_child(stack)

    var header := HBoxContainer.new()
    header.add_theme_constant_override("separation", 16)
    stack.add_child(header)
    header.add_child(_make_label("◇ K9000", 30, PINK))
    header.add_child(_make_label("LuHm-OS  /  CROWN CATHEDRAL", 13, CYAN))
    var spacer := Control.new()
    spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    header.add_child(spacer)
    header.add_child(_make_label("JACOB CREATOR  ·  FAMILY SAFE", 12, CYAN))

    var hero := _panel()
    hero.size_flags_vertical = Control.SIZE_EXPAND_FILL
    stack.add_child(hero)
    var hero_row := HBoxContainer.new()
    hero_row.add_theme_constant_override("separation", 32)
    hero.add_child(hero_row)
    var hero_content := VBoxContainer.new()
    hero_content.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    hero_content.add_theme_constant_override("separation", 14)
    hero_row.add_child(hero_content)
    hero_content.add_child(_make_label("PRIVATE · OFFLINE-FIRST · CANDIDATE", 11, CYAN))
    hero_content.add_child(_make_label("CREATE THE IMPOSSIBLE.", 37, PINK))
    hero_content.add_child(_make_label(
        "One cockpit for worlds, art, camera work and local AI.\n" +
        "No camera stream, model, cloud account or private asset is active.", 16, MUTED))
    var go := Button.new()
    go.text = "ENTER GODOT WORLD  ↗"
    go.custom_minimum_size = Vector2(250, 51)
    go.pressed.connect(func() -> void: world_requested.emit())
    hero_content.add_child(go)
    var emblem := _make_label("✧", 118, PINK)
    emblem.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    emblem.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
    emblem.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    hero_row.add_child(emblem)

    var tiles := HBoxContainer.new()
    tiles.add_theme_constant_override("separation", 16)
    stack.add_child(tiles)
    _add_tile(tiles, "CHARACTER FORGE", "Original art + rigging", "ASSETS PENDING")
    _add_tile(tiles, "CAMERA MATRIX", "USB devices / six-camera goal", "DEVICE PROOF PENDING")
    _add_tile(tiles, "HEADLESS AI", "LiteRT-LM adapter", "MODEL UNCONFIGURED")
    stack.add_child(_make_label(
        "MACOS DEVELOPMENT CANDIDATE  ·  NO RECORDING  ·  NO PUBLIC SIGNING  ·  CROWN STOP",
        11, MUTED))

func _add_tile(parent: HBoxContainer, title: String, subtitle: String, state: String) -> void:
    var tile := _panel()
    tile.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    parent.add_child(tile)
    var content := VBoxContainer.new()
    content.add_theme_constant_override("separation", 7)
    tile.add_child(content)
    content.add_child(_make_label(title, 19, CYAN))
    content.add_child(_make_label(subtitle, 14, MUTED))
    content.add_child(_make_label(state, 11, PINK))

extends CanvasLayer

const ACTIVITY_DOCTRINE_PATH := "res://doctrine/chatActivityPresentationV1.json"

var activity_root: Control
var activity_label: Label
var stage_label: Label
var progress_bar: ProgressBar
var spinner_label: Label
var spinner_phase := 0.0

func _ready() -> void:
    _build_activity_view()
    set_process(true)
    show_idle()

func _process(delta: float) -> void:
    if activity_root == null or not activity_root.visible:
        return
    if progress_bar != null and progress_bar.indeterminate:
        spinner_phase += delta * 5.0
        var glyphs := ["◇", "◆", "✦", "✧"]
        spinner_label.text = glyphs[int(spinner_phase) % glyphs.size()]

func _build_activity_view() -> void:
    activity_root = Control.new()
    activity_root.name = "LuHmActivityLoading"
    activity_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    add_child(activity_root)

    var shade := ColorRect.new()
    shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    shade.color = Color(0.025, 0.02, 0.06, 0.86)
    activity_root.add_child(shade)

    var panel := VBoxContainer.new()
    panel.set_anchors_preset(Control.PRESET_CENTER)
    panel.position = Vector2(-260, -120)
    panel.size = Vector2(520, 240)
    panel.add_theme_constant_override("separation", 18)
    activity_root.add_child(panel)

    spinner_label = Label.new()
    spinner_label.text = "◇"
    spinner_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    spinner_label.add_theme_font_size_override("font_size", 44)
    panel.add_child(spinner_label)

    activity_label = Label.new()
    activity_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    activity_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    activity_label.add_theme_font_size_override("font_size", 26)
    panel.add_child(activity_label)

    stage_label = Label.new()
    stage_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    stage_label.add_theme_font_size_override("font_size", 18)
    panel.add_child(stage_label)

    progress_bar = ProgressBar.new()
    progress_bar.min_value = 0
    progress_bar.max_value = 100
    progress_bar.show_percentage = true
    panel.add_child(progress_bar)

func present_activity(activity: Dictionary) -> void:
    var label := str(activity.get("label", "Working…"))
    var stage_id := str(activity.get("stageId", activity.get("eventType", "stageChanged")))
    var progress = activity.get("progress", null)
    activity_label.text = label
    stage_label.text = stage_id
    if progress is float or progress is int:
        progress_bar.indeterminate = false
        progress_bar.value = clampf(float(progress), 0.0, 100.0)
    else:
        progress_bar.indeterminate = true
    activity_root.visible = true

func show_idle() -> void:
    activity_label.text = "Lum is standing by."
    stage_label.text = "idle"
    progress_bar.indeterminate = true
    activity_root.visible = false

func finish_activity(label: String = "Ready") -> void:
    activity_label.text = label
    stage_label.text = "taskComplete"
    progress_bar.indeterminate = false
    progress_bar.value = 100.0

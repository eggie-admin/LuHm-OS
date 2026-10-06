extends CanvasLayer

const SOURCE_SHA := "6427357afccb76c085a4d7632e1310f9a27ccad0"
const CAST_BUILD_SHA := "f8a9acb22257f324187fcc9f0dc822f8ea93c5a1"
const CAST_RUN := "36969799620"

var progress := 0.0
var progress_bar: ProgressBar
var status: Label

func _ready() -> void:
    var root := VBoxContainer.new()
    root.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
    root.custom_minimum_size = Vector2(620, 280)
    add_child(root)
    var title := Label.new()
    title.text = "OPERATION TITAN7 // WAR NEVER CHANGES"
    title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    title.add_theme_font_size_override("font_size", 28)
    root.add_child(title)
    var milestone := Label.new()
    milestone.text = "MILESTONE: GODOT 4 CURRENT-DOCTRINE GAME SOURCE"
    milestone.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    root.add_child(milestone)
    progress_bar = ProgressBar.new()
    progress_bar.max_value = 100
    progress_bar.value = 0
    progress_bar.custom_minimum_size = Vector2(620, 48)
    root.add_child(progress_bar)
    status = Label.new()
    status.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    root.add_child(status)
    var receipt := Label.new()
    receipt.text = "Titan7 main %s\nPrior CAST build %s · run %s\nProfessor holds the Crown" % [SOURCE_SHA.substr(0,8), CAST_BUILD_SHA.substr(0,8), CAST_RUN]
    receipt.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    root.add_child(receipt)

func _process(delta: float) -> void:
    if progress >= 100.0:
        return
    progress = minf(100.0, progress + delta * 22.0)
    progress_bar.value = progress
    status.text = _stage_for(progress)

func _stage_for(value: float) -> String:
    if value < 16: return "INGEST // protected references"
    if value < 33: return "MUTATE // original character canon"
    if value < 50: return "COMPILE // Godot source"
    if value < 67: return "TEST // static + runtime gates"
    if value < 84: return "PACKAGE // candidate only"
    if value < 100: return "TITAN7 // cathedral synchronization"
    return "100% // REWARD UNLOCKED"

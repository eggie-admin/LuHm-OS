extends Node3D
## Self-contained PRIVATE creative rehearsal. Existing gameplay remains untouched.
## Godot's original CathedralWorld builds the real scene geometry and Lum socket.

const CathedralWorldScript := preload("res://scripts/game/cathedralWorld.gd")
const FinalBossScript := preload("res://scripts/game/witchingHourFinalBoss.gd")
const MAIN_SCENE := "res://scenes/Main.tscn"

var _cathedral: Node3D
var _cue_label: Label
var _cast_button: Button
var _casting := false

func _ready() -> void:
    _cathedral = CathedralWorldScript.new()
    _cathedral.name = "CathedralWorld"
    add_child(_cathedral)

    var camera := Camera3D.new()
    camera.name = "WitchingHourCamera"
    camera.position = Vector3(0.0, 4.2, 8.5)
    add_child(camera)
    camera.look_at(Vector3(0.0, 2.6, -12.4))
    camera.current = true

    var interface := CanvasLayer.new()
    interface.name = "CastingHud"
    add_child(interface)
    var canvas := Control.new()
    canvas.name = "SafeControls"
    canvas.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    interface.add_child(canvas)

    _cue_label = Label.new()
    _cue_label.name = "CueLabel"
    _cue_label.text = "WITCHING HOUR · PRIVATE REHEARSAL"
    _cue_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    _cue_label.anchor_left = 0.02
    _cue_label.anchor_right = 0.98
    _cue_label.anchor_top = 0.05
    _cue_label.anchor_bottom = 0.17
    _cue_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    _cue_label.add_theme_font_size_override("font_size", 23)
    canvas.add_child(_cue_label)

    var actions := HBoxContainer.new()
    actions.name = "Actions"
    actions.anchor_left = 0.04
    actions.anchor_right = 0.96
    actions.anchor_top = 0.80
    actions.anchor_bottom = 0.96
    actions.add_theme_constant_override("separation", 16)
    canvas.add_child(actions)

    _cast_button = Button.new()
    _cast_button.name = "CastFourFlames"
    _cast_button.text = "CAST · FINAL FORM"
    _cast_button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    _cast_button.pressed.connect(start_cast)
    actions.add_child(_cast_button)

    var back := Button.new()
    back.name = "ReturnToCathedral"
    back.text = "BACK"
    back.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    back.pressed.connect(return_to_main)
    actions.add_child(back)

func start_cast() -> void:
    if _casting or _cathedral == null:
        return
    _casting = true
    _cast_button.disabled = true
    var overlay := FinalBossScript.new()
    overlay.name = "WitchingHourCast"
    _cathedral.add_child(overlay)
    overlay.cue_changed.connect(_on_cue)
    overlay.rehearsal_finished.connect(_on_finish)
    overlay.cast()

func _on_cue(label: String) -> void:
    if _cue_label != null:
        _cue_label.text = label

func _on_finish() -> void:
    _casting = false
    if _cast_button != null:
        _cast_button.disabled = false
        _cast_button.text = "RECAST · FINAL FORM"

func return_to_main() -> void:
    get_tree().change_scene_to_file(MAIN_SCENE)

func _unhandled_input(event: InputEvent) -> void:
    if event.is_action_pressed("ui_cancel"):
        get_viewport().set_input_as_handled()
        return_to_main()

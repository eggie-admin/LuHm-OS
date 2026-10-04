extends Node

signal event_emitted(event_name: String)

var director: Node
var player: CharacterBody3D
var world: Node3D
var hud: CanvasLayer
var _configured := false

func configure(director_node: Node, player_node: CharacterBody3D, world_node: Node3D, hud_node: CanvasLayer) -> void:
    director = director_node
    player = player_node
    world = world_node
    hud = hud_node
    director.beat_started.connect(_on_beat_started)
    director.cutscene_finished.connect(_on_finished)
    director.cutscene_cancelled.connect(_on_cancelled)
    director.cutscene_failed.connect(_on_failed)
    _configured = true

func play_path(path: String) -> void:
    if not _configured:
        push_warning("CutsceneBridge is not configured")
        return
    var document := _load_document(path)
    if document.is_empty():
        _on_failed("cutscene document unavailable: %s" % path)
        return
    await director.play_cutscene(document)

func cancel() -> void:
    if director != null and director.is_running():
        director.cancel()

func restore_now() -> void:
    if hud != null:
        hud.clear_dialogue()
    if world != null:
        world.restore_lum()
        world.set_lum_expression("neutral", 0.0)
    if player != null:
        player.restore_camera(0.0)
        player.set_controls_locked(false)

func _load_document(path: String) -> Dictionary:
    if not FileAccess.file_exists(path):
        return {}
    var decoded = JSON.parse_string(FileAccess.get_file_as_string(path))
    return decoded if decoded is Dictionary else {}

func _on_beat_started(beat: Dictionary) -> void:
    var beat_type := str(beat.get("type", ""))
    var duration := maxf(float(beat.get("duration", 0.0)), 0.0)
    match beat_type:
        "lock_player":
            player.set_controls_locked(true)
        "camera_move":
            player.focus_camera(world.get_lum_focus_position(), duration)
        "lum_beacon_pulse":
            world.pulse_lum(duration)
        "dialogue":
            var text := str(beat.get("dialogue", ""))
            hud.show_dialogue(text)
            world.set_lum_expression("talk", 0.55)
            var event_name := str(beat.get("event", ""))
            if not event_name.is_empty():
                event_emitted.emit(event_name)
        "restore":
            hud.clear_dialogue()
            world.set_lum_expression("neutral", 0.0)
            world.restore_lum()
            player.restore_camera(duration)

func _on_finished(_cutscene_id: String) -> void:
    restore_now()

func _on_cancelled(_cutscene_id: String) -> void:
    restore_now()

func _on_failed(reason: String) -> void:
    push_warning("LuHm cutscene failed: %s" % reason)
    restore_now()

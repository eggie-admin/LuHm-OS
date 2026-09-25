extends Node

signal beat_started(beat: Dictionary)
signal beat_finished(beat_id: String)
signal cutscene_finished(cutscene_id: String)
signal cutscene_cancelled(cutscene_id: String)
signal cutscene_failed(reason: String)

const ALLOWED_TYPES := {
    "lock_player": true,
    "camera_move": true,
    "lum_beacon_pulse": true,
    "dialogue": true,
    "restore": true,
}

var _cancelled := false
var _running := false
var _active_cutscene_id := ""

func is_running() -> bool:
    return _running

func play_cutscene(document: Dictionary) -> void:
    if _running:
        cutscene_failed.emit("cutscene already running")
        return
    if not document.has("beats") or not document["beats"] is Array:
        cutscene_failed.emit("cutscene beats missing")
        return

    _cancelled = false
    _running = true
    _active_cutscene_id = str(document.get("id", "unnamed"))

    for raw_beat in document["beats"]:
        if _cancelled:
            _finish_cancelled()
            return
        if not raw_beat is Dictionary:
            _finish_failed("beat must be a Dictionary")
            return

        var beat: Dictionary = raw_beat
        var beat_type := str(beat.get("type", ""))
        if not ALLOWED_TYPES.has(beat_type):
            _finish_failed("unsupported beat type: %s" % beat_type)
            return

        beat_started.emit(beat)
        var duration := maxf(float(beat.get("duration", 0.0)), 0.0)
        if duration > 0.0:
            await get_tree().create_timer(duration).timeout
        beat_finished.emit(str(beat.get("id", "beat")))

    if _cancelled:
        _finish_cancelled()
        return

    var finished_id := _active_cutscene_id
    _running = false
    _active_cutscene_id = ""
    cutscene_finished.emit(finished_id)

func cancel() -> void:
    if _running:
        _cancelled = true

func _finish_cancelled() -> void:
    var cancelled_id := _active_cutscene_id
    _running = false
    _active_cutscene_id = ""
    cutscene_cancelled.emit(cancelled_id)

func _finish_failed(reason: String) -> void:
    _running = false
    _active_cutscene_id = ""
    cutscene_failed.emit(reason)

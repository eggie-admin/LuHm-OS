extends Area3D
## Procedural, rights-safe story hotspot. Scanned by the existing Godot proximity system.
var zone_id := ""
var zone_name := ""
var story_beat := ""
var _active := false

func configure(id: String, title: String, beat: String) -> void:
    zone_id = id
    zone_name = title.left(80)
    story_beat = beat.left(220)

func get_event_name() -> String:
    return "aramoor:" + zone_id

func get_prompt() -> String:
    return "INSPECT"

func set_active(enabled: bool) -> void:
    _active = enabled

func is_available() -> bool:
    return _active and not zone_id.is_empty()

func get_story_line() -> String:
    return zone_name + ": " + story_beat

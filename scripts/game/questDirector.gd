extends Node

signal quest_changed(title: String, objective: String, current_step: int, total_steps: int)
signal quest_completed(quest_id: String, message: String)

var _quest: Dictionary = {}
var _step_index := 0
var _complete := false

func load_quest(path: String) -> bool:
    if not FileAccess.file_exists(path):
        push_warning("Quest document missing: %s" % path)
        return false
    var parsed = JSON.parse_string(FileAccess.get_file_as_string(path))
    if not parsed is Dictionary:
        push_warning("Quest document is not a Dictionary: %s" % path)
        return false
    var steps = parsed.get("steps", [])
    if not steps is Array or steps.is_empty():
        push_warning("Quest has no steps: %s" % path)
        return false
    _quest = parsed.duplicate(true)
    _step_index = 0
    _complete = false
    _emit_state()
    return true

func is_loaded() -> bool:
    return not _quest.is_empty()

func is_complete() -> bool:
    return _complete

func current_step() -> Dictionary:
    var steps = _quest.get("steps", [])
    if not steps is Array or _step_index < 0 or _step_index >= steps.size():
        return {}
    var value = steps[_step_index]
    return value.duplicate(true) if value is Dictionary else {}

func current_world_id() -> String:
    return str(current_step().get("worldId", ""))

func current_event() -> String:
    return str(current_step().get("event", ""))

func accepts_event(event_name: String) -> bool:
    return not _complete and event_name == current_event()

func apply_event(event_name: String) -> Dictionary:
    if _complete:
        return {
            "accepted": false,
            "complete": true,
            "message": str(_quest.get("completion", {}).get("message", "Quest already complete."))
        }

    var step := current_step()
    if step.is_empty() or event_name != str(step.get("event", "")):
        return {
            "accepted": false,
            "complete": false,
            "message": "That is not the current objective."
        }

    var response := str(step.get("response", ""))
    _step_index += 1
    var steps = _quest.get("steps", [])
    if _step_index >= steps.size():
        _complete = true
        var completion = _quest.get("completion", {})
        var completion_message := str(completion.get("message", response))
        quest_completed.emit(str(_quest.get("questId", "quest")), completion_message)
        return {
            "accepted": true,
            "complete": true,
            "message": completion_message
        }

    _emit_state()
    return {
        "accepted": true,
        "complete": false,
        "message": response,
        "nextWorldId": current_world_id()
    }

func snapshot() -> Dictionary:
    return {
        "questId": str(_quest.get("questId", "")),
        "stepIndex": _step_index,
        "complete": _complete,
        "currentStep": current_step()
    }

func _emit_state() -> void:
    var step := current_step()
    var steps = _quest.get("steps", [])
    quest_changed.emit(
        str(_quest.get("title", "Quest")),
        str(step.get("objective", "")),
        _step_index + 1,
        steps.size()
    )

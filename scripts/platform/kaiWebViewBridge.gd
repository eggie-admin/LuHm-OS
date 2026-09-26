extends Node

signal world_requested
signal toy_action_requested(action: String)
signal move_axis_changed(axis: Vector2)
signal camera_delta_requested(delta: Vector2)
signal quit_requested

const WINDOW_MODES := ["bubble", "compact", "panel", "fullscreen", "hidden"]
const TOY_ACTIONS := ["pet_lum", "oni_pop", "crown_pulse"]
var _plugin = null

func _ready() -> void:
    if OS.get_name() != "Android":
        return
    if not Engine.has_singleton("KAIWebView"):
        push_warning("KAIWebView singleton unavailable; native HUD fallback remains active")
        return
    _plugin = Engine.get_singleton("KAIWebView")
    if _plugin.has_signal("bridge_message"):
        _plugin.bridge_message.connect(_on_bridge_message)

func is_available() -> bool:
    return _plugin != null

func show_cockpit(mode: String = "compact") -> void:
    if _plugin == null:
        return
    _plugin.showCockpit()
    set_mode(mode)

func hide_cockpit() -> void:
    if _plugin != null:
        _plugin.hideCockpit()

func set_mode(mode: String) -> void:
    if _plugin != null and mode in WINDOW_MODES:
        _plugin.setCockpitMode(mode)

func post_reply(reply: Dictionary) -> void:
    if _plugin != null:
        _plugin.postToCockpit(JSON.stringify(reply))

func _on_bridge_message(raw: String) -> void:
    var parsed = JSON.parse_string(raw)
    if typeof(parsed) != TYPE_DICTIONARY:
        return
    if String(parsed.get("schema", "")) != "luhm.bridge.v1":
        return
    var message_type := String(parsed.get("type", ""))
    var payload = parsed.get("payload", {})
    if not payload is Dictionary:
        payload = {}

    match message_type:
        "world.show":
            world_requested.emit()
        "toy.action":
            var action := String(payload.get("action", ""))
            if action in TOY_ACTIONS:
                toy_action_requested.emit(action)
        "input.axis":
            var axis := Vector2(
                clampf(float(payload.get("x", 0.0)), -1.0, 1.0),
                clampf(float(payload.get("y", 0.0)), -1.0, 1.0)
            )
            move_axis_changed.emit(axis)
        "camera.delta":
            var delta := Vector2(
                clampf(float(payload.get("dx", 0.0)), -120.0, 120.0),
                clampf(float(payload.get("dy", 0.0)), -120.0, 120.0)
            )
            camera_delta_requested.emit(delta)
        "window.mode":
            var mode := String(payload.get("mode", ""))
            if mode in WINDOW_MODES:
                set_mode(mode)
        "app.quit":
            quit_requested.emit()
        "chat.send":
            var professor_message := String(payload.get("message", "")).left(320)
            post_reply({
                "schema": "luhm.bridge.reply.v1",
                "type": "chat.reply",
                "payload": {
                    "speaker": "Lum",
                    "message": "WebGlass bridge online. Godot owns the world; this floating glass owns the controls. Received: " + professor_message
                }
            })
        _:
            pass

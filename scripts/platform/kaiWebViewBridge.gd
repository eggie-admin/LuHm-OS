extends Node

signal world_requested
signal toy_action_requested(action: String)
signal ritual_requested(ritual_id: String)
signal move_axis_changed(axis: Vector2)
signal camera_delta_requested(delta: Vector2)
signal quit_requested
signal avatar_tune_requested(key: String, value: float)
signal avatar_reset_requested
signal avatar_inspect_requested

const DoctrineGateScript := preload("res://scripts/core/doctrineGate.gd")

var _plugin = null
var _doctrine = DoctrineGateScript.new()

func _ready() -> void:
    if _doctrine.get_parent() == null:
        add_child(_doctrine)
    if not _doctrine.is_valid():
        push_error("LuHm WebGlass bridge disabled: doctrine gate invalid")
        return
    if OS.get_name() != "Android":
        return
    if not Engine.has_singleton("KAIWebView"):
        push_warning("KAIWebView singleton unavailable; native HUD fallback remains active")
        return
    _plugin = Engine.get_singleton("KAIWebView")
    if _plugin.has_signal("bridge_message"):
        _plugin.bridge_message.connect(_on_bridge_message)

func is_available() -> bool:
    return _plugin != null and _doctrine.is_valid()

func get_allowed_rituals() -> Array:
    return _doctrine.get_allowed_rituals()

func show_cockpit(mode: String = "compact") -> void:
    if _plugin == null or not _doctrine.allows_window_mode(mode):
        return
    _plugin.showCockpit()
    set_mode(mode)

func hide_cockpit() -> void:
    if _plugin != null:
        _plugin.hideCockpit()

func set_mode(mode: String) -> void:
    if _plugin != null and _doctrine.allows_window_mode(mode):
        _plugin.setCockpitMode(mode)

func post_reply(reply: Dictionary) -> void:
    if _plugin != null:
        _plugin.postToCockpit(JSON.stringify(reply))

func _reject(message_type: String, reason: String) -> void:
    post_reply({
        "schema": "luhm.bridge.reply.v1",
        "type": "bridge.rejected",
        "payload": {
            "message_type": message_type,
            "reason": reason,
            "doctrine_valid": _doctrine.is_valid()
        }
    })

func _on_bridge_message(raw: String) -> void:
    if not _doctrine.is_valid():
        _reject("unknown", "doctrine_invalid")
        return

    var parsed = JSON.parse_string(raw)
    if typeof(parsed) != TYPE_DICTIONARY:
        _reject("unknown", "malformed_json")
        return
    if String(parsed.get("schema", "")) != "luhm.bridge.v1":
        _reject(String(parsed.get("type", "unknown")), "schema_mismatch")
        return

    var message_type := String(parsed.get("type", ""))
    if not _doctrine.allows_message_type(message_type):
        _reject(message_type, "message_type_not_allowed")
        return

    var payload = parsed.get("payload", {})
    if typeof(payload) != TYPE_DICTIONARY:
        payload = {}

    match message_type:
        "system.capabilities":
            post_reply({
                "schema": "luhm.bridge.reply.v1",
                "type": "system.capabilities",
                "payload": _doctrine.snapshot()
            })
        "world.show":
            world_requested.emit()
        "toy.action":
            var action := String(payload.get("action", ""))
            if _doctrine.allows_toy_action(action):
                toy_action_requested.emit(action)
            else:
                _reject(message_type, "toy_action_not_allowed")
        "ritual.start":
            var ritual_id := String(payload.get("ritual", ""))
            if _doctrine.allows_ritual(ritual_id):
                ritual_requested.emit(ritual_id)
            else:
                _reject(message_type, "ritual_not_allowed")
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
            if _doctrine.allows_window_mode(mode):
                set_mode(mode)
            else:
                _reject(message_type, "window_mode_not_allowed")
        "avatar.tune":
            var key := String(payload.get("key", ""))
            if _doctrine.allows_avatar_slider(key):
                avatar_tune_requested.emit(key, clampf(float(payload.get("value", 0.5)), 0.0, 1.0))
            else:
                _reject(message_type, "avatar_slider_not_allowed")
        "avatar.reset":
            avatar_reset_requested.emit()
        "avatar.inspect":
            avatar_inspect_requested.emit()
        "app.quit":
            quit_requested.emit()
        "chat.send":
            var professor_message := String(payload.get("message", "")).left(320)
            post_reply({
                "schema": "luhm.bridge.reply.v1",
                "type": "chat.reply",
                "payload": {
                    "speaker": "Lum",
                    "state": "LOCAL_BRIDGE_ONLY",
                    "persisted": false,
                    "message": "Cathedral bridge received %d characters. Local KAI/Ollama remains a separate Crown-gated companion." % professor_message.length()
                }
            })

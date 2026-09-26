extends Node

var _plugin = null

func _ready() -> void:
    if OS.get_name() != "Android":
        return
    if not Engine.has_singleton("KAIWebView"):
        push_warning("KAIWebView singleton unavailable")
        return
    _plugin = Engine.get_singleton("KAIWebView")
    if _plugin.has_signal("bridge_message"):
        _plugin.bridge_message.connect(_on_bridge_message)

func show_cockpit() -> void:
    if _plugin != null:
        _plugin.showCockpit()

func hide_cockpit() -> void:
    if _plugin != null:
        _plugin.hideCockpit()

func _on_bridge_message(raw: String) -> void:
    var parsed = JSON.parse_string(raw)
    if typeof(parsed) != TYPE_DICTIONARY:
        return
    var message_type := String(parsed.get("type", ""))
    if message_type == "chat.send":
        var payload = parsed.get("payload", {})
        var professor_message := String(payload.get("message", ""))
        var reply := {
            "schema": "luhm.bridge.reply.v1",
            "type": "chat.reply",
            "payload": {
                "speaker": "Lum",
                "message": "Native Cathedral bridge online. Ollama handoff remains external until paired. Received: " + professor_message.left(160)
            }
        }
        _plugin.postToCockpit(JSON.stringify(reply))

extends Node

const DOCTRINE_PATH := "res://doctrine/runtimeDoctrine-20260926.json"
const EXPECTED_SCHEMA := "luhm-os.runtime-doctrine.v1"

var _doc: Dictionary = {}
var _valid := false

func _init() -> void:
    _load_doctrine()

func is_valid() -> bool:
    return _valid

func source_law() -> String:
    if not _valid:
        return ""
    var source = _doc.get("source", {})
    if typeof(source) != TYPE_DICTIONARY:
        return ""
    return String(source.get("source_law", ""))

func get_allowed_rituals() -> Array:
    return _capability_array("rituals")

func get_allowed_toy_actions() -> Array:
    return _capability_array("toy_actions")

func get_allowed_window_modes() -> Array:
    return _capability_array("window_modes")

func get_allowed_avatar_sliders() -> Array:
    return _capability_array("avatar_sliders")

func get_allowed_message_types() -> Array:
    return _capability_array("message_types")

func allows_ritual(value: String) -> bool:
    return value in get_allowed_rituals()

func allows_toy_action(value: String) -> bool:
    return value in get_allowed_toy_actions()

func allows_window_mode(value: String) -> bool:
    return value in get_allowed_window_modes()

func allows_avatar_slider(value: String) -> bool:
    return value in get_allowed_avatar_sliders()

func allows_message_type(value: String) -> bool:
    return value in get_allowed_message_types()

func snapshot() -> Dictionary:
    return {
        "valid": _valid,
        "schema": EXPECTED_SCHEMA if _valid else "invalid",
        "crown": "Professor" if _valid else "none",
        "source_law": source_law(),
        "capabilities": {
            "rituals": get_allowed_rituals(),
            "toy_actions": get_allowed_toy_actions(),
            "window_modes": get_allowed_window_modes(),
            "avatar_sliders": get_allowed_avatar_sliders(),
            "message_types": get_allowed_message_types()
        },
        "constraints": {
            "network": "dark",
            "generic_shell": false,
            "filesystem_bridge": false,
            "eval_bridge": false,
            "root": false,
            "persistent_ritual_mutation": false
        }
    }

func _capability_array(key: String) -> Array:
    if not _valid:
        return []
    var runtime = _doc.get("runtime", {})
    if typeof(runtime) != TYPE_DICTIONARY:
        return []
    var bridge = runtime.get("bridge", {})
    if typeof(bridge) != TYPE_DICTIONARY:
        return []
    var capabilities = bridge.get("capabilities", {})
    if typeof(capabilities) != TYPE_DICTIONARY:
        return []
    var values = capabilities.get(key, [])
    if typeof(values) != TYPE_ARRAY:
        return []
    return values.duplicate()

func _load_doctrine() -> void:
    _doc = {}
    _valid = false
    if not FileAccess.file_exists(DOCTRINE_PATH):
        push_error("LuHm doctrine gate: runtime doctrine missing")
        return

    var raw := FileAccess.get_file_as_string(DOCTRINE_PATH)
    var parsed = JSON.parse_string(raw)
    if typeof(parsed) != TYPE_DICTIONARY:
        push_error("LuHm doctrine gate: runtime doctrine malformed")
        return
    if String(parsed.get("schema", "")) != EXPECTED_SCHEMA:
        push_error("LuHm doctrine gate: schema mismatch")
        return

    var authority = parsed.get("authority", {})
    if typeof(authority) != TYPE_DICTIONARY:
        push_error("LuHm doctrine gate: authority missing")
        return
    if String(authority.get("crown", "")) != "Professor":
        push_error("LuHm doctrine gate: Crown mismatch")
        return
    if not bool(authority.get("human_final_authority", false)):
        push_error("LuHm doctrine gate: human authority disabled")
        return
    if bool(authority.get("ai_self_approval", true)):
        push_error("LuHm doctrine gate: AI self approval forbidden")
        return

    var runtime = parsed.get("runtime", {})
    if typeof(runtime) != TYPE_DICTIONARY:
        push_error("LuHm doctrine gate: runtime missing")
        return
    if String(runtime.get("network", "")) != "dark":
        push_error("LuHm doctrine gate: WebGlass network must remain dark")
        return
    for forbidden_key in ["generic_shell", "filesystem_bridge", "eval_bridge", "arbitrary_url_bridge", "root", "silent_install"]:
        if bool(runtime.get(forbidden_key, true)):
            push_error("LuHm doctrine gate: forbidden capability enabled: %s" % forbidden_key)
            return

    _doc = parsed
    _valid = true

extends Node

const CONTRACT_PATH := "res://assets/system/luhmAgentMesh.json"

var contract: Dictionary = {}
var valid := false

func _ready() -> void:
    valid = _load_contract()
    if valid:
        print("LUHM_AGENT_MESH_CONTRACT=PASS")
    else:
        push_error("LUHM_AGENT_MESH_CONTRACT=FAIL")

func _load_contract() -> bool:
    if not FileAccess.file_exists(CONTRACT_PATH):
        return false
    var file := FileAccess.open(CONTRACT_PATH, FileAccess.READ)
    if file == null:
        return false
    var parsed = JSON.parse_string(file.get_as_text())
    if typeof(parsed) != TYPE_DICTIONARY:
        return false
    contract = parsed
    if contract.get("manager", "") != "Lum":
        return false
    if contract.get("sourceLaw", "") != "AI proposes. Policy authorizes. CI proves. Human promotes.":
        return false
    var android: Dictionary = contract.get("android", {})
    if android.get("executesOpenAIAgents", true):
        return false
    if android.get("containsProviderSecret", true):
        return false
    if android.get("termuxBridge", true):
        return false
    if android.get("remoteShell", true):
        return false
    return true

func summary() -> String:
    if not valid:
        return "AGENT MESH // CONTRACT BLOCKED"
    return "LUM + ONI // HOST MESH CROWN-GATED"

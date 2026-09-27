extends SceneTree

func _init() -> void:
    if not FileAccess.file_exists("res://assets/system/luhmAgentMesh.json"):
        _fail("embedded agent mesh contract missing from export pack")
        return
    if not FileAccess.file_exists("res://doctrine/luhmAgentMeshFinal-20260927.json"):
        _fail("agent mesh doctrine missing from export pack")
        return
    if FileAccess.file_exists("res://agents/luhm_mesh.py"):
        _fail("host OpenAI runtime leaked into export pack")
        return
    if FileAccess.file_exists("res://deploy/systemd/luhm-agent-mesh.service.example"):
        _fail("host deployment file leaked into export pack")
        return
    var file := FileAccess.open("res://assets/system/luhmAgentMesh.json", FileAccess.READ)
    if file == null:
        _fail("cannot read embedded mesh contract")
        return
    var parsed = JSON.parse_string(file.get_as_text())
    if typeof(parsed) != TYPE_DICTIONARY:
        _fail("embedded mesh contract is not JSON object")
        return
    var android: Dictionary = parsed.get("android", {})
    if bool(android.get("executesOpenAIAgents", true)):
        _fail("embedded contract claims Android executes OpenAI agents")
        return
    if bool(android.get("containsProviderSecret", true)):
        _fail("embedded contract claims provider secret")
        return
    print("LUHM_AGENT_MESH_PACK_SMOKE=PASS")
    quit(0)

func _fail(message: String) -> void:
    push_error("LUHM_AGENT_MESH_PACK_SMOKE=FAIL // " + message)
    quit(1)

extends SceneTree

func _init() -> void:
    # When an exported PCK is mounted by the editor binary from a repository
    # checkout, res:// can still see sibling source files from that checkout.
    # Raw FileAccess existence checks therefore cannot prove pack membership.
    # Host-only path exclusion is enforced by the Android export plugin and
    # source audit; this smoke verifies the contract actually embedded in PCK.
    if not FileAccess.file_exists("res://assets/system/luhmAgentMesh.json"):
        _fail("embedded agent mesh contract missing from export pack")
        return
    if not FileAccess.file_exists("res://doctrine/luhmAgentMeshFinal-20260927.json"):
        _fail("agent mesh doctrine missing from export pack")
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
    if bool(android.get("internetPermission", true)):
        _fail("embedded contract claims Android internet permission")
        return
    print("LUHM_AGENT_MESH_PACK_SMOKE=PASS")
    print("HOST_RUNTIME_BOUNDARY=EXPORT_PLUGIN_AND_SOURCE_AUDIT")
    quit(0)

func _fail(message: String) -> void:
    push_error("LUHM_AGENT_MESH_PACK_SMOKE=FAIL // " + message)
    quit(1)

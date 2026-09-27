extends SceneTree

func _init() -> void:
    var script = load("res://scripts/game/agentMeshContract.gd")
    if script == null:
        _fail("agent mesh contract script missing")
        return
    var node = script.new()
    root.add_child(node)
    await process_frame
    if not node.valid:
        _fail("embedded agent mesh contract rejected")
        return
    if node.contract.get("manager", "") != "Lum":
        _fail("manager is not Lum")
        return
    if int(node.contract.get("userFacingAgentCount", 0)) != 1:
        _fail("unexpected user-facing agent count")
        return
    var android: Dictionary = node.contract.get("android", {})
    if bool(android.get("internetPermission", true)):
        _fail("Android contract unexpectedly permits internet")
        return
    print("LUHM_AGENT_MESH_GODOT_SMOKE=PASS")
    quit(0)

func _fail(message: String) -> void:
    push_error("LUHM_AGENT_MESH_GODOT_SMOKE=FAIL // " + message)
    quit(1)

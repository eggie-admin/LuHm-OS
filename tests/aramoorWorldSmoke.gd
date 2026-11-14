extends SceneTree
## Godot source execution, not proof of final art, gameplay, WebGL or Samsung.
var errors: Array[String] = []

func _initialize() -> void:
    call_deferred("_run")

func _check(condition: bool, message: String) -> void:
    if condition:
        print("GREEN_ARAMOOR: ", message)
    else:
        errors.append(message)
        push_error("RED_ARAMOOR: " + message)

func _run() -> void:
    var scene: Variant = load("res://scenes/AramoorWorldPreview.tscn")
    _check(scene is PackedScene, "preview scene loads")
    if not scene is PackedScene:
        quit(1)
        return
    var world := (scene as PackedScene).instantiate() as Node3D
    root.add_child(world)
    var first: Dictionary = world.call("world_summary")
    _check(first.get("status") == "GENERATED_GEOMETRY_CANDIDATE", "world geometry generated")
    _check(int(first.get("zoneCount", 0)) == 9, "nine separate zones")
    _check(int(first.get("bridgeCount", 0)) == 12, "connected bridges")
    _check(int(first.get("artSocketCount", 0)) == 9, "canon art sockets preserved")
    _check(first.get("renderProfile") == "compatibilityWebGL2Safe", "web safe renderer contract")
    _check(first.get("sourcePdfIngested") == false, "unread original module not falsely claimed")
    _check(first.get("canonPromoted") == false, "world cannot auto promote")
    _check(first.get("crown") == "STOP", "source gate locked")
    var generated: Node = world.get_node_or_null("GeneratedWorld")
    _check(generated != null, "generated stage exists")
    var count := 0
    if generated != null:
        for child in generated.get_children():
            if str(child.name).begins_with("Zone_"):
                count += 1
                _check(child.get_node_or_null("CanonArtSocket") != null, "private model socket " + str(child.name))
    _check(count == 9, "nine independent scene roots")
    world.call("build_world")
    var repeat: Dictionary = world.call("world_summary")
    _check(first.get("fingerprint") == repeat.get("fingerprint"), "same seed same fingerprint")
    world.call("set_tide", true)
    var ghost: Dictionary = world.call("world_summary")
    _check(ghost.get("worldState") == "ghostTide", "second tide regenerated")
    _check(ghost.get("fingerprint") != first.get("fingerprint"), "distinct twin tide")
    _check(int(ghost.get("bridgeCount", 0)) == 12, "second tide retains connections")
    world.call("set_seed", 2011)
    var second_seed: Dictionary = world.call("world_summary")
    _check(second_seed.get("fingerprint") != ghost.get("fingerprint"), "new seed distinct decoration")
    _check(int(second_seed.get("shadowCasterCount", 1)) == 0, "default web profile no shadow cost")
    world.free()
    if errors.is_empty():
        print("ARAMOOR_WORLD_GODOT_SMOKE_GREEN")
        quit(0)
    else:
        print("ARAMOOR_WORLD_GODOT_SMOKE_RED: " + ", ".join(errors))
        quit(1)

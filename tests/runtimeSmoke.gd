extends SceneTree

var failures: Array[String] = []

func _initialize() -> void:
    call_deferred("_run")

func _run() -> void:
    var packed := load("res://scenes/Main.tscn")
    _check(packed is PackedScene, "Main.tscn loads as PackedScene")
    if not packed is PackedScene:
        _finish()
        return

    var game := packed.instantiate()
    root.add_child(game)
    await process_frame
    await physics_frame

    var world := game.get_node_or_null("NeonWorld")
    var player := game.get_node_or_null("PlayerController")
    var hud := game.get_node_or_null("GameHud")

    _check(world != null, "NeonWorld exists")
    _check(player != null, "PlayerController exists")
    _check(hud != null, "GameHud exists")
    _check(game.get_node_or_null("CutsceneDirector") != null, "CutsceneDirector exists")
    _check(game.get_node_or_null("CutsceneBridge") != null, "CutsceneBridge exists")

    if world != null:
        _check(world.get_node_or_null("WalkFloor") is StaticBody3D, "WalkFloor is collidable StaticBody3D")
        _check(world.get_node_or_null("LumAvatarSocket") != null, "Lum avatar socket exists")

    if player != null:
        _check(player.get_node_or_null("CameraYaw/CameraPitch/SpringArm3D/Camera3D") is Camera3D, "collision-aware camera rig exists")
        player.set_world_active(true)
        for _frame in range(18):
            await physics_frame
        _check(player.global_position.y > -2.0, "player remains supported by world collision")

    if game.has_method("_enter_world"):
        game.call("_enter_world")
        await process_frame
        _check(hud.world_root.visible, "world HUD becomes visible")
        _check(not hud.backend_root.visible, "backend overlay hides in world mode")

    _finish()

func _check(condition: bool, label: String) -> void:
    if condition:
        print("GREEN: ", label)
    else:
        failures.append(label)
        push_error("RED: %s" % label)

func _finish() -> void:
    if failures.is_empty():
        print("CROWN RUNTIME SMOKE GREEN")
        quit(0)
    else:
        push_error("CROWN RUNTIME SMOKE RED: %s" % ", ".join(failures))
        quit(1)

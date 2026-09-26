extends SceneTree

var failures: Array[String] = []

func _initialize() -> void:
    call_deferred("_run")

func _run() -> void:
    var packed := load("res://scenes/Main.tscn") as PackedScene
    _check(packed != null, "Main.tscn loads as PackedScene")
    if packed == null:
        _finish()
        return

    var game: Node = packed.instantiate()
    root.add_child(game)
    await process_frame
    await physics_frame

    var world: Node = game.get_node_or_null("NeonWorld")
    var player: Node = game.get_node_or_null("PlayerController")
    var hud: Node = game.get_node_or_null("GameHud")

    _check(world != null, "NeonWorld exists")
    _check(player != null, "PlayerController exists")
    _check(hud != null, "GameHud exists")
    _check(game.get_node_or_null("CutsceneDirector") != null, "CutsceneDirector exists")
    _check(game.get_node_or_null("CutsceneBridge") != null, "CutsceneBridge exists")

    if world != null:
        _check(world.get_node_or_null("WalkFloor") is StaticBody3D, "WalkFloor is collidable StaticBody3D")
        var lum: Node = world.get_node_or_null("LumAvatarSocket")
        _check(lum != null, "Lum avatar socket exists")
        if lum != null:
            _check(lum.get_node_or_null("AnimationTree") is AnimationTree, "Lum stable wrapper exposes AnimationTree")
            _check(lum.get_node_or_null("LookTarget") is Node3D, "Lum stable wrapper exposes LookTarget")

            if ResourceLoader.exists("res://assets/lum/luhm.glb"):
                _check(bool(lum.call("uses_external_model")), "Drive Lum external model loaded")
                var summary := lum.call("get_rig_summary") as Dictionary
                _check(int(summary.get("skeleton_bones", 0)) >= 20, "Drive Lum exposes humanoid skeleton")
                _check(int(summary.get("animations", 0)) >= 1, "Drive Lum exposes animation tracks")
                _check(int(summary.get("canonical_mapped", 0)) == int(summary.get("canonical_required", -1)), "Lum canonical body map resolves")
                _check(bool(summary.get("animation_tree_active", false)), "Lum AnimationTree active")
                _check(bool(summary.get("head_tracking", false)), "Lum head tracking active")
                var eye_mode := String(summary.get("eye_tracking_mode", ""))
                _check(eye_mode == "bone_pair" or eye_mode == "head_fallback", "Lum eye tracking capability explicit")

    if player != null:
        _check(player.get_node_or_null("CameraYaw/CameraPitch/SpringArm3D/Camera3D") is Camera3D, "collision-aware camera rig exists")
        player.call("set_world_active", true)
        for _frame in range(18):
            await physics_frame
        var player3d := player as Node3D
        _check(player3d != null and player3d.global_position.y > -2.0, "player remains supported by world collision")

    if game.has_method("enterWorldMode") and hud != null:
        game.call("enterWorldMode")
        await process_frame
        var world_root := hud.get("world_root") as Control
        var backend_root := hud.get("backend_root") as Control
        _check(world_root != null and world_root.visible, "world HUD becomes visible")
        _check(backend_root != null and not backend_root.visible, "backend overlay hides in world mode")

        game.call("_enter_backend")
        await process_frame
        _check(backend_root.visible and not world_root.visible, "return to Cathedral restores HUD")
        _check(not bool(player.get("world_active")), "Cathedral disables world movement")
        _check(not bool(player.get("controls_locked")), "Cathedral releases cutscene control lock")
        _check(not bool(hud.get("dialogue_label").visible), "Cathedral clears dialogue")
        _check(player.get("touch_axis") == Vector2.ZERO, "Cathedral clears held touch input")

    _check_expression_restore()
    _finish()

func _check_expression_restore() -> void:
    var avatar = load("res://scripts/game/lumAvatar.gd").new()
    var model := Node3D.new()
    avatar.add_child(model)
    avatar.model_root = model
    var mesh := ArrayMesh.new()
    mesh.add_blend_shape("mouth_open")
    mesh.add_blend_shape("custom")
    var arrays: Array = []
    arrays.resize(Mesh.ARRAY_MAX)
    arrays[Mesh.ARRAY_VERTEX] = PackedVector3Array([Vector3.ZERO, Vector3.RIGHT, Vector3.UP])
    var shapes: Array[Array] = [arrays.duplicate(true), arrays.duplicate(true)]
    mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays, shapes)
    var instance := MeshInstance3D.new()
    instance.mesh = mesh
    model.add_child(instance)
    instance.set_blend_shape_value(1, 0.25)
    avatar.set_expression("talk", 0.55)
    _check(is_equal_approx(instance.get_blend_shape_value(0), 0.55), "talk activates mouth fixture")
    avatar.restore_visual_state()
    _check(is_zero_approx(instance.get_blend_shape_value(0)), "neutral clears talking expression")
    _check(is_equal_approx(instance.get_blend_shape_value(1), 0.25), "neutral preserves unrelated shape")
    avatar.free()

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

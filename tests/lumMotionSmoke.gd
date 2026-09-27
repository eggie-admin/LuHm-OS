extends SceneTree

var failures: Array[String] = []

func _initialize() -> void:
    call_deferred("_run")

func _run() -> void:
    var avatar := (load("res://scenes/LumAvatar.tscn") as PackedScene).instantiate()
    root.add_child(avatar)
    await process_frame
    var rig := avatar.get("skeleton") as Skeleton3D
    var tree := avatar.get("animation_tree") as AnimationTree
    if rig == null or tree == null:
        push_error("Missing live avatar rig")
        quit(1)
        return
    tree.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
    tree.advance(0.1)
    rig.force_update_all_bone_transforms()
    for side in ["Left", "Right"]:
        var arm := rig.find_bone(side + "Arm")
        var elbow := rig.find_bone(side + "ForeArm")
        var direction := (rig.get_bone_global_pose(elbow).origin - rig.get_bone_global_pose(arm).origin).normalized()
        _check(direction.y < -0.7, side + " arm relaxed below shoulder, not T-pose")
    var spine := rig.find_bone("Spine")
    var idle_before := rig.get_bone_pose_rotation(spine)
    tree.advance(0.7)
    _check(idle_before.angle_to(rig.get_bone_pose_rotation(spine)) > 0.005, "idle changes skeletal pose")
    _check(avatar.play_motion_hint("run"), "running donor bound to active avatar")
    tree.advance(0.07)
    var leg := rig.find_bone("LeftUpLeg")
    var run_before := rig.get_bone_pose_rotation(leg)
    tree.advance(0.2)
    _check(run_before.angle_to(rig.get_bone_pose_rotation(leg)) > 0.05, "run changes leg pose over time")
    avatar.restore_visual_state()
    tree.advance(0.1)
    rig.force_update_all_bone_transforms()
    var direction := (rig.get_bone_global_pose(rig.find_bone("LeftForeArm")).origin - rig.get_bone_global_pose(rig.find_bone("LeftArm")).origin).normalized()
    _check(direction.y < -0.7, "restore returns to relaxed idle")
    avatar.queue_free()
    quit(0 if failures.is_empty() else 1)

func _check(ok: bool, label: String) -> void:
    print("PASS: " if ok else "FAIL: ", label)
    if not ok:
        failures.append(label)

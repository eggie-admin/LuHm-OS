extends SceneTree

var failures: Array[String] = []

func _initialize() -> void:
    call_deferred("_run")

func _run() -> void:
    var packed := load("res://scenes/LumAvatar.tscn") as PackedScene
    _check(packed != null, "LumAvatar.tscn loads")
    if packed == null:
        _finish()
        return

    var avatar := packed.instantiate()
    root.add_child(avatar)
    await process_frame
    await process_frame

    _check(avatar.get_node_or_null("AnimationTree") is AnimationTree, "AnimationTree wrapper exists")
    _check(avatar.get_node_or_null("LookTarget") is Node3D, "LookTarget exists")
    _check(bool(avatar.call("uses_external_model")), "Drive Lum GLB loaded")

    var summary := avatar.call("get_rig_summary") as Dictionary
    _check(int(summary.get("skeleton_bones", 0)) == 24, "canonical donor exposes 24 bones")
    _check(int(summary.get("canonical_required", 0)) == 22, "canonical map defines 22 humanoid roles")
    _check(int(summary.get("canonical_mapped", 0)) == 22, "all required humanoid roles resolve")
    _check((summary.get("canonical_missing", []) as Array).is_empty(), "canonical map has no missing required bones")
    _check(bool(summary.get("animation_tree_active", false)), "AnimationTree is active")
    _check(int(summary.get("animation_tree_states", 0)) >= 1, "AnimationTree has at least one imported state")
    _check(bool(summary.get("head_tracking", false)), "head LookAtModifier3D installed")

    var eye_mode := String(summary.get("eye_tracking_mode", ""))
    _check(eye_mode == "head_fallback" or eye_mode == "bone_pair", "eye tracking capability is explicit")
    if eye_mode == "head_fallback":
        _check(not bool(summary.get("eye_tracking", true)), "current donor honestly reports no eye-bone pair")

    var target := avatar.global_position + Vector3(0.5, 1.9, -3.5)
    avatar.call("set_look_target_world", target)
    await process_frame
    var marker := avatar.get_node_or_null("LookTarget") as Node3D
    _check(marker != null and marker.global_position.distance_to(target) < 0.001, "look target updates in world space")

    _finish()

func _check(condition: bool, label: String) -> void:
    if condition:
        print("GREEN: ", label)
    else:
        failures.append(label)
        push_error("RED: %s" % label)

func _finish() -> void:
    if failures.is_empty():
        print("LUHM RIG V2 PHASE 1 GREEN")
        quit(0)
    else:
        push_error("LUHM RIG V2 PHASE 1 RED: %s" % ", ".join(failures))
        quit(1)

extends SceneTree
# Isolated headless test against ephemeral GLB; no production writes.
const MODEL_PATH := "res://assets/lum/luhm.glb"
const SHAPES := ["hip_width", "waist_shape", "smile"]
const EXPECTED_COUNTS := {"hip_width": 17109, "waist_shape": 11536, "smile": 5562}
var errors: Array[String] = []

func _initialize() -> void:
    call_deferred("_run")

func _run() -> void:
    var scene = load(MODEL_PATH)
    if not scene is PackedScene:
        _check(false, "candidate must import as PackedScene")
        _finish()
        return
    var character: Node = scene.instantiate()
    root.add_child(character)
    var skeletons = character.find_children("*", "Skeleton3D", true, false)
    _check(skeletons.size() > 0, "Skeleton3D exists")
    if not skeletons.is_empty():
        _check((skeletons[0] as Skeleton3D).get_bone_count() == 24, "24 source bones remain")
    var players = character.find_children("*", "AnimationPlayer", true, false)
    _check(not players.is_empty(), "animation player preserved")
    if not players.is_empty():
        _check((players[0] as AnimationPlayer).get_animation_list().size() > 0, "source animation accessible")
    var found: Dictionary = {}
    for node in character.find_children("*", "MeshInstance3D", true, false):
        var instance := node as MeshInstance3D
        var array_mesh := instance.mesh as ArrayMesh
        if array_mesh == null:
            continue
        for idx in range(array_mesh.get_blend_shape_count()):
            var morph_name := String(array_mesh.get_blend_shape_name(idx)).to_lower()
            if morph_name not in SHAPES:
                continue
            _check(is_zero_approx(instance.get_blend_shape_value(idx)), "original default zero: " + morph_name)
            var moved := 0
            for surface in range(array_mesh.get_surface_count()):
                var blend_arrays = array_mesh.surface_get_blend_shape_arrays(surface)
                if idx >= blend_arrays.size():
                    continue
                var attributes: Array = blend_arrays[idx]
                var base_arrays: Array = array_mesh.surface_get_arrays(surface)
                var base_positions: PackedVector3Array = base_arrays[Mesh.ARRAY_VERTEX]
                var target_positions: PackedVector3Array = attributes[Mesh.ARRAY_VERTEX]
                if target_positions.size() != base_positions.size():
                    _check(false, "blend shape and base vertex count mismatch: " + morph_name)
                    continue
                for vertex_index in range(base_positions.size()):
                    if (target_positions[vertex_index] - base_positions[vertex_index]).length() > 0.00001:
                        moved += 1
            var expected := int(EXPECTED_COUNTS[morph_name])
            _check(moved >= int(expected * 0.8) and moved <= int(expected * 1.2), "actual displaced vertices: " + morph_name + " (" + str(moved) + ")")
            instance.set_blend_shape_value(idx, 0.75)
            _check(is_equal_approx(instance.get_blend_shape_value(idx), 0.75), "Godot setter: " + morph_name)
            instance.set_blend_shape_value(idx, 0.0)
            _check(is_zero_approx(instance.get_blend_shape_value(idx)), "reset to original: " + morph_name)
            found[morph_name] = moved
    for shape in SHAPES:
        _check(found.has(shape), "imported actual morph: " + shape)
    print("MORPH_MOVED_VERTEX_COUNTS=", JSON.stringify(found))
    _stress_bones_with_active_morphs(character)
    character.free()
    _finish()

func _stress_bones_with_active_morphs(character: Node) -> void:
    var skeletons = character.find_children("*", "Skeleton3D", true, false)
    if skeletons.is_empty():
        _check(false, "pose stress requires real skeleton")
        return
    var skeleton := skeletons[0] as Skeleton3D

    # Play actual source motion before checking bounded manual stress poses.
    var players = character.find_children("*", "AnimationPlayer", true, false)
    if not players.is_empty():
        var animator := players[0] as AnimationPlayer
        var clips := animator.get_animation_list()
        if not clips.is_empty():
            animator.play(clips[0])
            animator.advance(0.12)
            _check(animator.is_playing(), "source animation advances")
            animator.stop()

    var meshes = character.find_children("*", "MeshInstance3D", true, false)
    var active_morphs := 0
    for obj in meshes:
        var instance := obj as MeshInstance3D
        if instance == null or instance.mesh == null:
            continue
        for shape_idx in range(instance.mesh.get_blend_shape_count()):
            if String(instance.mesh.get_blend_shape_name(shape_idx)).to_lower() in SHAPES:
                instance.set_blend_shape_value(shape_idx, 0.75)
                _check(is_equal_approx(instance.get_blend_shape_value(shape_idx), 0.75), "morph remains active during pose")
                active_morphs += 1
    _check(active_morphs == 3, "three real morph targets coexist with skeleton")

    # Change actual source limb bones. Confirm the global bone transform changes,
    # then restore it. This is a skeleton/runtime coexistence smoke, NOT a
    # photographed mesh-clipping or deformation-quality certification.
    var stress_angles := {
        "LeftArm": 35.0,
        "RightArm": -35.0,
        "LeftLeg": 20.0,
        "RightLeg": -20.0
    }
    var tested_bones := 0
    for bone_name in stress_angles:
        var bone_idx := skeleton.find_bone(String(bone_name))
        _check(bone_idx >= 0, "canonical stress bone present: " + str(bone_name))
        if bone_idx < 0:
            continue
        var before_local := skeleton.get_bone_pose_rotation(bone_idx)
        var before_global := skeleton.get_bone_global_pose(bone_idx).basis.get_rotation_quaternion()
        var direction := Vector3.RIGHT if String(bone_name).contains("Leg") else Vector3.FORWARD
        var angle := deg_to_rad(float(stress_angles[bone_name]))
        skeleton.set_bone_pose_rotation(bone_idx, before_local * Quaternion(direction, angle))
        skeleton.force_update_all_bone_transforms()
        var moved_global := skeleton.get_bone_global_pose(bone_idx).basis.get_rotation_quaternion()
        _check(before_global.angle_to(moved_global) > deg_to_rad(5.0), "visible skeletal pose rotation: " + str(bone_name))
        skeleton.set_bone_pose_rotation(bone_idx, before_local)
        skeleton.force_update_all_bone_transforms()
        var restored := skeleton.get_bone_global_pose(bone_idx).basis.get_rotation_quaternion()
        _check(before_global.angle_to(restored) < 0.001, "bone pose reversibly restored: " + str(bone_name))
        tested_bones += 1
    _check(tested_bones == 4, "four limb stress poses exercised")
    for obj in meshes:
        var instance := obj as MeshInstance3D
        if instance == null or instance.mesh == null:
            continue
        for shape_idx in range(instance.mesh.get_blend_shape_count()):
            if String(instance.mesh.get_blend_shape_name(shape_idx)).to_lower() in SHAPES:
                _check(is_equal_approx(instance.get_blend_shape_value(shape_idx), 0.75), "morph survives limb pose")
                instance.set_blend_shape_value(shape_idx, 0.0)
                _check(is_zero_approx(instance.get_blend_shape_value(shape_idx)), "post-pose morph reset")
    print("LUM_MORPH_PHASE2_POSE_SMOKE_GREEN" if errors.is_empty() else "LUM_MORPH_PHASE2_POSE_SMOKE_RED")

func _check(ok: bool, label: String) -> void:
    if ok:
        print("GREEN: ", label)
    else:
        errors.append(label)
        push_error("RED_LUM_MORPH_PHASE2: " + label)

func _finish() -> void:
    if errors.is_empty():
        print("LUM_MORPH_PHASE2_GODOT_GREEN")
        quit(0)
    else:
        print("LUM_MORPH_PHASE2_GODOT_RED: ", ", ".join(errors))
        quit(1)

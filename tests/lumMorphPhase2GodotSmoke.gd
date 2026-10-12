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
    character.free()
    _finish()

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

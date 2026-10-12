extends SceneTree

var failures: Array[String] = []

func _initialize() -> void:
    call_deferred("_run")

func _run() -> void:
    var controller = load("res://scripts/game/characterMorphController.gd").new()
    var root_node := Node3D.new()
    root.add_child(root_node)
    root_node.add_child(controller)

    var mesh := ArrayMesh.new()
    mesh.add_blend_shape("hip_width")
    mesh.add_blend_shape("bust_volume")
    mesh.add_blend_shape("body_softness")
    var arrays: Array = []
    arrays.resize(Mesh.ARRAY_MAX)
    arrays[Mesh.ARRAY_VERTEX] = PackedVector3Array([Vector3.ZERO, Vector3.RIGHT, Vector3.UP])
    var shapes: Array[Array] = [
        arrays.duplicate(true),
        arrays.duplicate(true),
        arrays.duplicate(true)
    ]
    mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays, shapes)

    var instance := MeshInstance3D.new()
    instance.mesh = mesh
    root_node.add_child(instance)

    controller.configure(root_node)
    var receipt := controller.apply_preset("urd")

    _check(receipt.get("character") == "urd", "Urd preset selected")
    _check(is_equal_approx(instance.get_blend_shape_value(0), 0.82), "Urd hip morph applied")
    _check(is_equal_approx(instance.get_blend_shape_value(1), 0.82), "Urd bust morph applied")
    _check(is_equal_approx(instance.get_blend_shape_value(2), 0.66), "Urd softness morph applied")
    _check(int(receipt.get("appliedCount", 0)) == 3, "only available shapes counted as applied")
    _check(int(receipt.get("missingCount", 0)) > 0, "unavailable candidate shapes reported honestly")
    _check(receipt.get("physicsApplied") is bool and receipt.get("physicsApplied") == false, "shape morph does not fake physics")
    _check(receipt.get("canonPromoted") == false, "runtime preset cannot promote canon")

    controller.reset_known_shapes()
    _check(is_zero_approx(instance.get_blend_shape_value(0)), "reset clears known morphs")

    root_node.free()
    _finish()

func _check(condition: bool, label: String) -> void:
    if condition:
        print("GREEN: ", label)
    else:
        failures.append(label)
        push_error("RED: %s" % label)

func _finish() -> void:
    if failures.is_empty():
        print("GODDESS MORPH RUNTIME SMOKE GREEN")
        quit(0)
    else:
        push_error("GODDESS MORPH RUNTIME SMOKE RED: %s" % ", ".join(failures))
        quit(1)

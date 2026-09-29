extends RefCounted

static func install(avatar: Node3D) -> Dictionary:
    if avatar == null:
        return {"status": "NO_AVATAR", "installed": []}

    var skeleton := _find_skeleton(avatar)
    if skeleton == null:
        return {"status": "NO_SKELETON", "installed": []}
    if not ClassDB.class_exists("SpringBoneSimulator3D"):
        return {"status": "ENGINE_UNAVAILABLE", "installed": []}

    var world_scale := skeleton.global_transform.basis.get_scale()
    var scale_error := maxf(absf(world_scale.x - 1.0), maxf(absf(world_scale.y - 1.0), absf(world_scale.z - 1.0)))
    if scale_error > 0.03:
        return {
            "status": "BLOCKED_SCALED_SKELETON",
            "installed": [],
            "world_scale": [world_scale.x, world_scale.y, world_scale.z],
            "remedy": "Bake/apply character scale in the authored GLB before enabling spring bones."
        }

    var candidates := [
        {"id":"hair_center","roots":["HairRoot","hair_root","Hair_01","hair01"],"ends":["HairTip","hair_tip","Hair_05","hair05"],"stiffness":0.72,"drag":0.42,"gravity":0.06},
        {"id":"hair_left","roots":["Hair_L_01","hair_l_01","HairLeft01"],"ends":["Hair_L_05","hair_l_05","HairLeftTip"],"stiffness":0.70,"drag":0.44,"gravity":0.06},
        {"id":"hair_right","roots":["Hair_R_01","hair_r_01","HairRight01"],"ends":["Hair_R_05","hair_r_05","HairRightTip"],"stiffness":0.70,"drag":0.44,"gravity":0.06},
        {"id":"tail","roots":["Tail_01","tail_01","TailRoot"],"ends":["Tail_05","tail_05","TailTip"],"stiffness":0.62,"drag":0.36,"gravity":0.08},
        {"id":"wing_left","roots":["Wing_L_01","wing_l_01"],"ends":["Wing_L_04","wing_l_04"],"stiffness":0.82,"drag":0.52,"gravity":0.03},
        {"id":"wing_right","roots":["Wing_R_01","wing_r_01"],"ends":["Wing_R_04","wing_r_04"],"stiffness":0.82,"drag":0.52,"gravity":0.03},
        {"id":"bust_left","roots":["Breast_L","breast_l","Bust_L","bust_l"],"ends":[],"stiffness":0.90,"drag":0.64,"gravity":0.01},
        {"id":"bust_right","roots":["Breast_R","breast_r","Bust_R","bust_r"],"ends":[],"stiffness":0.90,"drag":0.64,"gravity":0.01}
    ]

    var installed: Array[String] = []
    for spec in candidates:
        var root_name := _find_bone_name(skeleton, spec["roots"])
        if root_name.is_empty():
            continue
        var end_name := _find_bone_name(skeleton, spec["ends"])
        if end_name.is_empty():
            end_name = root_name

        var simulator = ClassDB.instantiate("SpringBoneSimulator3D")
        if not (simulator is Node):
            continue
        simulator.name = "BetaSpring_%s" % spec["id"]
        skeleton.add_child(simulator)
        simulator.call("set_setting_count", 1)
        simulator.call("set_root_bone_name", 0, root_name)
        simulator.call("set_end_bone_name", 0, end_name)
        if root_name == end_name and simulator.has_method("set_extend_end_bone"):
            simulator.call("set_extend_end_bone", 0, true)
            if simulator.has_method("set_end_bone_length"):
                simulator.call("set_end_bone_length", 0, 0.16)
        simulator.call("set_stiffness", 0, float(spec["stiffness"]))
        simulator.call("set_drag", 0, float(spec["drag"]))
        simulator.call("set_gravity", 0, float(spec["gravity"]))
        simulator.call("set_gravity_direction", 0, Vector3.DOWN)
        if simulator.has_method("set_radius"):
            simulator.call("set_radius", 0, 0.035)
        if simulator.has_method("reset"):
            simulator.call("reset")
        installed.append(str(spec["id"]))

    return {"status": "INSTALLED" if not installed.is_empty() else "NO_MATCHING_CHAINS", "installed": installed, "skeleton_bones": skeleton.get_bone_count()}

static func _find_skeleton(root: Node3D) -> Skeleton3D:
    var direct := root.find_children("*", "Skeleton3D", true, false)
    return direct[0] as Skeleton3D if not direct.is_empty() else null

static func _find_bone_name(skeleton: Skeleton3D, aliases: Array) -> String:
    for alias in aliases:
        var name := str(alias)
        if skeleton.find_bone(name) >= 0:
            return name
    return ""

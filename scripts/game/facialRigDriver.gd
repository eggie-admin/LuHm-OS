extends RefCounted

const GROUPS := {
    "blink": ["blink", "blink_l", "blink_r", "eye_blink", "eyeblinkleft", "eyeblinkright"],
    "smile": ["smile", "happy", "joy", "mouthsmileleft", "mouthsmileright"],
    "jaw_open": ["jawopen", "jaw_open", "mouth_open", "aa", "a"],
    "brow_up": ["browinnerup", "brow_outer_up_l", "brow_outer_up_r", "browup"],
    "brow_down": ["browdownleft", "browdownright", "brow_down_l", "brow_down_r"],
    "viseme_o": ["oh", "o", "viseme_o"],
    "viseme_e": ["ee", "e", "viseme_e"],
    "viseme_mbp": ["mouthclose", "mbp", "viseme_mbp"]
}

static func inspect(avatar: Node3D) -> Dictionary:
    if avatar == null:
        return {"status":"NO_AVATAR","blend_shapes":[],"coverage":{}}
    var names: Array[String] = []
    for node in avatar.find_children("*", "MeshInstance3D", true, false):
        var mesh_instance := node as MeshInstance3D
        var array_mesh := mesh_instance.mesh as ArrayMesh
        if array_mesh == null:
            continue
        for index in range(array_mesh.get_blend_shape_count()):
            var shape_name := str(array_mesh.get_blend_shape_name(index))
            if shape_name not in names:
                names.append(shape_name)
    var lowered: Array[String] = []
    for name in names:
        lowered.append(name.to_lower())
    var coverage := {}
    for group_name in GROUPS:
        var hit := false
        for alias in GROUPS[group_name]:
            if str(alias).to_lower() in lowered:
                hit = true
                break
        coverage[group_name] = hit
    return {"status":"READY" if not names.is_empty() else "NO_BLEND_SHAPES", "blend_shape_count":names.size(), "blend_shapes":names, "coverage":coverage}

static func set_group(avatar: Node3D, group_name: String, weight: float) -> int:
    if avatar == null or not GROUPS.has(group_name):
        return 0
    var aliases: Array = GROUPS[group_name]
    var changed := 0
    for node in avatar.find_children("*", "MeshInstance3D", true, false):
        var mesh_instance := node as MeshInstance3D
        var array_mesh := mesh_instance.mesh as ArrayMesh
        if array_mesh == null:
            continue
        for index in range(array_mesh.get_blend_shape_count()):
            var shape_name := str(array_mesh.get_blend_shape_name(index))
            if shape_name.to_lower() in aliases:
                mesh_instance.set("blend_shapes/%s" % shape_name, clampf(weight, 0.0, 1.0))
                changed += 1
    return changed

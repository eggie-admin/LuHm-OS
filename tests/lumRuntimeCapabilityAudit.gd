extends SceneTree

const LUM_PATH := "res://assets/lum/luhm.glb"
const OUT_PATH := "res://build/beta-engine/lum-runtime-capabilities.json"

func _initialize() -> void:
    call_deferred("_run")

func _run() -> void:
    var packed := load(LUM_PATH) as PackedScene
    assert(packed != null)
    var model := packed.instantiate() as Node3D
    assert(model != null)
    root.add_child(model)
    await process_frame

    var skeletons := model.find_children("*", "Skeleton3D", true, false)
    var bone_names: Array[String] = []
    if not skeletons.is_empty():
        var skeleton := skeletons[0] as Skeleton3D
        for index in range(skeleton.get_bone_count()):
            bone_names.append(String(skeleton.get_bone_name(index)))

    var blend_shapes: Array[String] = []
    var materials: Array[Dictionary] = []
    var mesh_count := 0
    var min_y := 1.0e20
    var max_y := -1.0e20
    var bounds_found := false
    var axis_values: Array[float] = [0.0, 1.0]

    for child in model.find_children("*", "MeshInstance3D", true, false):
        var mesh_instance := child as MeshInstance3D
        if mesh_instance == null or mesh_instance.mesh == null:
            continue
        mesh_count += 1
        var array_mesh := mesh_instance.mesh as ArrayMesh
        if array_mesh != null:
            for blend_index in range(array_mesh.get_blend_shape_count()):
                var blend_name := String(array_mesh.get_blend_shape_name(blend_index))
                if blend_name not in blend_shapes:
                    blend_shapes.append(blend_name)

        var box := mesh_instance.get_aabb()
        for xi in axis_values:
            for yi in axis_values:
                for zi in axis_values:
                    var local_corner := box.position + Vector3(box.size.x * xi, box.size.y * yi, box.size.z * zi)
                    var point := mesh_instance.global_transform * local_corner
                    min_y = minf(min_y, point.y)
                    max_y = maxf(max_y, point.y)
                    bounds_found = true

        for surface in range(mesh_instance.mesh.get_surface_count()):
            var material := mesh_instance.get_active_material(surface)
            materials.append(_material_record(mesh_instance.name, surface, material))

    var animations: Array[String] = []
    for child in model.find_children("*", "AnimationPlayer", true, false):
        var player := child as AnimationPlayer
        if player == null:
            continue
        for animation_name in player.get_animation_list():
            var label := String(animation_name)
            if label not in animations:
                animations.append(label)

    blend_shapes.sort()
    bone_names.sort()
    animations.sort()

    var channel_totals := {
        "base_color_texture": 0,
        "normal_texture": 0,
        "roughness_texture": 0,
        "metallic_texture": 0,
        "ao_texture": 0,
        "height_texture": 0,
        "emission_texture": 0,
    }
    for record in materials:
        var channels: Dictionary = record.get("channels", {})
        for key in channel_totals:
            if bool(channels.get(key, {}).get("present", false)):
                channel_totals[key] = int(channel_totals[key]) + 1

    var report := {
        "schema": "luhm-os.lum-runtime-capability-audit.v1",
        "source": LUM_PATH,
        "mesh_count": mesh_count,
        "raw_visual_height": max_y - min_y if bounds_found else 0.0,
        "skeleton_count": skeletons.size(),
        "bone_count": bone_names.size(),
        "bone_names": bone_names,
        "animation_count": animations.size(),
        "animations": animations,
        "blend_shape_count": blend_shapes.size(),
        "blend_shapes": blend_shapes,
        "material_surface_count": materials.size(),
        "material_channel_totals": channel_totals,
        "materials": materials,
        "secondary_motion_alias_hits": _secondary_motion_alias_hits(bone_names),
    }

    var output_dir := ProjectSettings.globalize_path("res://build/beta-engine")
    DirAccess.make_dir_recursive_absolute(output_dir)
    var file := FileAccess.open(OUT_PATH, FileAccess.WRITE)
    assert(file != null)
    file.store_string(JSON.stringify(report, "  ") + "\n")
    file.close()

    print("LUM_RUNTIME_CAPABILITIES=PASS bones=%d animations=%d blend_shapes=%d surfaces=%d raw_height=%.6f channels=%s" % [
        bone_names.size(),
        animations.size(),
        blend_shapes.size(),
        materials.size(),
        float(report["raw_visual_height"]),
        JSON.stringify(channel_totals),
    ])
    model.queue_free()
    quit(0)

func _material_record(mesh_name: StringName, surface: int, material: Material) -> Dictionary:
    if material == null:
        return {"mesh": String(mesh_name), "surface": surface, "material_class": "NONE", "channels": {}}
    return {
        "mesh": String(mesh_name),
        "surface": surface,
        "material_class": material.get_class(),
        "resource_path": material.resource_path,
        "channels": {
            "base_color_texture": _texture_info(material, "albedo_texture"),
            "normal_texture": _texture_info(material, "normal_texture"),
            "roughness_texture": _texture_info(material, "roughness_texture"),
            "metallic_texture": _texture_info(material, "metallic_texture"),
            "ao_texture": _texture_info(material, "ao_texture"),
            "height_texture": _texture_info(material, "heightmap_texture"),
            "emission_texture": _texture_info(material, "emission_texture"),
        },
    }

func _texture_info(material: Material, property_name: String) -> Dictionary:
    if not _has_property(material, property_name):
        return {"present": false, "property": property_name}
    var value = material.get(property_name)
    if not (value is Texture2D):
        return {"present": false, "property": property_name}
    var texture := value as Texture2D
    return {
        "present": true,
        "property": property_name,
        "resource_path": texture.resource_path,
        "width": texture.get_width(),
        "height": texture.get_height(),
    }

func _has_property(object: Object, property_name: String) -> bool:
    for entry in object.get_property_list():
        if String(entry.get("name", "")) == property_name:
            return true
    return false

func _secondary_motion_alias_hits(bones: Array[String]) -> Dictionary:
    var groups := {
        "hair": ["hair", "pony", "bang", "strand"],
        "cloth": ["cloth", "skirt", "cape", "coat"],
        "tail": ["tail"],
        "wing": ["wing"],
        "bust": ["breast", "bust"],
    }
    var result := {}
    for group in groups:
        var hits: Array[String] = []
        for bone in bones:
            var lowered := bone.to_lower()
            for token in groups[group]:
                if lowered.contains(String(token)):
                    hits.append(bone)
                    break
        result[group] = hits
    return result

extends RefCounted

static func apply_sidecar(root: Node3D, sidecar_path: String) -> Dictionary:
    if root == null:
        return {"status":"NO_AVATAR","materials":0}
    if not FileAccess.file_exists(sidecar_path):
        return {"status":"NO_SIDECAR","materials":0}
    var parsed = JSON.parse_string(FileAccess.get_file_as_string(sidecar_path))
    if not (parsed is Dictionary):
        return {"status":"INVALID_SIDECAR","materials":0}
    var entries = parsed.get("materials", [])
    if not (entries is Array):
        return {"status":"INVALID_MATERIAL_LIST","materials":0}
    var changed := 0
    for entry in entries:
        if not (entry is Dictionary):
            continue
        var mesh_name := str(entry.get("mesh", ""))
        var surface := int(entry.get("surface", 0))
        var mesh_instance := root.find_child(mesh_name, true, false) as MeshInstance3D
        if mesh_instance == null or mesh_instance.mesh == null:
            continue
        if surface < 0 or surface >= mesh_instance.mesh.get_surface_count():
            continue
        var source := mesh_instance.get_active_material(surface)
        var material := source.duplicate() if source != null else StandardMaterial3D.new()
        if not (material is BaseMaterial3D):
            continue
        _bind_texture(material, "albedo_texture", str(entry.get("base_color", "")))
        _bind_texture(material, "normal_texture", str(entry.get("normal", "")))
        if not str(entry.get("normal", "")).is_empty():
            _set_if(material, "normal_enabled", true)
        _bind_texture(material, "roughness_texture", str(entry.get("roughness", "")))
        _bind_texture(material, "metallic_texture", str(entry.get("metallic", "")))
        _bind_texture(material, "ao_texture", str(entry.get("ao", "")))
        if not str(entry.get("ao", "")).is_empty():
            _set_if(material, "ao_enabled", true)
        _bind_texture(material, "heightmap_texture", str(entry.get("height", "")))
        if not str(entry.get("height", "")).is_empty():
            _set_if(material, "heightmap_enabled", true)
        _bind_texture(material, "emission_texture", str(entry.get("emissive", "")))
        if not str(entry.get("emissive", "")).is_empty():
            _set_if(material, "emission_enabled", true)
        mesh_instance.set_surface_override_material(surface, material)
        changed += 1
    return {"status":"APPLIED" if changed > 0 else "NO_MATCHES","materials":changed}

static func _bind_texture(material: Material, property_name: String, path: String) -> void:
    if path.is_empty() or not ResourceLoader.exists(path):
        return
    var resource := load(path)
    if resource is Texture2D:
        _set_if(material, property_name, resource)

static func _set_if(object: Object, property_name: String, value: Variant) -> void:
    for entry in object.get_property_list():
        if str(entry.get("name", "")) == property_name:
            object.set(property_name, value)
            return

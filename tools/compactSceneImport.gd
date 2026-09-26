@tool
extends EditorScenePostImport

const SHARED_MESH := "res://assets/lum/lumSharedMesh.res"

func _post_import(scene: Node) -> Object:
    var meshes := scene.find_children("*", "MeshInstance3D", true, false)
    if meshes.size() != 1:
        push_error("Compact import requires exactly one mesh")
        return scene
    var instance := meshes[0] as MeshInstance3D
    var incoming := instance.mesh as ArrayMesh
    if ResourceLoader.exists(SHARED_MESH):
        var shared := load(SHARED_MESH) as ArrayMesh
        if shared.get_surface_count() != incoming.get_surface_count() or shared.get_blend_shape_count() != incoming.get_blend_shape_count():
            push_error("Compact mesh structure differs")
            return scene
        for i in range(shared.get_surface_count()):
            if var_to_bytes(shared.surface_get_arrays(i)) != var_to_bytes(incoming.surface_get_arrays(i)):
                push_error("Compact mesh geometry differs")
                return scene
        instance.mesh = shared
    else:
        var error := ResourceSaver.save(incoming, SHARED_MESH, ResourceSaver.FLAG_COMPRESS)
        if error != OK:
            push_error("Cannot save shared compact mesh")
            return scene
        instance.mesh = load(SHARED_MESH)
    return scene

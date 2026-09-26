extends SceneTree

func _initialize() -> void:
    call_deferred("_run")

func _run() -> void:
    var original := Image.load_from_file("res://assets/lum/lumShared.png")
    var texture := load("res://assets/lum/lumShared.png") as Texture2D
    var imported := texture.get_image()
    if imported == null or imported.get_size() != original.get_size():
        push_error("Compact texture resolution changed")
        quit(1)
        return
    original.clear_mipmaps()
    imported.clear_mipmaps()
    original.convert(Image.FORMAT_RGB8)
    imported.convert(Image.FORMAT_RGB8)
    var metrics := original.compute_image_metrics(imported, false)
    print("COMPACT_TEXTURE_METRICS ", JSON.stringify(metrics))
    if float(metrics["peak_snr"]) < 40.0:
        push_error("Compact texture PSNR below 40 dB")
        quit(1)
        return
    for path in ["res://assets/lum/luhm.glb", "res://assets/lum/luhmRunning.glb"]:
        var scene := (load(path) as PackedScene).instantiate()
        var meshes := scene.find_children("*", "MeshInstance3D", true, false)
        var skeletons := scene.find_children("*", "Skeleton3D", true, false)
        var players := scene.find_children("*", "AnimationPlayer", true, false)
        if meshes.size() != 1 or skeletons.size() != 1 or players.size() != 1:
            push_error("Compact rig structure changed")
            quit(1)
            return
        var instance := meshes[0] as MeshInstance3D
        if instance.mesh.resource_path != "res://assets/lum/lumSharedMesh.res" or (skeletons[0] as Skeleton3D).get_bone_count() != 24:
            push_error("Shared mesh or rig contract failed")
            quit(1)
            return
        if (players[0] as AnimationPlayer).get_animation_list().is_empty():
            push_error("Compact animation lost")
            quit(1)
            return
        var material := instance.mesh.surface_get_material(0) as StandardMaterial3D
        if material == null or material.albedo_texture != texture:
            push_error("Shared material texture contract failed")
            quit(1)
            return
        scene.free()
    print("COMPACT ASSET SMOKE PASS")
    quit(0)

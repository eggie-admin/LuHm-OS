extends SceneTree

const REQUIRED := [
    "res://assets/community/runtime/city-industrial/building-a.glb",
    "res://assets/community/runtime/city-industrial/chimney-large.glb",
    "res://assets/community/runtime/city-industrial/detail-tank.glb",
    "res://assets/community/runtime/factory/catwalk-straight.glb",
    "res://assets/community/runtime/factory/crane.glb",
    "res://assets/community/runtime/factory/pipe-large-valve.glb",
    "res://assets/community/runtime/factory/robot-arm-a.glb",
    "res://assets/community/runtime/furniture/kitchenBar.glb",
    "res://assets/community/runtime/furniture/stoolBar.glb",
    "res://assets/community/runtime/furniture/loungeSofaLong.glb",
    "res://assets/community/runtime/furniture/radio.glb",
    "res://assets/community/runtime/furniture/televisionVintage.glb"
]

func _initialize() -> void:
    call_deferred("_run")

func _run() -> void:
    var loaded := 0
    var selection = JSON.parse_string(FileAccess.get_file_as_string("res://assets/community/selected-assets.json"))
    var paths: Array[String] = []
    for group in selection["groups"]:
        for file in selection["groups"][group]:
            paths.append("res://assets/community/runtime/%s/%s" % [group, file])
    for path in paths:
        if not ResourceLoader.exists(path):
            push_error("COMMUNITY ASSET MISSING: %s" % path)
            quit(1)
            return
        var resource = load(path)
        if not resource is PackedScene:
            push_error("COMMUNITY ASSET NOT PACKEDSCENE: %s" % path)
            quit(1)
            return
        var instance := (resource as PackedScene).instantiate()
        if instance == null:
            push_error("COMMUNITY ASSET INSTANTIATE FAILED: %s" % path)
            quit(1)
            return
        if "/factory/" in path or "/city-industrial/" in path:
            var textured := false
            for child in instance.find_children("*", "MeshInstance3D", true, false):
                var mesh := child as MeshInstance3D
                for surface in range(mesh.mesh.get_surface_count()):
                    var material := mesh.get_active_material(surface) as BaseMaterial3D
                    if material != null and material.albedo_texture != null:
                        textured = true
            if not textured:
                push_error("COMMUNITY TEXTURE MISSING: %s" % path)
                instance.free()
                quit(1)
                return
        instance.free()
        loaded += 1
    var dress := (load("res://scripts/game/communitySetDress.gd") as Script).new() as Node3D
    root.add_child(dress)
    if dress.get("missing_count") != 0 or int(dress.get("loaded_count")) < paths.size():
        push_error("Curated content is packaged but not instantiated")
        quit(1)
        return
    dress.queue_free()
    print("COMMUNITY_ASSET_SMOKE=PASS loaded=%d" % loaded)
    quit(0)

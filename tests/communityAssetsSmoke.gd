extends SceneTree

func _initialize() -> void:
    for item in ["building-a", "chimney-large", "shipping-container-a"]:
        var packed := load("res://assets/community/industrial/%s.glb" % item) as PackedScene
        if packed == null:
            push_error("Missing community prop: " + item)
            quit(1)
            return
        var instance := packed.instantiate()
        var meshes := instance.find_children("*", "MeshInstance3D", true, false)
        if meshes.is_empty():
            push_error("Community prop has no mesh: " + item)
            instance.free()
            quit(1)
            return
        instance.free()
    print("COMMUNITY ASSETS SMOKE PASS")
    quit(0)

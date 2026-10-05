extends SceneTree

func _initialize() -> void:
    var packed := load("res://scenes/YumeCutsceneFactoryProof.tscn")
    if packed == null:
        push_error("YUME_SMOKE_RED scene failed to load")
        quit(1)
        return

    var instance := packed.instantiate()
    root.add_child(instance)

    var required := [
        NodePath("WorldEnvironment"),
        NodePath("HeroProxy"),
        NodePath("KeyLight"),
        NodePath("CameraRig/Camera3D"),
    ]
    for path in required:
        if not instance.has_node(path):
            push_error("YUME_SMOKE_RED missing node: %s" % path)
            quit(2)
            return

    var camera := instance.get_node("CameraRig/Camera3D") as Camera3D
    if camera == null or not camera.current:
        push_error("YUME_SMOKE_RED camera is not current")
        quit(3)
        return

    print("GREEN_YUME_CUTSCENE_SMOKE")
    quit(0)

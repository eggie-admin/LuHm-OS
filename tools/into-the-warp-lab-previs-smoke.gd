extends SceneTree
## Validate the instantiated scene after Node._ready has built its procedural set.

var _stage: Node

func _initialize() -> void:
    var scene := load("res://scenes/into-the-warp-lab-previs.tscn") as PackedScene
    if scene == null:
        push_error("LAB_PREVIS_RED no scene")
        quit(1)
        return
    _stage = scene.instantiate()
    root.add_child(_stage)
    call_deferred("_verify_built_scene")

func _verify_built_scene() -> void:
    for path in ["LaboratorySet/BenchTop", "Monitor01/CRT", "Monitor02/CRT",
                 "Monitor03/CRT", "Monitor04/CRT", "EggieHumanProxy/HumanHead",
                 "EggieHumanProxy/RoundWireGlasses", "LumOniProxy/AuburnUpdo",
                 "PrevisCamera", "ReviewSlate/SourceBoundary"]:
        if not _stage.has_node(NodePath(path)):
            push_error("LAB_PREVIS_RED missing " + path)
            quit(2)
            return
    var camera := _stage.get_node("PrevisCamera") as Camera3D
    if camera == null or not camera.current:
        push_error("LAB_PREVIS_RED camera")
        quit(3)
        return
    print("GREEN_LAB_PREVIS_GODOT_IMPORT proxy_only=true monitors=4")
    quit(0)

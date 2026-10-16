extends SceneTree

func _initialize() -> void:
    var scene := load("res://scenes/into-the-warp-lab-previs.tscn") as PackedScene
    if scene == null:
        push_error("LAB_PREVIS_RED no scene")
        quit(1)
        return
    var stage := scene.instantiate()
    root.add_child(stage)
    for path in ["LaboratorySet/BenchTop", "Monitor01/CRT", "Monitor02/CRT",
                 "Monitor03/CRT", "Monitor04/CRT", "EggieHumanProxy/HumanHead",
                 "EggieHumanProxy/RoundWireGlasses", "LumOniProxy/AuburnUpdo",
                 "PrevisCamera", "ReviewSlate/SourceBoundary"]:
        if not stage.has_node(NodePath(path)):
            push_error("LAB_PREVIS_RED missing " + path)
            quit(2)
            return
    print("GREEN_LAB_PREVIS_GODOT_IMPORT proxy_only=true monitors=4")
    quit(0)

extends SceneTree

func _initialize() -> void:
    call_deferred("_run")

func _run() -> void:
    var scene := load("res://scenes/Main.tscn") as PackedScene
    assert(scene != null)
    var game: Node = scene.instantiate()
    root.add_child(game)

    for _frame in range(4):
        await process_frame

    var world := game.get_node_or_null("NeonWorld") as Node3D
    assert(world != null)
    assert(world.get_node_or_null("CoffeeHouseSetDress") != null)
    assert(world.get_node_or_null("PrivateNexusSetDress") != null)

    var lum := world.get_node_or_null("LumAvatarSocket") as Node3D
    assert(lum != null)
    assert(lum.position.z > 10.0)

    var coffee := world.get_node_or_null("CoffeeHouseSetDress")
    assert(coffee.get_node_or_null("KissatenFloor") != null)
    assert(coffee.get_node_or_null("OniCoffeeSign") != null)

    print("FINAL_COFFEE_HOUSE_SMOKE=PASS")
    game.queue_free()
    quit(0)

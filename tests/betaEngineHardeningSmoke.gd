extends SceneTree

func _initialize() -> void:
    call_deferred("_run")

func _run() -> void:
    var scene := load("res://scenes/Main.tscn") as PackedScene
    assert(scene != null)
    var game := scene.instantiate()
    root.add_child(game)
    for _frame in range(24):
        await process_frame
    var beta := game.get_node_or_null("BetaEngineDirector")
    assert(beta != null)
    var world := game.get_node_or_null("NeonWorld") as Node3D
    assert(world != null)
    var env_node := world.get_node_or_null("WorldEnvironment") as WorldEnvironment
    assert(env_node != null)
    assert(env_node.environment != null)
    assert(env_node.environment.tonemap_mode == Environment.TONE_MAPPER_ACES)
    assert(env_node.environment.glow_enabled)
    assert(world.get_node_or_null("BetaLumHeroKey") != null)
    assert(world.get_node_or_null("BetaLumFill") != null)
    var registry = JSON.parse_string(FileAccess.get_file_as_string("res://assets/registry/BETA_ASSET_SOURCES_V1.json"))
    assert(registry is Dictionary)
    assert(registry.get("runtimeNetwork", true) == false)
    var sources = registry.get("sources", [])
    assert(sources is Array and sources.size() >= 6)
    var summary: Dictionary = beta.call("get_beta_summary")
    assert(summary.has("renderer"))
    assert(summary.has("facial"))
    assert(summary.has("secondary_motion"))
    assert(summary.has("private_mods"))
    var renderer := RenderingServer.get_current_rendering_method()
    assert(renderer in ["gl_compatibility", "mobile", "forward_plus"])
    print("GODOT4_BETA_ENGINE_SMOKE=PASS renderer=%s source_lanes=%d" % [renderer, sources.size()])
    game.queue_free()
    quit(0)

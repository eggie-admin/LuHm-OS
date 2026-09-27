extends SceneTree

func _initialize() -> void:
    call_deferred("_run")

func _run() -> void:
    var scene := load("res://scenes/Main.tscn") as PackedScene
    assert(scene != null)
    var game := scene.instantiate()
    root.add_child(game)
    for _frame in range(30):
        await process_frame

    var beta := game.get_node_or_null("BetaEngineDirector")
    assert(beta != null)
    var world := game.get_node_or_null("NeonWorld") as Node3D
    assert(world != null)

    var env_node := world.get_node_or_null("WorldEnvironment") as WorldEnvironment
    assert(env_node != null and env_node.environment != null)
    assert(env_node.environment.tonemap_mode == Environment.TONE_MAPPER_ACES)
    assert(env_node.environment.glow_enabled)
    assert(world.get_node_or_null("BetaLumHeroKey") != null)
    assert(world.get_node_or_null("BetaLumFill") != null)

    var community := world.get_node_or_null("CommunityCathedralSetDress") as Node3D
    assert(community != null)
    var asset_summary: Dictionary = community.call("get_runtime_asset_summary") as Dictionary
    assert(int(asset_summary.get("expected", 0)) == 77)
    assert(int(asset_summary.get("loaded", 0)) == 77)
    assert(int(asset_summary.get("missing", 1)) == 0)

    var lum := world.get_node_or_null("LumAvatarSocket") as Node3D
    assert(lum != null)
    assert(bool(lum.call("uses_external_model")))
    var rig: Dictionary = lum.call("get_rig_summary") as Dictionary
    assert(int(rig.get("skeleton_bones", 0)) >= 24)
    assert(int(rig.get("canonical_required", 0)) == 22)
    assert(int(rig.get("canonical_mapped", 0)) == 22)
    assert(bool(rig.get("running_asset_present", false)))
    assert(bool(rig.get("animation_tree_active", false)))

    var registry = JSON.parse_string(FileAccess.get_file_as_string("res://assets/registry/BETA_ASSET_SOURCES_V1.json"))
    assert(registry is Dictionary and registry.get("runtimeNetwork", true) == false)
    var capmap = JSON.parse_string(FileAccess.get_file_as_string("res://assets/registry/GODOT4_COMMUNITY_CAPABILITY_MAP_V1.json"))
    assert(capmap is Dictionary)
    assert(int(capmap.get("referenceCount", 0)) == 20)
    assert((capmap.get("capabilities", []) as Array).size() == 20)

    var summary: Dictionary = beta.call("get_beta_summary")
    assert(summary.has("renderer"))
    assert(summary.has("facial"))
    assert(summary.has("secondary_motion"))
    assert(summary.has("private_mods"))
    var renderer := RenderingServer.get_current_rendering_method()
    assert(renderer in ["gl_compatibility", "mobile", "forward_plus"])
    print("GODOT4_BETA_ENGINE_SMOKE=PASS renderer=%s community=77 rig_bones=%d mapped=22 capability_sources=20" % [renderer, int(rig.get("skeleton_bones", 0))])
    game.queue_free()
    quit(0)

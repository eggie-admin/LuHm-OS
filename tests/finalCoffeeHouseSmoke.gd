extends SceneTree

func _initialize() -> void:
    call_deferred("_run")

func _run() -> void:
    var scene := load("res://scenes/Main.tscn") as PackedScene
    assert(scene != null)
    var game: Node = scene.instantiate()
    root.add_child(game)

    for _frame in range(8):
        await process_frame

    # Let intro/pulse/restore finish; early node existence missed scale regressions.
    await create_timer(6.0).timeout

    var world := game.get_node_or_null("NeonWorld") as Node3D
    assert(world != null)
    assert(world.get_node_or_null("CoffeeHouseSetDress") != null)
    assert(world.get_node_or_null("CrownCathedralSetDress") != null)
    assert(world.get_node_or_null("CrownDonorGallery") != null)
    assert(world.get_node_or_null("PrivateNexusSetDress") != null)

    var crown := world.get_node_or_null("CrownCathedralSetDress") as Node3D
    assert(crown.get_node_or_null("CrownCathedralSign") != null)
    assert(crown.get_node_or_null("CrownGateTop") != null)
    assert(crown.get_node_or_null("RoofRidge") != null)

    var gallery := world.get_node_or_null("CrownDonorGallery") as Node3D
    assert(gallery != null)
    assert(gallery.get_node_or_null("CathedralArchiveHolo/ArchiveTexture") != null)
    assert(gallery.get_node_or_null("LumRetroShrine/ArchiveTexture") != null)
    var donor_summary: Dictionary = gallery.call("get_donor_summary") as Dictionary
    assert(int(donor_summary.get("expected", 0)) == 2)
    assert(int(donor_summary.get("loaded", 0)) == 2)
    assert(str(donor_summary.get("scope", "")) == "LUHM_OS_FULL_GAME_ONLY")
    assert(bool(donor_summary.get("kai9000_authority", true)) == false)

    var community := world.get_node_or_null("CommunityCathedralSetDress") as Node3D
    assert(community != null)
    var asset_summary: Dictionary = community.call("get_runtime_asset_summary") as Dictionary
    assert(int(asset_summary.get("expected", 0)) == 77)
    assert(int(asset_summary.get("loaded", 0)) == 77)
    assert(int(asset_summary.get("missing", 1)) == 0)

    var lum := world.get_node_or_null("LumAvatarSocket") as Node3D
    assert(lum != null)
    assert(lum.position.z > 13.0)
    assert(bool(lum.call("uses_external_model")))

    var overlay := game.get_node_or_null("FinalCoffeeHouseMutation") as Node3D
    assert(overlay != null)
    var lum_height := float(overlay.call("_measure_visual_height", lum))
    assert(lum_height > 1.70 and lum_height < 2.10)

    var player := game.get_node_or_null("PlayerController") as CharacterBody3D
    assert(player != null)
    assert(player.position.z > 10.0)
    await physics_frame
    await process_frame
    var camera := player.get_node("CameraYaw/CameraPitch/SpringArm3D/Camera3D") as Camera3D
    var size := root.get_visible_rect().size
    var feet := lum.global_position + Vector3(0, 0.05, 0)
    var head := feet + Vector3(0, lum_height, 0)
    assert(not camera.is_position_behind(head))
    var head_uv := camera.unproject_position(head) / size
    var feet_uv := camera.unproject_position(feet) / size
    var fraction := feet_uv.y - head_uv.y
    assert(fraction > 0.55 and fraction < 0.90)
    assert(head_uv.y > 0.02 and feet_uv.y < 0.98)
    assert(absf(head_uv.x - 0.5) < 0.10)
    print("LUM_FOCUS_PROJECTION=PASS height_fraction=%.3f" % fraction)

    var coffee := world.get_node_or_null("CoffeeHouseSetDress") as Node3D
    assert(coffee.get_node_or_null("KissatenFloor") != null)
    assert(coffee.get_node_or_null("OniCoffeeSign") != null)

    print("CROWN_CATHEDRAL_SCENE_SMOKE=PASS assets=77 donors=2 lum_height=%.3f" % lum_height)
    game.queue_free()
    quit(0)

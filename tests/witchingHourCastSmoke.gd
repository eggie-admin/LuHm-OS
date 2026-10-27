extends SceneTree
## Exact-source headless scene acceptance: actual original Cathedral instantiation,
## mobile-sized controls, button signal, and start of the bounded casting sequence.

func _initialize() -> void:
    call_deferred("_smoke")

func _fail(reason: String) -> void:
    push_error("WITCHING_HOUR_CAST_RED: " + reason)
    quit(1)

func _smoke() -> void:
    var packed := load("res://scenes/WitchingHourFinalBoss.tscn") as PackedScene
    if packed == null:
        _fail("scene not loadable")
        return
    var scene := packed.instantiate() as Node3D
    if scene == null:
        _fail("scene not Node3D")
        return
    root.add_child(scene)
    await process_frame

    if not (scene.get_node_or_null("CathedralWorld/Altar") is StaticBody3D):
        _fail("real cathedral altar missing")
        return
    if scene.get_node_or_null("CathedralWorld/LumAvatarSocket") == null:
        _fail("real Lum socket missing")
        return
    var button := scene.get_node_or_null("CastingHud/SafeControls/Actions/CastFourFlames") as Button
    var back := scene.get_node_or_null("CastingHud/SafeControls/Actions/ReturnToCathedral") as Button
    if button == null or back == null:
        _fail("touch-safe cast/back controls missing")
        return

    button.pressed.emit()
    await process_frame
    var casting := scene.get_node_or_null("CathedralWorld/WitchingHourCast")
    if casting == null or not bool(casting.get("_casting")):
        _fail("user-requested casting did not start")
        return
    if not button.disabled:
        _fail("duplicate cast not blocked")
        return
    if scene.get_node_or_null("CathedralWorld/WitchingHourCast/SkuldLightCandidate") == null:
        _fail("first actual light summon missing")
        return
    if scene.get_node_or_null("CathedralWorld/Altar") == null:
        _fail("base geometry was deleted")
        return

    print("WITCHING_HOUR_CAST_SCOPED_GREEN scene+altar+Lum+buttons+first_cast")
    quit(0)

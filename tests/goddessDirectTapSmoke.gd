extends SceneTree
## Exercise 3D hit targeting without requiring private rig or textures.
const IDS := ["lum", "urd", "belldandy", "skuld"]
var failures: Array[String] = []

func _initialize() -> void:
    call_deferred("_run")

func _check(ok: bool, label: String) -> void:
    if not ok:
        failures.append(label)
        push_error("RED_GODDESS_TAP: " + label)

func _run() -> void:
    var packed := load("res://scenes/GoddessRehearsal.tscn") as PackedScene
    _check(packed != null, "sceneLoads")
    if packed == null:
        _finish()
        return
    var scene := packed.instantiate()
    root.add_child(scene)
    await process_frame
    await process_frame
    var camera := scene.get_viewport().get_camera_3d()
    _check(camera != null, "cameraExists")
    if camera == null:
        _finish()
        return

    var lum_socket := scene.get_node_or_null("lum/LumRigSocket") as Node3D
    _check(lum_socket != null, "existingLumAvatarReused")
    var rig_staged := ResourceLoader.exists("res://assets/lum/luhm.glb")
    if lum_socket != null:
        _check(bool(lum_socket.call("uses_external_model")) == rig_staged, "rigPresenceReported")
        if rig_staged:
            var summary: Dictionary = lum_socket.call("get_rig_summary")
            _check(int(summary.get("skeleton_bones", 0)) == 24, "rig24Bones")
            _check(int(summary.get("canonical_mapped", 0)) == 22, "rig22MappedRoles")
            _check(bool(scene.get("_lum_rig_loaded")), "rehearsalUsesActualRig")
        else:
            _check(not bool(scene.get("_lum_rig_loaded")), "fallbackWithoutAsset")
    for i in IDS.size():
        var actor := scene.get_node_or_null(IDS[i]) as Node3D
        _check(actor != null, "actorExists:" + IDS[i])
        if actor == null:
            continue
        var focus := actor.get_node_or_null("TapFocus") as Node3D
        _check(focus != null, "focusMarker:" + IDS[i])
        var point := camera.unproject_position(actor.global_position + Vector3(0, 1.6, 0))
        if i % 2 == 0:
            var mouse := InputEventMouseButton.new()
            mouse.button_index = MOUSE_BUTTON_LEFT
            mouse.position = point
            mouse.pressed = true
            scene._unhandled_input(mouse)
        else:
            var touch := InputEventScreenTouch.new()
            touch.position = point
            touch.pressed = true
            scene._unhandled_input(touch)
        await process_frame
        _check(int(scene.get("active_index")) == i, "tapSelects:" + IDS[i])
        if focus != null:
            _check(focus.visible, "focusVisible:" + IDS[i])
        var message: Label = scene.get("message") as Label
        _check(message != null and message.text.to_lower().contains(IDS[i]), "dialogueIdentity:" + IDS[i])

    # In-process Godot behavior assertions, not just source token checks.
    # No donor upload, Web build, release, or external API call.
    var stageMessage: Label = scene.get("message") as Label
    _check(stageMessage != null, "interactionMessageExists")
    var bondValues: Array = scene.get("_bond_points")
    var dialogueTurns: Array = scene.get("_dialogue_turns")
    _check(bondValues.size() == IDS.size(), "fourBondRoutes")
    _check(dialogueTurns.size() == IDS.size(), "fourDialogueRoutes")
    for i in IDS.size():
        scene.call("_select", i)
        scene.call("_talk")
        _check(int(bondValues[i]) == 1, "talkEarnsBond:" + IDS[i])
        _check(int(dialogueTurns[i]) == 1, "talkAdvancesRoute:" + IDS[i])
        _check(stageMessage.text.to_lower().contains(IDS[i]), "talkIdentifiesCast:" + IDS[i])
        scene.call("_dance")
        _check(int(bondValues[i]) == 2, "danceEarnsBond:" + IDS[i])
        _check(str(scene.call("_route_status")).contains("BOND 2/9"), "visibleBondStatus:" + IDS[i])

    _check(str(scene.call("_route_status")).contains("CATHEDRAL CIRCLE COMPLETE"), "fourRouteQuestComplete")
    scene.call("_select", 0)
    for turn in 8:
        scene.call("_talk")
    _check(int(bondValues[0]) == 9, "bondCappedAtNine")
    _check(int(dialogueTurns[0]) == 9, "dialogueRepeatsSafely")

    var talkKey := InputEventKey.new()
    talkKey.keycode = KEY_T
    talkKey.pressed = true
    var previousTurn := int(dialogueTurns[0])
    scene._unhandled_input(talkKey)
    _check(int(dialogueTurns[0]) == previousTurn + 1, "keyboardTalkRoute")

    var danceKey := InputEventKey.new()
    danceKey.keycode = KEY_D
    danceKey.pressed = true
    var previousDance := float(scene.get("_dance_until"))
    scene._unhandled_input(danceKey)
    _check(float(scene.get("_dance_until")) >= previousDance, "keyboardDanceRoute")

    # The mobile action grid must remain tappable on a narrow Android viewport.
    root.size = Vector2i(320, 700)
    await process_frame
    scene.call("_refresh_hud_layout")
    var actionGrid: GridContainer = scene.get("_action_grid") as GridContainer
    var selectorGrid: GridContainer = scene.get("_selector_grid") as GridContainer
    _check(actionGrid != null and actionGrid.columns == 1, "narrowTouchActionStack")
    _check(selectorGrid != null and selectorGrid.columns == 2, "narrowTouchSelectorPairs")
    _finish()

func _finish() -> void:
    if failures.is_empty():
        print("GODDESS_DIRECT_TAP_SMOKE_GREEN")
        print("GODDESS_INTERACTION_LOOP_GREEN")
        if ResourceLoader.exists("res://assets/lum/luhm.glb"):
            print("GODDESS_LUM_RIG_IN_REHEARSAL_GREEN")
        quit(0)
    else:
        push_error("GODDESS_DIRECT_TAP_SMOKE_RED: " + ", ".join(failures))
        quit(1)

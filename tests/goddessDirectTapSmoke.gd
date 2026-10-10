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
    _finish()

func _finish() -> void:
    if failures.is_empty():
        print("GODDESS_DIRECT_TAP_SMOKE_GREEN")
        quit(0)
    else:
        push_error("GODDESS_DIRECT_TAP_SMOKE_RED: " + ", ".join(failures))
        quit(1)

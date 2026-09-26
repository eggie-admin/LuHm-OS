extends SceneTree

var failures: Array[String] = []

func _initialize() -> void:
    call_deferred("_run")

func check(ok: bool, label: String) -> void:
    if not ok:
        failures.append(label)
        push_error(label)

func _run() -> void:
    var viewport := SubViewport.new()
    viewport.size = Vector2i(720, 1560)
    root.add_child(viewport)
    var hud = load("res://scripts/game/gameHud.gd").new()
    viewport.add_child(hud)
    await process_frame
    var profiles := [
        Vector2i(720, 1560),
        Vector2i(1560, 720),
        Vector2i(720, 1152),
        Vector2i(1152, 720),
        Vector2i(720, 720),
        Vector2i(1080, 2340),
        Vector2i(2340, 1080)
    ]
    for dimensions in profiles:
        viewport.size = dimensions
        await process_frame
        var safe := Rect2(Vector2(48, 36), Vector2(dimensions) - Vector2(96, 84))
        hud.show_world()
        hud.apply_layout(Vector2(dimensions), safe)
        hud.show_dialogue("Professor, the Crown is yours. Return to Cathedral when ready.")
        await process_frame
        var controls: Array[Control] = hud.layout_controls()
        for control in controls:
            check(safe.encloses(control.get_global_rect()), "%s stays in safe area at %s" % [control.name, dimensions])
        for i in range(controls.size()):
            for j in range(i + 1, controls.size()):
                check(not controls[i].get_global_rect().intersects(controls[j].get_global_rect()), "HUD controls do not overlap at %s" % dimensions)
        for button in hud._pads:
            check(button.size.x >= 80 and button.size.y >= 80, "movement target minimum")
        var press := InputEventScreenTouch.new()
        press.index = 3
        press.position = hud._pads[0].get_global_rect().get_center()
        press.pressed = true
        hud._input(press)
        check(hud._touch_axis == Vector2.UP, "touch fixture starts movement")
        var other := InputEventScreenTouch.new()
        other.index = 4
        other.pressed = false
        hud._input(other)
        check(hud._touch_axis == Vector2.UP, "other finger cannot release movement")
        hud.apply_layout(Vector2(dimensions), safe)
        check(hud._touch_axis == Vector2.ZERO and hud._touch_owner == -1, "rotation releases held movement")
        hud._input(press)
        hud.notification(Node.NOTIFICATION_APPLICATION_FOCUS_OUT)
        check(hud._touch_axis == Vector2.ZERO, "focus loss releases movement")
        hud._set_touch_axis(Vector2.RIGHT)
        hud.show_backend()
        check(hud._touch_axis == Vector2.ZERO and hud.backend_root.visible and not hud.world_root.visible, "Cathedral return clears held movement")
        check(safe.encloses(hud._scroll.get_global_rect()), "Cathedral scroll stays in safe area")
        check(hud._audit_switch != null, "audit seal switch exists")
        check(hud._audit_switch.custom_minimum_size.y >= 88, "audit seal switch touch target minimum")
        hud._set_audit_panel(true)
        check(hud._audit_panel.visible, "audit seal panel opens")
        check(hud._audit_panel.text.contains("GREEN_DOCUMENTATION_WORKFLOW"), "audit workflow status loads from doctrine")
        check(hud._audit_panel.text.contains("GREEN_DOCUMENTATION_SEAL"), "audit seal status loads from doctrine")
        check(hud._audit_panel.text.contains("RUNTIME · UNCHANGED"), "audit panel preserves runtime boundary")
        check(hud._audit_panel.text.contains("RELEASE · UNCHANGED"), "audit panel preserves release boundary")
        hud._set_audit_panel(false)
        check(not hud._audit_panel.visible, "audit seal panel closes")
        print("LAYOUT PROFILE VERIFIED ", dimensions)
    viewport.queue_free()
    await process_frame
    if failures.is_empty():
        print("SAMSUNG ORIENTATION HARNESS PASS")
        quit(0)
    else:
        quit(1)

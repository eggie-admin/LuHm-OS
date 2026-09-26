extends SceneTree

const RitualDirectorScript := preload("res://scripts/game/ritualDirector.gd")

class FakeWorld:
    extends Node
    var calls: Array[String] = []

    func crown_pulse() -> void:
        calls.append("crown_pulse")
        await get_tree().process_frame

    func pet_lum() -> void:
        calls.append("pet_lum")

    func oni_pop() -> void:
        calls.append("oni_pop")

    func pulse_lum(_duration: float) -> void:
        calls.append("pulse_lum")

    func set_lum_expression(_name: String, _weight: float = 1.0) -> void:
        calls.append("expression")

    func restore_lum() -> void:
        calls.append("restore_lum")

class FakeBridge:
    extends Node
    signal ritual_requested(ritual_id: String)
    var replies: Array[Dictionary] = []

    func post_reply(reply: Dictionary) -> void:
        replies.append(reply)

class FakeHud:
    extends CanvasLayer
    var statuses: Array[String] = []

    func set_status(message: String) -> void:
        statuses.append(message)

var failures: Array[String] = []

func _initialize() -> void:
    call_deferred("_run")

func _run() -> void:
    var world := FakeWorld.new()
    var bridge := FakeBridge.new()
    var hud := FakeHud.new()
    var director := RitualDirectorScript.new()
    root.add_child(world)
    root.add_child(bridge)
    root.add_child(hud)
    root.add_child(director)
    director.configure(world, bridge, hud)
    director.set_test_step_seconds(0.001)

    _check(director.get_ritual_ids() == ["crown_wake", "oni_trinity", "witching_hour"], "three ritual allowlist")
    director.start("unknown")
    _check(not director.is_busy(), "unknown ritual fails closed")
    _check(String(bridge.replies[-1].get("payload", {}).get("state", "")) == "rejected", "unknown ritual receipt")

    var finished := false
    director.ritual_finished.connect(func(id: String, status: String):
        if id == "witching_hour" and status == "complete":
            finished = true
    )
    bridge.ritual_requested.emit("witching_hour")
    for _i in range(30):
        await process_frame
        if finished:
            break

    _check(finished, "witching hour completes")
    _check("oni_pop" in world.calls, "witching hour calls oni effect")
    _check("crown_pulse" in world.calls, "witching hour calls crown effect")
    _check("pulse_lum" in world.calls, "witching hour calls Lum pulse")
    _check("restore_lum" in world.calls, "ritual restores Lum")
    _check(not director.is_busy(), "director returns idle")
    _finish()

func _check(condition: bool, label: String) -> void:
    if condition:
        print("GREEN: ", label)
    else:
        failures.append(label)
        push_error("RED: %s" % label)

func _finish() -> void:
    if failures.is_empty():
        print("WITCHING HOUR THREE RITUAL SMOKE GREEN")
        quit(0)
    else:
        push_error("WITCHING HOUR THREE RITUAL SMOKE RED: %s" % ", ".join(failures))
        quit(1)

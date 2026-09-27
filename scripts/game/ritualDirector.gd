extends Node

signal ritual_finished(ritual_id: String, status: String)

const DoctrineGateScript := preload("res://scripts/core/doctrineGate.gd")

var world: Node3D
var bridge: Node
var hud: CanvasLayer
var _busy := false
var _generation := 0
var _step_seconds := 0.22
var _doctrine = DoctrineGateScript.new()

func _ready() -> void:
    if _doctrine.get_parent() == null:
        add_child(_doctrine)

func configure(world_node: Node3D, bridge_node: Node, hud_node: CanvasLayer) -> void:
    world = world_node
    bridge = bridge_node
    hud = hud_node
    if bridge != null and bridge.has_signal("ritual_requested"):
        bridge.ritual_requested.connect(start)

func get_ritual_ids() -> Array:
    return _doctrine.get_allowed_rituals()

func is_busy() -> bool:
    return _busy

func set_test_step_seconds(value: float) -> void:
    _step_seconds = clampf(value, 0.001, 0.22)

func start(ritual_id: String) -> void:
    if not _doctrine.is_valid():
        _post(ritual_id, "doctrine_fault")
        return
    if not _doctrine.allows_ritual(ritual_id):
        _post(ritual_id, "rejected")
        return
    if _busy:
        _post(ritual_id, "busy")
        return
    _generation += 1
    _busy = true
    var ticket := _generation
    _post(ritual_id, "starting")
    call_deferred("_run", ritual_id, ticket)

func cancel() -> void:
    _generation += 1
    _busy = false
    if world != null and world.has_method("restore_lum"):
        world.restore_lum()
    _post("none", "cancelled")

func _run(ritual_id: String, ticket: int) -> void:
    match ritual_id:
        "crown_wake":
            await _crown_wake(ticket)
        "oni_trinity":
            await _oni_trinity(ticket)
        "witching_hour":
            await _witching_hour(ticket)
        _:
            _busy = false
            _post(ritual_id, "rejected")
            return

    if ticket != _generation:
        return
    _busy = false
    if world != null and world.has_method("restore_lum"):
        world.restore_lum()
    _set_status("☾ RITUAL COMPLETE // %s" % ritual_id.to_upper())
    _post(ritual_id, "complete")
    ritual_finished.emit(ritual_id, "complete")

func _crown_wake(ticket: int) -> void:
    _set_status("♛ RITUAL I // CROWN WAKE")
    if world != null and world.has_method("crown_pulse"):
        await world.crown_pulse()
    var active := await _step(ticket)
    if not active:
        return
    if world != null and world.has_method("pet_lum"):
        world.pet_lum()
    await _step(ticket)

func _oni_trinity(ticket: int) -> void:
    _set_status("👹 RITUAL II // ONI TRINITY")
    if world != null and world.has_method("oni_pop"):
        world.oni_pop()
    if world != null and world.has_method("pulse_lum"):
        world.pulse_lum(0.8)
    var active := await _step(ticket)
    if not active:
        return
    if world != null and world.has_method("crown_pulse"):
        await world.crown_pulse()
    await _step(ticket)

func _witching_hour(ticket: int) -> void:
    _set_status("☾ RITUAL III // WITCHING HOUR")
    if world != null and world.has_method("oni_pop"):
        world.oni_pop()
    if world != null and world.has_method("set_lum_expression"):
        world.set_lum_expression("talk", 0.55)
    var active := await _step(ticket)
    if not active:
        return
    if world != null and world.has_method("crown_pulse"):
        await world.crown_pulse()
    active = await _step(ticket)
    if not active:
        return
    if world != null and world.has_method("pulse_lum"):
        world.pulse_lum(1.0)
    await _step(ticket)

func _step(ticket: int) -> bool:
    await get_tree().create_timer(_step_seconds).timeout
    return ticket == _generation

func _set_status(message: String) -> void:
    if hud != null and hud.has_method("set_status"):
        hud.set_status(message)

func _post(ritual_id: String, state: String) -> void:
    if bridge == null or not bridge.has_method("post_reply"):
        return
    bridge.post_reply({
        "schema": "luhm.bridge.reply.v1",
        "type": "ritual.status",
        "payload": {
            "ritual": ritual_id,
            "state": state,
            "busy": _busy,
            "allowed": _doctrine.get_allowed_rituals(),
            "doctrine_valid": _doctrine.is_valid()
        }
    })

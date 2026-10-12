extends SceneTree
# CI source truth for four proof stations; one real Lum donor, three missing bodies.
var failures: Array[String] = []
func _initialize() -> void:
    call_deferred("_run")

func _run() -> void:
    var packed = load("res://scenes/GoddessLineupProof.tscn")
    if not packed is PackedScene:
        _check(false, "lineup scene is a PackedScene")
        _finish()
        return
    var stage := (packed as PackedScene).instantiate() as Node3D
    root.add_child(stage)
    _check(stage.actors.size() == 4, "four distinct stations created")
    var receipts: Dictionary = stage.lineup_receipts()
    _check(receipts.size() == 4, "four runtime state receipts preserved")
    for character_id in ["lum", "urd", "belldandy", "skuld"]:
        var avatar: Node3D = stage.actors.get(character_id)
        _check(avatar != null, character_id + " scene exists")
        if avatar == null:
            continue
        var socket: Node3D = avatar.get_node("BodySocket")
        var record: Dictionary = receipts.get(character_id, {})
        _check(record.get("character") == character_id, character_id + " source identity")
        var components: Dictionary = record.get("componentReceipt", {})
        _check(components.get("canonPromoted") == false, character_id + " remains candidate")
        if character_id == "lum":
            _check(socket.get_child_count() == 1, "Lum donor visible as assembled body")
            _check(int(components.get("blockerCount", 100)) == 0, "Lum model mounted")
        else:
            _check(socket.get_child_count() == 0, character_id + " has no fake 3D body")
            _check(int(components.get("blockerCount", 0)) > 0, character_id + " missing body blocks")
        var label: Label3D = avatar.get_parent().get_node("StatusLabel")
        _check(label.text.find(character_id.to_upper()) >= 0, character_id + " label assigned")
    print("LINEUP_TRUTH=lum:riggedCandidate,urd:bodyMissing,belldandy:bodyMissing,skuld:bodyMissing")
    stage.free()
    _finish()

func _check(ok: bool, label: String) -> void:
    if ok:
        print("GREEN: ", label)
    else:
        failures.append(label)
        push_error("RED_GODDESS_LINEUP: " + label)

func _finish() -> void:
    if failures.is_empty():
        print("GODDESS_LINEUP_RUNTIME_SMOKE_GREEN")
        quit(0)
    else:
        print("GODDESS_LINEUP_RUNTIME_SMOKE_RED: ", ", ".join(failures))
        quit(1)

extends SceneTree
# Real Godot 4.7 runtime regression, with hashed donor injected by the proof job.
var failures: Array[String] = []

func _initialize() -> void:
    call_deferred("_run")

func _run() -> void:
    var scene = load("res://scenes/GoddessAvatar.tscn")
    if not scene is PackedScene:
        _check(false, "GoddessAvatar must import as PackedScene")
        _finish()
        return
    var avatar := (scene as PackedScene).instantiate() as Node3D
    root.add_child(avatar)
    var assembler: Node = avatar.get_node("ComponentAssembler")
    var body: Node3D = avatar.get_node("BodySocket")
    var hair: Node3D = avatar.get_node("HairSocket")
    _check(assembler != null, "assembler attached to running avatar")

    # Seed intentionally stale geometry, then switch to a character with no body.
    var stale_body := MeshInstance3D.new()
    stale_body.name = "previousLumBody"
    body.add_child(stale_body)
    var stale_hair := MeshInstance3D.new()
    stale_hair.name = "previousLumHair"
    hair.add_child(stale_hair)

    for character_id in ["urd", "belldandy", "skuld"]:
        var stale := MeshInstance3D.new()
        stale.name = "staleBefore" + character_id
        body.add_child(stale)
        var receipt: Dictionary = assembler.assemble_character(character_id)
        _check(int(receipt.get("blockerCount", 0)) > 0, character_id + " missing required body blocks")
        _check("body:unassigned" in receipt.get("blockers", []), character_id + " names missing source")
        _check(body.get_child_count() == 0, character_id + " stale body cleared immediately")
        _check(hair.get_child_count() == 0, character_id + " stale hair cleared immediately")
        _check(receipt.get("canonPromoted") == false, character_id + " cannot self-promote")

    # Lum uses the exact SHA-verified donor generated in the isolated CI runner.
    var lum: Dictionary = assembler.assemble_character("lum")
    _check(int(lum.get("blockerCount", 0)) == 0, "Lum imported body has no blocker")
    _check(int(lum.get("appliedCount", 0)) == 1, "Lum body mounted through actual PackedScene")
    _check(body.get_child_count() == 1, "Lum body socket contains one real node")
    var u: Dictionary = assembler.assemble_character("urd")
    _check(int(u.get("blockerCount", 0)) > 0, "switch Lum to Urd blocks unassigned body")
    _check(body.get_child_count() == 0, "switch Lum to Urd removes prior body without a frame of overlap")

    var invalid: Dictionary = assembler.assemble_character("unregistered")
    _check(int(invalid.get("blockerCount", 0)) > 0, "unknown character rejected")
    _check(body.get_child_count() == 0, "unknown character cannot resurrect previous body")
    _check(assembler.mounted.is_empty(), "no stale mount registry after blocked switch")
    print("FOUR_GODDESS_COMPONENT_SOURCE_STATUS=lum:PROOF_CANDIDATE,urd:MISSING,belldandy:MISSING,skuld:MISSING")
    avatar.free()
    _finish()

func _check(ok: bool, label: String) -> void:
    if ok:
        print("GREEN: ", label)
    else:
        failures.append(label)
        push_error("RED_GODDESS_COMPONENT: " + label)

func _finish() -> void:
    if failures.is_empty():
        print("GODDESS_COMPONENT_RUNTIME_SMOKE_GREEN")
        quit(0)
    else:
        print("GODDESS_COMPONENT_RUNTIME_SMOKE_RED: ", ", ".join(failures))
        quit(1)

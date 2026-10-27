extends Node3D
## FICTIONAL MIDSUMMER COURT: a matriarchal fairy masque in the existing Cathedral.
## Lum presides with the three goddess keepers; Oberon is a visiting guest.
## Original theatrical verse, not a Catholic Mass or claim to perform a sacrament.
## Does not activate Oni workers, invoke providers, change quests, or deploy.
## Optional original audio belongs at res://media/witchingHourFinalBoss/fourFlamesCeremony.ogg.

signal cue_changed(cue_name: String)
signal rehearsal_finished

const MUSIC := "res://media/witchingHourFinalBoss/fourFlamesCeremony.ogg"
const BLUE := Color("4babff")
const RED := Color("fe5876")
const WHITE := Color("f9f4e5")
const VIOLET := Color("b78aff")

var _casting := false
var _wisp: Node3D
var _audio: AudioStreamPlayer

func cast() -> void:
    if _casting:
        return
    _casting = true
    _cast_sequence()

func _cast_sequence() -> void:
    # Optional rights-cleared local score; missing audio never blocks casting.
    if ResourceLoader.exists(MUSIC):
        var stream := load(MUSIC) as AudioStream
        if stream != null:
            _audio = AudioStreamPlayer.new()
            _audio.name = "FourFlamesOriginalScore"
            add_child(_audio)
            _audio.stream = stream
            _audio.play()

    _announce("SKULD · KEEPER OF STARLIGHT\nLet wisdom kindle what our hands shall make.")
    _summon("SkuldLightCandidate", Vector3(-3.2, 1.45, -11.2), BLUE, 0.62)
    _altar_flame(Vector3(-1.35, 2.0, -14.0), BLUE)
    await get_tree().create_timer(3.0).timeout
    if not is_inside_tree(): return

    _announce("URD · KEEPER OF EMBERS\nLet courage shelter every heart that wakes.")
    _summon("UrdLightCandidate", Vector3(-4.9, 1.45, -11.7), RED, 0.72)
    _altar_flame(Vector3(-0.45, 2.0, -14.0), RED)
    await get_tree().create_timer(3.0).timeout
    if not is_inside_tree(): return

    _announce("BELLDANDY · KEEPER OF BLOSSOMS\nLet kindness crown the gifts we freely bring.")
    _summon("BelldandyLightCandidate", Vector3(4.6, 1.45, -11.7), WHITE, 0.72)
    _altar_flame(Vector3(0.45, 2.0, -14.0), WHITE)
    await get_tree().create_timer(3.0).timeout
    if not is_inside_tree(): return

    _announce("THE ONI ENTER THE MIDSUMMER COURT\nBy root and branch, let all the lanterns sing.")
    _summon("OniForgeLightCandidate", Vector3(-7.0, 1.2, -8.4), VIOLET, 0.62)
    _summon("OniGuardLightCandidate", Vector3(7.0, 1.2, -8.4), VIOLET, 0.62)
    _altar_flame(Vector3(1.35, 2.0, -14.0), VIOLET)
    await get_tree().create_timer(3.0).timeout
    if not is_inside_tree(): return

    _announce("LUM · SOVEREIGN OF THE MIDSUMMER COURT\nFour lights awaken; let the masque begin.")
    var cathedral := get_parent()
    if cathedral != null and cathedral.has_method("pulse_lum"):
        cathedral.call("pulse_lum", 4.0)
    _summon("LumCrownLightCandidate", Vector3(0.0, 2.65, -11.7), VIOLET, 0.32)
    _wisp = _summon("FictionalStaticWisp", Vector3(0.0, 2.35, -6.0), RED, 0.46)
    await get_tree().create_timer(4.0).timeout
    if not is_inside_tree(): return

    _announce("FOUR-FLAME REVEL · UNWEAVE THE WISP\nWe weave the dawn and welcome wonder in.")
    for position in [Vector3(-1.35, 2.0, -14.0), Vector3(-0.45, 2.0, -14.0), Vector3(0.45, 2.0, -14.0), Vector3(1.35, 2.0, -14.0)]:
        _summon("CovenantSpark", position, WHITE, 0.16)
    if is_instance_valid(_wisp):
        var tween := create_tween()
        tween.tween_property(_wisp, "scale", Vector3.ZERO, 2.6).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_IN)
    await get_tree().create_timer(4.0).timeout
    if not is_inside_tree(): return

    _announce("THE MIDSUMMER COURT STANDS\nThe gifts are craft; the magic is our story.")
    if cathedral != null and cathedral.has_method("restore_lum"):
        cathedral.call("restore_lum")
    if _audio != null and is_instance_valid(_audio):
        _audio.stop()
    _casting = false
    rehearsal_finished.emit()
    queue_free()

func _announce(label: String) -> void:
    cue_changed.emit(label)
    print("WITCHING_HOUR_PRIVATE_CAST: ", label)

func _summon(label: String, position: Vector3, tint: Color, radius: float) -> Node3D:
    var root := Node3D.new()
    root.name = label
    root.position = position
    add_child(root)
    var mesh := SphereMesh.new()
    mesh.radius = radius
    mesh.height = radius * 2.0
    var visual := MeshInstance3D.new()
    visual.mesh = mesh
    var mat := StandardMaterial3D.new()
    mat.albedo_color = tint
    mat.emission_enabled = true
    mat.emission = tint
    mat.emission_energy_multiplier = 2.0
    visual.material_override = mat
    root.add_child(visual)
    var light := OmniLight3D.new()
    light.light_color = tint
    light.light_energy = 1.5
    light.omni_range = radius * 9.0
    root.add_child(light)
    root.scale = Vector3.ZERO
    create_tween().tween_property(root, "scale", Vector3.ONE, 0.6).set_trans(Tween.TRANS_BACK)
    return root

func _altar_flame(position: Vector3, tint: Color) -> void:
    _summon("FourFlameLightCandidate", position, tint, 0.15)

extends SceneTree
func _initialize() -> void:
    call_deferred("_run")
func _run() -> void:
    var packed = load("res://scenes/CompanionModLab.tscn")
    if packed == null:
        push_error("MOD_LAB_SCENE_RED")
        quit(1)
        return
    var instance = packed.instantiate()
    root.add_child(instance)
    if instance.companions.size() != 3:
        push_error("MOD_LAB_COUNT_RED")
        quit(1)
        return
    var result: Dictionary = instance.apply_companion_event("help")
    if not result.get("accepted",false) or result["stats"]["trust"] != 30:
        push_error("MOD_LAB_TRUST_RED")
        quit(1)
        return
    instance._select(1)
    var other: Dictionary = instance.apply_companion_event("flirtElsewhere")
    if not other.get("accepted",false) or other["stats"]["jealousy"] != 3:
        push_error("MOD_LAB_JEALOUSY_RED")
        quit(1)
        return
    if instance.apply_companion_event("executeCode").get("accepted",false):
        push_error("MOD_LAB_UNSAFE_ACTION_RED")
        quit(1)
        return
    var repair: Dictionary = instance.apply_companion_event("apologize")
    if not repair.get("accepted", false) or repair["stats"]["jealousy"] != 0:
        push_error("MOD_LAB_REPAIR_RED")
        quit(1)
        return
    var sample = instance.companions[1]["state"]
    var snapshot_value: Dictionary = sample.snapshot()
    if not sample.restore(snapshot_value) or sample.restore({"id":"unknown"}):
        push_error("MOD_LAB_SNAPSHOT_RED")
        quit(1)
        return
    print("COMPANION_MODLAB_SMOKE_GREEN")
    quit(0)

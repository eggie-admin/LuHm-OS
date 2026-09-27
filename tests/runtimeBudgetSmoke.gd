extends SceneTree

const RuntimeBudget := preload("res://scripts/game/runtimeBudget.gd")

func _initialize() -> void:
    call_deferred("_run")

func _run() -> void:
    var world := Node3D.new()
    world.name = "RuntimeBudgetSmokeWorld"
    root.add_child(world)

    var budget := RuntimeBudget.new()
    budget.name = "RuntimeBudget"
    root.add_child(budget)
    budget.configure(world, root, "mobile")

    var initial: Dictionary = budget.get_summary()
    assert(str(initial.get("quality", "")) == "HIGH")
    assert(bool(initial.get("adaptive", true)) == false)
    assert(int(initial.get("target_fps", 0)) == 60)
    assert(int(initial.get("low_samples_required", 0)) >= 3)
    assert(int(initial.get("recover_samples_required", 0)) > int(initial.get("low_samples_required", 0)))

    budget.call("_apply_quality", "BALANCED", "smoke")
    var balanced: Dictionary = budget.get_summary()
    assert(str(balanced.get("quality", "")) == "BALANCED")

    print("LUHM_RUNTIME_BUDGET_SMOKE=PASS adaptive_headless=false")
    world.queue_free()
    budget.queue_free()
    quit(0)

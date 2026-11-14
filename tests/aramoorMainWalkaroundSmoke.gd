extends SceneTree
## Proves the actual Main.tscn route rather than only an isolated Godot world factory.
var errors: Array[String] = []

func _initialize() -> void:
    call_deferred("_run")

func _check(condition: bool, description: String) -> void:
    if condition:
        print("GREEN_ARAMOOR_PLAY: ", description)
    else:
        errors.append(description)
        push_error("RED_ARAMOOR_PLAY: " + description)

func _run() -> void:
    var packed: Variant = load("res://scenes/Main.tscn")
    _check(packed is PackedScene, "canonical Main scene loads")
    if not packed is PackedScene:
        quit(1)
        return
    var main: Node3D = (packed as PackedScene).instantiate()
    root.add_child(main)
    var hud: Node = main.get("game_hud")
    var player: CharacterBody3D = main.get("player_controller")
    _check(hud != null and player != null, "HUD and Godot player created")
    if hud == null or player == null:
        quit(1)
        return
    _check(str(main.get("active_world_id")) == "neonRiverwalk", "First Night default preserved")
    main.call("_enter_aramoor_mode")
    _check(str(main.get("active_world_id")) == "aramoorArchipelago", "Aramoor game menu enters world")
    _check(bool(player.get("world_active")), "player movement enabled")
    var world: Node3D = main.get("active_world")
    _check(world != null, "Aramoor scene mounted under main")
    if world == null:
        quit(1)
        return
    _check((world.get("player_spawn") as Vector3).y > 1.0, "player spawn above island floor")
    _check(world.call("get_interaction_points").size() == 9, "nine Godot proximity story sockets")
    var point: Area3D = world.call("get_interaction_points")[0]
    player.global_position = point.global_position + Vector3(0.0, 0.0, 1.0)
    main.call("_update_interaction_target")
    _check(main.get("nearest_interactable") != null, "player can approach Aramoor story hotspot")
    main.call("_interact")
    var dialogue: Label = hud.get("dialogue_label")
    _check(dialogue.visible and dialogue.text.find("Aramoor") >= 0, "interaction displays in 2D HUD over 3D game")
    main.call("_toggle_aramoor_tide")
    var tide_world: Node3D = main.get("active_world")
    _check(bool(tide_world.get("ghost_tide")), "Ghost Tide toggled through gameplay UI")
    _check(tide_world.call("get_interaction_points").size() == 9, "story markers persist after tide regen")
    main.call("_enter_backend")
    main.call("enterWorldMode")
    _check(str(main.get("active_world_id")) == "neonRiverwalk", "original First Night returns intact")
    _check(bool(player.get("world_active")), "player movement resumes in original world")
    main.free()
    if errors.is_empty():
        print("ARAMOOR_MAIN_WALKAROUND_SMOKE_GREEN")
        quit(0)
    else:
        print("ARAMOOR_MAIN_WALKAROUND_SMOKE_RED: " + ", ".join(errors))
        quit(1)

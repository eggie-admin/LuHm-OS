extends RefCounted
## One bounded game-side adapter: keeps Main.gd under its 350-line orchestration budget.
## Uses existing Godot player, HUD, quest and world factory. No new engine or transport.

func open_world(main: Node3D) -> void:
    var hud: Node = main.get("game_hud")
    var player: Node = main.get("player_controller")
    var android: Variant = main.get("android_web3_plugin")
    if android != null:
        android.hideCockpit()
    if not bool(main.call("switchWorld", "aramoorArchipelago")):
        hud.call("set_status", "ARAMOOR · WORLD SOURCE UNAVAILABLE")
        return
    hud.call("show_world")
    player.call("set_world_active", true)
    hud.call("set_aramoor_controls", true)
    hud.call("set_status", "ARAMOOR · PRIVATE SOURCE PREVIEW")
    hud.call("set_quest", "GHOST GIRLS OF ARAMOOR", "Walk the bridges and inspect ghost story beacons.", 1, 9)
    hud.call("show_dialogue", "Lum: Explore the islands, investigate beacons, and try Ghost Tide. Unapproved monster art is not included.")

func toggle_tide(main: Node3D) -> void:
    if str(main.get("active_world_id")) != "aramoorArchipelago":
        return
    var world: Node3D = main.get("active_world")
    if world == null:
        return
    main.set("nearest_interactable", null)
    var ghost := not bool(world.get("ghost_tide"))
    world.call("set_tide", ghost)
    var hud: Node = main.get("game_hud")
    hud.call("show_dialogue", "Ghost Tide. The coast remembers another time." if ghost else "Living Tide. The present returns.")
    hud.call("set_status", "ARAMOOR · GHOST TIDE" if ghost else "ARAMOOR · LIVING TIDE")
    main.call("_update_interaction_target")

func return_to_first_night(main: Node3D) -> void:
    main.call("switchWorld", "neonRiverwalk")
    var quest: Node = main.get("quest_director")
    var hud: Node = main.get("game_hud")
    var progress: Dictionary = quest.call("snapshot")
    var step: Dictionary = progress.get("currentStep", {})
    var count := int(main.get("encore_count"))
    var total := 5 if count == 0 else 4
    hud.call("set_quest", "FIRST NIGHT CIRCUIT" if count == 0 else "NIGHT SHIFT ENCORE", str(step.get("objective", "Continue the current quest.")), mini(int(progress.get("stepIndex", 0)) + 1, total), total)

func inspect(main: Node3D, event_name: String) -> bool:
    if str(main.get("active_world_id")) != "aramoorArchipelago" or not event_name.begins_with("aramoor:"):
        return false
    var zone_id := event_name.trim_prefix("aramoor:")
    var world: Node3D = main.get("active_world")
    var line := str(world.call("get_zone_line", zone_id))
    if line.is_empty():
        return true
    var hud: Node = main.get("game_hud")
    hud.call("show_dialogue", line)
    hud.call("set_status", "ARAMOOR · EXPLORE " + zone_id.to_upper())
    var player: Node = main.get("player_controller")
    if player.has_method("pulse_effect"):
        player.call("pulse_effect", Color("9adcf0"))
    return true

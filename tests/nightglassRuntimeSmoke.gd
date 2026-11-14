extends SceneTree
## Exact-engine, headless runtime smoke of Main → Nightglass → original Vesper dialogue.
## No external AI, network, assets or production grant.

func _initialize() -> void:
    call_deferred("_run")

func _check(condition: bool, reason: String) -> bool:
    if not condition:
        push_error("NIGHTGLASS_RUNTIME_RED: " + reason)
        quit(1)
        return false
    return true

func _run() -> void:
    var packed := load("res://scenes/Main.tscn") as PackedScene
    if not _check(packed != null, "Main scene absent"):
        return
    var firstNight := packed.instantiate()
    root.add_child(firstNight)
    current_scene = firstNight
    await process_frame
    await process_frame
    var hud = firstNight.get_node_or_null("GameHud")
    if not _check(hud != null, "first-night HUD missing"):
        return
    var entrance := hud.find_child("NightglassCreatorStudio", true, false) as Button
    if not _check(entrance != null and entrance.visible, "Nightglass main-menu entry missing"):
        return
    entrance.pressed.emit()
    await process_frame
    await process_frame
    var studio: Node = current_scene
    if not _check(studio != null and studio.name == "NightglassHub", "main-menu scene change failed"):
        return
    if not _check(studio.get("activeSceneId") == "nightglassBarHub", "bar did not load"):
        return
    var geometry := studio.get_node_or_null("ProceduralScene")
    if not _check(geometry != null, "procedural 3D stage missing"):
        return
    var npc := geometry.get_node_or_null("VesperNocturne")
    if not _check(npc != null and npc.get_node_or_null("AmethystHair") != null and npc.get_node_or_null("ChestMoonRune") != null, "original 3D Vesper proxy missing"):
        return
    if not _check(npc.get_node_or_null("VesperTalkTarget") is Area3D, "3D talk hitbox missing"):
        return
    var speaker := studio.get("speakerLabel") as Label
    var story := studio.get("storyLabel") as Label
    if not _check(speaker != null and speaker.text == "vesperNocturne", "Vesper opening speaker missing"):
        return
    if not _check(story != null and story.text.contains("visitor can cross the tide"), "Vesper dialogue did not render"):
        return
    var talkButton := studio.find_child("TalkToVesper", true, false) as Button
    if not _check(talkButton != null and talkButton.visible, "mobile talk button missing"):
        return
    var dialogueChoices := studio.get("choicesRoot") as VBoxContainer
    if not _check(dialogueChoices != null and dialogueChoices.get_child_count() >= 1, "branching dialogue missing"):
        return
    var firstChoice := dialogueChoices.get_child(0) as Button
    firstChoice.pressed.emit()
    if not _check(studio.get("currentLineId") == "lumWelcome", "dialogue choice did not advance"):
        return
    talkButton.pressed.emit()
    if not _check(studio.get("currentLineId") == "vesperEcho", "talk-to-Vesper did not restore dialogue"):
        return
    studio.call("_travel")
    if not _check(studio.get("activeSceneId") == "echoShore", "destination change failed"):
        return
    if not _check(not talkButton.visible and speaker.text == "maraIronvale", "shore palette/dialogue route failed"):
        return
    studio.call("_travel")
    if not _check(studio.get("activeSceneId") == "nightglassBarHub" and talkButton.visible, "return travel failed"):
        return
    var data = studio.get("manuscript")
    if not _check(data is Dictionary and data.get("assetPolicy", {}).get("thirdPartyDataAllowed") == false, "third-party art gate invalid"):
        return
    if not _check(data.get("orchestration", {}).get("liveWorkerState") == "QUARANTINED" and data.get("release", {}).get("cast") == "STOP", "source rights/release gate invalid"):
        return
    print("NIGHTGLASS_GODOT_SCENE_SMOKE_GREEN main_menu scene_change original_vesper dialogue_branch travel_return rights_hold")
    quit(0)

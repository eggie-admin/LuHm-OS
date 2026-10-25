extends SceneTree
## Headless native-TTS capability/consent contract. No speech is played in CI.
const DeviceVoiceScript := preload("res://scripts/game/witchingHourDeviceVoice.gd")
const DirectorScript := preload("res://scripts/game/witchingHourDirector.gd")
var errors: Array[String] = []

func _initialize() -> void:
    call_deferred("_run")

func _check(ok: bool, reason: String) -> void:
    if not ok:
        errors.append(reason)
        push_error("DEVICE_VOICE_RED_" + reason)

func _run() -> void:
    var director := DirectorScript.new()
    director.name = "StageDirector"
    root.add_child(director)
    var device := DeviceVoiceScript.new()
    device.name = "DeviceVoice"
    root.add_child(device)
    device.configure(director)
    await process_frame

    _check(not device.user_enabled, "noAutoOptIn")
    _check(not device.speak_on_user_action("lum", "Hello, Professor"), "noSpeechWithoutTap")
    _check(device.active_character.is_empty(), "noSpeechAfterDenied")
    device.set_user_enabled(false)
    _check(not device.speak_on_user_action("unknown", "No."), "unknownCharacterBlocked")
    _check(not device.speak_on_user_action("skuld", ""), "emptyTextBlocked")

    var bus_id := AudioServer.get_bus_index("PremonitionMusic")
    _check(bus_id >= 0, "musicBusExists")
    _check(director.set_json_tuning({"audio.musicVolume": 0.4}), "volumeTuning")
    director.set_external_speech_active(true)
    _check(AudioServer.get_bus_volume_db(bus_id) < linear_to_db(0.4), "nativeTtsDucksMusic")
    director.set_external_speech_active(false)
    _check(absf(AudioServer.get_bus_volume_db(bus_id) - linear_to_db(0.4)) < 0.01, "nativeTtsMusicRestore")

    var rehearsal := load("res://scenes/GoddessRehearsal.tscn") as PackedScene
    _check(rehearsal != null, "existingGoddessSceneLoads")
    if rehearsal != null:
        var game := rehearsal.instantiate()
        root.add_child(game)
        await process_frame
        var button := game.find_child("HearCharacterVoice", true, false) as Button
        _check(button != null, "tapToSpeakButton")
        _check(game.get_node_or_null("WitchingHourDeviceVoice") != null, "voiceAttachedToGame")
        game.queue_free()
        await process_frame
    device.queue_free()
    director.queue_free()
    if errors.is_empty():
        print("WITCHING_HOUR_DEVICE_TTS_CONSENT_GREEN_SOURCE_SCOPE")
        quit(0)
    else:
        push_error("WITCHING_HOUR_DEVICE_TTS_RED: " + ", ".join(errors))
        quit(1)

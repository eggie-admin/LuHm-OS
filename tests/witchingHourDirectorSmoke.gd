extends SceneTree
## Headless Godot 4 proof: orchestration contract only, never a voice provider receipt.
const DirectorScript := preload("res://scripts/game/witchingHourDirector.gd")
var failures: Array[String] = []
var seen: Array[String] = []

func _initialize() -> void:
    call_deferred("_run")

func _check(value: bool, name: String) -> void:
    if not value:
        failures.append(name)
        push_error("WITCHING_HOUR_RED_" + name)

func _turn(ref: String, speaker: String, turn_id: String, overlap: bool = false) -> Dictionary:
    return {"v": 1, "k": "speech", "i": turn_id, "r": ref, "s": speaker,
        "t": "Test caption " + turn_id, "o": "godot", "x": overlap}

func _run() -> void:
    var director := DirectorScript.new()
    director.name = "WitchingHourDirector"
    root.add_child(director)
    await process_frame
    director.caption_ready.connect(func(who: String, caption: String): seen.append(who + ":" + caption))
    for bus_name in ["PremonitionVoiceLead", "PremonitionVoiceGuest", "PremonitionMusic", "PremonitionEffects"]:
        _check(AudioServer.get_bus_index(bus_name) >= 0, "bus_" + bus_name)
    _check(director.has_node("LeadVoiceAudio") and director.has_node("GuestVoiceAudio"), "voicePlayers")
    _check(director.has_node("MusicAudio") and director.has_node("EffectsAudio"), "musicEffectsPlayers")
    var sha: String = "a".repeat(40)
    var first: Dictionary = _turn(sha, "lum", "intro")
    _check(not director.submit_turn(first), "unboundReject")
    _check(not director.bind_source("dev"), "badShaRejected")
    _check(director.bind_source(sha), "sourceBinding")
    _check(director.submit_turn(first), "leadAccepted")
    _check(director.active_turns.size() == 1, "oneLead")
    var guest: Dictionary = _turn(sha, "urd", "visitor", true)
    _check(director.submit_turn(guest), "guestOverlapApproved")
    _check(director.active_turns.size() == 2, "twoSpeakersMax")
    var queued: Dictionary = _turn(sha, "skuld", "next")
    _check(director.submit_turn(queued), "thirdTurnQueued")
    _check(director.queued_turns.size() == 1, "queueBounded")
    _check(not director.submit_turn(_turn("b".repeat(40), "belldandy", "wrongSha")), "wrongShaRejected")
    var injected: Dictionary = _turn(sha, "belldandy", "attack")
    injected["shell"] = "rm -rf /"
    _check(not director.submit_turn(injected), "shellPacketRejected")
    _check(not director.set_json_tuning({"audio.musicVolume": 2.0}), "badMusicVolumeRejected")
    _check(not director.set_json_tuning({"audio.voiceGain": true}), "booleanRejected")
    _check(not director.set_json_tuning({"releaseAuthority": 1}), "releaseTuningRejected")
    _check(director.set_json_tuning({"audio.voiceGain": 1.3, "audio.musicVolume": 0.4}), "typedSqlJsonTuneAccepted")
    _check(absf(director.music_volume - 0.4) < 0.00001, "musicTuned")
    var fake_stream := AudioStreamGenerator.new()
    _check(not director.play_approved_music(fake_stream, false), "noMusicAutoplay")
    _check(director.play_approved_music(fake_stream, true), "approvedMusicPlays")
    _check(director.play_voice("lum", fake_stream), "leadVoicePlays")
    var music_bus: int = AudioServer.get_bus_index("PremonitionMusic")
    var db_during: float = AudioServer.get_bus_volume_db(music_bus)
    _check(db_during < linear_to_db(0.4), "musicDuckedForVoice")
    director.end_turn("lum")
    director.end_turn("urd")
    _check(director.active_turns.has("skuld"), "queuedTurnResumes")
    _check(director.queued_turns.is_empty(), "queuedTurnDrained")
    director.end_turn("skuld")
    _check(director.active_turns.is_empty(), "turnFinished")
    _check(absf(AudioServer.get_bus_volume_db(music_bus) - linear_to_db(0.4)) < 0.01, "musicRestored")
    director.stop_music()
    _check(seen.size() >= 3, "captionsPropagated")
    _finish()

func _finish() -> void:
    if failures.is_empty():
        print("WITCHING_HOUR_GODOT_STAGE_DIRECTOR_GREEN_SOURCE_SCOPE")
        quit(0)
    else:
        push_error("WITCHING_HOUR_STAGE_RED: " + ", ".join(failures))
        quit(1)

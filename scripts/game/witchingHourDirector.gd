extends Node
## Witching Hour: Godot 4 owns stage/audio timing, NOT OS networking or AI inference.
## JSON packets are treated only as data. Remote bridge must authenticate first.

signal caption_ready(speaker_id: String, caption: String)
signal turn_started(speaker_id: String, turn_id: String)
signal turn_finished(speaker_id: String, turn_id: String)
signal turn_rejected(reason: String)

const SOURCE_CONTRACT := "res://doctrine/premonitionStageDirectorV1.json"
const AUDIO_CONTRACT := "res://doctrine/premonitionUniversalAudioV1.json"
const KNOWN_ORIGINS := ["chatGpt", "godot", "androidAssistant", "samsungBixby", "appleAppIntents", "androidEdgeGallery", "ollama"]
const KNOWN_ACTORS := ["lum", "urd", "belldandy", "skuld"]
const BUS_NAMES := ["PremonitionVoiceLead", "PremonitionVoiceGuest", "PremonitionMusic", "PremonitionEffects"]
const QUEUE_LIMIT := 12

var bound_source_ref := ""
var voice_gain := 1.0
var music_volume := 0.65
var duck_factor := 0.26
var active_turns: Dictionary = {}
var queued_turns: Array[Dictionary] = []

var lead_player: AudioStreamPlayer
var guest_player: AudioStreamPlayer
var music_player: AudioStreamPlayer
var effects_player: AudioStreamPlayer

func _ready() -> void:
    for bus_name in BUS_NAMES:
        _ensure_bus(bus_name)
    lead_player = _player("LeadVoiceAudio", BUS_NAMES[0])
    guest_player = _player("GuestVoiceAudio", BUS_NAMES[1])
    music_player = _player("MusicAudio", BUS_NAMES[2])
    effects_player = _player("EffectsAudio", BUS_NAMES[3])
    lead_player.finished.connect(_on_lead_finished)
    guest_player.finished.connect(_on_guest_finished)
    _update_mix()

func _ensure_bus(bus_name: String) -> void:
    var index := AudioServer.get_bus_index(bus_name)
    if index >= 0:
        return
    AudioServer.add_bus()
    index = AudioServer.bus_count - 1
    AudioServer.set_bus_name(index, bus_name)
    AudioServer.set_bus_send(index, "Master")

func _player(node_name: String, bus_name: String) -> AudioStreamPlayer:
    var player := AudioStreamPlayer.new()
    player.name = node_name
    player.bus = bus_name
    add_child(player)
    return player

func bind_source(source_sha: String) -> bool:
    if not _is_sha(source_sha):
        turn_rejected.emit("SOURCE_REF_REQUIRED")
        return false
    bound_source_ref = source_sha
    return true

func _is_sha(value: String) -> bool:
    if value.length() != 40:
        return false
    for ch in value:
        if not ch in "0123456789abcdef":
            return false
    return true

func _packet_ok(packet: Dictionary) -> bool:
    if bound_source_ref.is_empty():
        return false
    if packet.get("v") != 1 or packet.get("k") != "speech":
        return false
    if not packet.get("i") is String or str(packet["i"]).is_empty() or str(packet["i"]).length() > 96:
        return false
    if str(packet.get("r", "")) != bound_source_ref:
        return false
    if not packet.get("s") in KNOWN_ACTORS or not packet.get("o") in KNOWN_ORIGINS:
        return false
    if not packet.get("t") is String or str(packet["t"]).is_empty() or str(packet["t"]).length() > 4000:
        return false
    if packet.has("x") and not packet["x"] is bool:
        return false
    for key in packet.keys():
        if not str(key) in ["v", "k", "i", "r", "s", "t", "o", "x"]:
            return false
    return true

func submit_turn(packet: Dictionary) -> bool:
    if not _packet_ok(packet):
        turn_rejected.emit("INVALID_OR_UNBOUND_SPEECH_ENVELOPE")
        return false
    var speaker_id := str(packet["s"])
    var overlap: bool = bool(packet.get("x", false))
    if active_turns.has(speaker_id):
        turn_rejected.emit("SPEAKER_ALREADY_ACTIVE")
        return false
    var can_overlap := overlap and active_turns.size() == 1 and speaker_id != "lum"
    if can_overlap:
        can_overlap = active_turns.has("lum")
    if not active_turns.is_empty() and not can_overlap:
        if queued_turns.size() >= QUEUE_LIMIT:
            turn_rejected.emit("TURN_QUEUE_FULL")
            return false
        queued_turns.append(packet.duplicate(true))
        return true
    if active_turns.size() >= 2:
        turn_rejected.emit("VOICE_CAPACITY")
        return false
    _activate_turn(packet)
    return true

func _activate_turn(packet: Dictionary) -> void:
    var speaker_id := str(packet["s"])
    active_turns[speaker_id] = packet.duplicate(true)
    caption_ready.emit(speaker_id, str(packet["t"]))
    turn_started.emit(speaker_id, str(packet["i"]))

func end_turn(speaker_id: String) -> void:
    if not active_turns.has(speaker_id):
        return
    var packet: Dictionary = active_turns[speaker_id]
    active_turns.erase(speaker_id)
    if speaker_id == "lum" and lead_player != null:
        lead_player.stop()
    elif guest_player != null:
        guest_player.stop()
    turn_finished.emit(speaker_id, str(packet["i"]))
    _update_mix()
    _drain_queue()

func _drain_queue() -> void:
    if not active_turns.is_empty() or queued_turns.is_empty():
        return
    var next_turn: Dictionary = queued_turns.pop_front()
    _activate_turn(next_turn)

func show_local_caption(speaker_id: String, words: String) -> bool:
    # Local rehearsal dialogue is NOT a network or model-execution receipt.
    if not speaker_id in KNOWN_ACTORS or words.is_empty() or words.length() > 4000:
        return false
    caption_ready.emit(speaker_id, words)
    return true

func play_voice(speaker_id: String, approved_stream: AudioStream) -> bool:
    # Only an explicit playable stream provided by a trusted local bridge.
    # Never infer access to ChatGPT/Siri/Gemini audio.
    if approved_stream == null or not active_turns.has(speaker_id):
        return false
    var player := lead_player if speaker_id == "lum" else guest_player
    if player == null or player.playing:
        return false
    player.stream = approved_stream
    player.play()
    _update_mix()
    return true

func play_approved_music(approved_stream: AudioStream, user_initiated: bool) -> bool:
    if not user_initiated or approved_stream == null or music_player == null:
        return false
    music_player.stream = approved_stream
    music_player.play()
    _update_mix()
    return true

func stop_music() -> void:
    if music_player != null:
        music_player.stop()

func set_json_tuning(variables: Dictionary) -> bool:
    # Mirrors existing SQL/JSON allowed numeric paths, but never writes SQL.
    if variables.is_empty():
        return false
    for key in variables.keys():
        if not str(key) in ["audio.voiceGain", "audio.musicVolume"]:
            return false
        var value = variables[key]
        if value is bool or not (value is int or value is float):
            return false
        var numeric := float(value)
        if not is_finite(numeric):
            return false
        if key == "audio.voiceGain" and (numeric < 0.0 or numeric > 2.0):
            return false
        if key == "audio.musicVolume" and (numeric < 0.0 or numeric > 1.0):
            return false
    if variables.has("audio.voiceGain"):
        voice_gain = float(variables["audio.voiceGain"])
    if variables.has("audio.musicVolume"):
        music_volume = float(variables["audio.musicVolume"])
    _update_mix()
    return true

func _update_mix() -> void:
    if lead_player == null or guest_player == null or music_player == null:
        return
    var voice_live := lead_player.playing or guest_player.playing
    var factor := duck_factor if voice_live else 1.0
    AudioServer.set_bus_volume_db(AudioServer.get_bus_index(BUS_NAMES[0]), linear_to_db(maxf(voice_gain, 0.0001)))
    AudioServer.set_bus_volume_db(AudioServer.get_bus_index(BUS_NAMES[1]), linear_to_db(maxf(voice_gain, 0.0001)))
    AudioServer.set_bus_volume_db(AudioServer.get_bus_index(BUS_NAMES[2]), linear_to_db(maxf(music_volume * factor, 0.0001)))

func _on_lead_finished() -> void:
    end_turn("lum")

func _on_guest_finished() -> void:
    for key in active_turns.keys():
        if str(key) != "lum":
            end_turn(str(key))
            break

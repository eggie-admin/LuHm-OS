extends Node
## Consent-based OS text-to-speech for original adult character stage dialogue.
## Free native device feature when available. Not an AI provider and not a live ChatGPT voice bridge.

signal speech_started(character_id: String)
signal speech_finished(character_id: String)
signal speech_unavailable(reason: String)

const CHARACTER_IDS := ["lum", "urd", "belldandy", "skuld"]
const PITCH := {"lum": 1.02, "urd": 0.90, "belldandy": 0.98, "skuld": 1.08}
const RATE := {"lum": 1.0, "urd": 0.93, "belldandy": 0.96, "skuld": 1.07}

var stage_director: Node
var active_character := ""
var voice_by_character: Dictionary = {}
var user_enabled := false

func _ready() -> void:
    if not has_native_tts():
        return
    DisplayServer.tts_set_utterance_callback(DisplayServer.TTS_UTTERANCE_ENDED, _on_utterance_end)
    DisplayServer.tts_set_utterance_callback(DisplayServer.TTS_UTTERANCE_CANCELED, _on_utterance_cancel)

func configure(director: Node) -> void:
    stage_director = director

func has_native_tts() -> bool:
    return DisplayServer.has_feature(DisplayServer.FEATURE_TEXT_TO_SPEECH)

func available_english_voices() -> PackedStringArray:
    if not has_native_tts():
        return PackedStringArray()
    return DisplayServer.tts_get_voices_for_language("en")

func set_user_enabled(enabled: bool) -> void:
    user_enabled = enabled
    if not enabled:
        stop()

func speak_on_user_action(character_id: String, words: String) -> bool:
    if not user_enabled:
        speech_unavailable.emit("OPT_IN_REQUIRED")
        return false
    if not character_id in CHARACTER_IDS or words.is_empty() or words.length() > 4000:
        speech_unavailable.emit("INVALID_CHARACTER_OR_TEXT")
        return false
    if not has_native_tts():
        speech_unavailable.emit("DEVICE_TTS_UNAVAILABLE")
        return false
    var voices := available_english_voices()
    if voices.is_empty():
        speech_unavailable.emit("NO_ENGLISH_DEVICE_VOICE")
        return false
    stop()
    var character_index: int = CHARACTER_IDS.find(character_id)
    # Rotate through installed voices when possible, with graceful single-voice fallback.
    var voice_id: String = voices[character_index % voices.size()]
    active_character = character_id
    if stage_director != null and stage_director.has_method("set_external_speech_active"):
        stage_director.call("set_external_speech_active", true)
    speech_started.emit(character_id)
    DisplayServer.tts_speak(words, voice_id, 68, float(PITCH[character_id]), float(RATE[character_id]), 1, true)
    return true

func stop() -> void:
    if has_native_tts():
        DisplayServer.tts_stop()
    _finish_current()

func _on_utterance_end(_utterance_id: int) -> void:
    _finish_current()

func _on_utterance_cancel(_utterance_id: int) -> void:
    _finish_current()

func _finish_current() -> void:
    if active_character.is_empty():
        return
    var previous := active_character
    active_character = ""
    if stage_director != null and stage_director.has_method("set_external_speech_active"):
        stage_director.call("set_external_speech_active", false)
    speech_finished.emit(previous)

func _exit_tree() -> void:
    stop()

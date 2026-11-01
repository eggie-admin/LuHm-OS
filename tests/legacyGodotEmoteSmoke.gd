extends SceneTree

var failures: Array[String] = []

func _initialize() -> void:
    call_deferred("_run")

func check(condition: bool, label: String) -> void:
    if not condition:
        failures.append(label)
        push_error(label)

func _run() -> void:
    var packed := load("res://scenes/Main.tscn") as PackedScene
    check(packed != null, "real main scene loads")
    if packed == null:
        quit(1)
        return
    var game := packed.instantiate()
    root.add_child(game)
    await process_frame
    var hud: Node = game.get_node_or_null("GameHud")
    check(hud != null, "existing HUD is mounted")
    var bridge: Object = game.get("legacy_emote_bridge")
    check(bridge != null, "adapter is part of main scene")
    if bridge == null or hud == null:
        quit(1)
        return
    game.call("enterWorldMode")
    await process_frame
    var observed: Array[String] = []
    bridge.connect("emote_requested", func(value: String): observed.append(value))
    check(bool(game.call("previewLegacyEmote")), "synthetic preview stages in main scene")
    await process_frame
    var label: Label = hud.get("dialogue_label") as Label
    check(label != null and label.visible, "Godot dialogue HUD visible")
    if label != null:
        check(label.text.contains("AB\nC"), "hex text decoded into HUD")
        check(label.text.contains("[EMOTE: ANGRY]"), "emote shown on HUD")
    check(observed == ["angry"], "semantic event emitted exactly once")
    var bad: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://game/story/legacyIpsEmoteDemoV1.json"))
    bad["targetSha256"] = "0".repeat(64)
    var count_before := observed.size()
    check(not bool(bridge.call("stage_preview", bad, hud)), "changed digest refused")
    check(observed.size() == count_before, "bad receipt has no side effects")
    var bad_tokens: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://game/story/legacyIpsEmoteDemoV1.json"))
    bad_tokens["after"][0]["tokens"].insert(0, "<EXEC>")
    check(not bool(bridge.call("stage_preview", bad_tokens, hud)), "unknown token refused")
    check(observed.size() == count_before, "bad token has no side effects")
    game.queue_free()
    await process_frame
    if failures.is_empty():
        print("LUHM LEGACY IPS GODOT EVENT SOURCE SMOKE GREEN")
        quit(0)
    else:
        quit(1)

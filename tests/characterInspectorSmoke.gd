extends SceneTree

var failures := 0

func _initialize() -> void:
    run.call_deferred()

func check(value: bool, label: String) -> void:
    if not value:
        failures += 1
        push_error("INSPECTOR_FAIL " + label)
    else:
        print("INSPECTOR_PASS " + label)

func run() -> void:
    var scene = load("res://scenes/CharacterInspector.tscn").instantiate()
    root.add_child(scene)
    await process_frame
    var initial: Dictionary = scene.reviewReceipt()
    check(initial["assetState"] == "ORIGINAL_TECHNICAL_PROXY", "proxy identity explicit")
    check(initial["clipCount"] == 3, "three real diagnostic clips")
    check(initial["boneCount"] == 0, "no invented skeleton")
    scene.selectClip(0)
    scene.seekClip(0.5)
    check(absf(scene.reviewReceipt()["seconds"] - 0.5) < 0.001, "seek applies exact clip time")
    scene.stepFrame(1)
    check(absf(scene.reviewReceipt()["seconds"] - (0.5 + 1.0 / 30.0)) < 0.001, "frame step")
    scene.togglePlayback()
    var before: float = scene.clipTime
    scene._process(0.05)
    check(scene.clipTime > before, "playback advances")
    scene.cameraPreset("Side")
    check(absf(scene.yaw - PI / 2.0) < 0.001, "side camera")
    scene.setClay(true)
    check(scene.materialMeshes[0].material_override != null, "clay enabled")
    scene.setClay(false)
    check(scene.materialMeshes[0].material_override == null, "material restored")
    scene.selectCharacter(2)
    var missing: Dictionary = scene.reviewReceipt()
    check(missing["characterId"] == "urd", "Urd selection")
    check(missing["assetState"] == "BODY_UNASSIGNED", "missing body is honest")
    check(missing["meshCount"] == 0, "proxy geometry removed on missing body")
    check(missing["clipCount"] == 0 and scene.playButton.disabled, "unavailable clips disabled")
    scene.seekClip(1.0)
    scene.selectCharacter(0)
    scene.cameraPreset("Reset")
    check(scene.reviewReceipt()["clipCount"] == 3, "proxy recovers after empty selection")
    check(not scene.reviewReceipt()["canonApproved"] and not scene.reviewReceipt()["serverWrites"], "no approval or upload claim")
    scene.queue_free()
    await process_frame
    print("CHARACTER_INSPECTOR_SMOKE ", "PASS" if failures == 0 else "FAIL")
    quit(0 if failures == 0 else 1)

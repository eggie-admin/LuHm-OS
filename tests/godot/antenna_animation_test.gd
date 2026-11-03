extends SceneTree
## Synthetic animation-control proof only; no private model or game scene.
var failed: bool = false

func check(value: bool, label: String) -> void:
    if not value:
        failed = true
        push_error(label)

func _initialize() -> void:
    call_deferred("run")

func run() -> void:
    var script = load("res://scripts/avatar-glass.gd")
    var stage: Node3D = script.new()
    var mount := Node3D.new()
    mount.name = "AvatarMount"
    stage.add_child(mount)
    root.add_child(stage)
    await process_frame
    var avatar := Node3D.new()
    var player := AnimationPlayer.new()
    avatar.add_child(player)
    mount.add_child(avatar)
    stage.set("activeAvatar", avatar)
    var library := AnimationLibrary.new()
    var animation := Animation.new()
    animation.length = 1.0
    library.add_animation("dance", animation)
    player.add_animation_library("", library)
    var request := {"schema": "luhmOs.avatarAnimation.v1", "action": "play", "clip": "dance", "time": 0.0}
    check(stage.call("applyAnimationRequest", request), "play rejected")
    check(player.is_playing(), "player did not start")
    request.action = "pause"
    check(stage.call("applyAnimationRequest", request), "pause rejected")
    check(not player.is_playing(), "pause did not stop advancement")
    request.action = "seek"
    request.time = 2.0
    check(stage.call("applyAnimationRequest", request), "seek rejected")
    check(absf(player.current_animation_position - 1.0) < 0.001, "seek not clamped to clip")
    request.action = "shell"
    check(not stage.call("applyAnimationRequest", request), "unknown action accepted")
    request.action = "play"
    request.clip = "missing"
    check(not stage.call("applyAnimationRequest", request), "missing clip accepted")
    request.clip = "dance"
    request.time = -1.0
    check(not stage.call("applyAnimationRequest", request), "negative time accepted")
    stage.queue_free()
    await process_frame
    if not failed:
        print("ANTENNA_ANIMATION_CONTROL_PASS_SYNTHETIC_NO_MODEL_PROOF")
    quit(1 if failed else 0)

extends Node3D
## LuHm-OS: Project Premonition | avatar-only glass renderer.
## Attach Professor-approved Node3D character scenes; NEVER import world gameplay.
@export var avatarScene: PackedScene
@onready var avatarMount: Node3D = $AvatarMount

var activeAvatar: Node3D = null

func _ready() -> void:
    if avatarScene == null:
        return
    var instance: Node = avatarScene.instantiate()
    if instance is Node3D:
        activeAvatar = instance
        avatarMount.add_child(activeAvatar)
    else:
        instance.queue_free()

func setExpression(expressionId: String) -> bool:
    if expressionId not in ["neutral", "smile", "talk", "thinking"]:
        return false
    if activeAvatar == null or not activeAvatar.has_method("setExpression"):
        return false
    activeAvatar.call("setExpression", expressionId)
    return true

func setPose(poseId: String) -> bool:
    if poseId not in ["idle", "wave", "turnLeft", "turnRight"]:
        return false
    if activeAvatar == null or not activeAvatar.has_method("setPose"):
        return false
    activeAvatar.call("setPose", poseId)
    return true

func applyAnimationRequest(request: Dictionary) -> bool:
    # Shared luhmOs.avatarAnimation.v1 contract; imported clips only, no scripts/URLs.
    if request.size() != 4 or not request.has_all(["schema", "action", "clip", "time"]):
        return false
    if request.schema != "luhmOs.avatarAnimation.v1" or request.action not in ["play", "pause", "seek"]:
        return false
    if typeof(request.clip) != TYPE_STRING or request.clip.length() > 128:
        return false
    for index in request.clip.length():
        if request.clip.unicode_at(index) < 32:
            return false
    if typeof(request.time) not in [TYPE_INT, TYPE_FLOAT]:
        return false
    var time: float = float(request.time)
    if not is_finite(time) or time < 0.0 or time > 3600.0 or activeAvatar == null:
        return false
    var players: Array[Node] = activeAvatar.find_children("*", "AnimationPlayer", true, false)
    if players.is_empty():
        return false
    var player: AnimationPlayer = players[0] as AnimationPlayer
    if request.action == "play":
        if request.clip.is_empty() or not player.has_animation(request.clip):
            return false
        player.play(request.clip)
    elif request.action == "pause":
        player.pause()
    else:
        if player.assigned_animation.is_empty() or not player.has_animation(player.assigned_animation):
            return false
        var duration: float = player.get_animation(player.assigned_animation).length
        player.seek(clampf(time, 0.0, duration), true)
    return true

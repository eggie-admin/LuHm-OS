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

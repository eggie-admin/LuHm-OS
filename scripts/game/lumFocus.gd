extends RefCounted

const SAFE_SPRING_LENGTH := 4.0
const SAFE_VERTICAL_FOV := 48.0
const PLAYER_TO_LUM_Z := 1.35

# Presentation-only module. Preserve the existing rig, world and input controller.
# Keep the player proxy inside the kissaten, but place the actual camera outside the
# front plane so Samsung cannot begin inside set geometry.
static func apply(player: CharacterBody3D, lum: Node3D) -> void:
    player.position = Vector3(lum.position.x, 1.15, lum.position.z - PLAYER_TO_LUM_Z)
    player.set("spawn_point", player.position)
    var yaw := player.get_node("CameraYaw") as Node3D
    var spring := player.get_node("CameraYaw/CameraPitch/SpringArm3D") as SpringArm3D
    var camera := spring.get_node("Camera3D") as Camera3D
    yaw.position.y = 0.45
    spring.spring_length = SAFE_SPRING_LENGTH
    # Exclude the controller's own capsule, retaining world collision.
    spring.add_excluded_object(player.get_rid())
    camera.keep_aspect = Camera3D.KEEP_HEIGHT
    camera.fov = SAFE_VERTICAL_FOV
    player.call("set_camera_home", PI, -0.12, spring.spring_length)
    print("LUM_FOCUS_APPLIED vertical_fov=%.1f spring=%.2f" % [SAFE_VERTICAL_FOV, SAFE_SPRING_LENGTH])

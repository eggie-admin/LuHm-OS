extends RefCounted

# Presentation-only module. Preserve the existing rig, world and input controller.
static func apply(player: CharacterBody3D, lum: Node3D) -> void:
    player.position = Vector3(lum.position.x, 1.15, lum.position.z - 1.35)
    player.set("spawn_point", player.position)
    var yaw := player.get_node("CameraYaw") as Node3D
    var spring := player.get_node("CameraYaw/CameraPitch/SpringArm3D") as SpringArm3D
    var camera := spring.get_node("Camera3D") as Camera3D
    yaw.position.y = 0.45
    spring.spring_length = 1.60
    # Exclude the controller's own capsule, retaining world collision.
    spring.add_excluded_object(player.get_rid())
    camera.keep_aspect = Camera3D.KEEP_HEIGHT
    camera.fov = 50.0
    player.call("set_camera_home", PI, -0.20, spring.spring_length)
    print("LUM_FOCUS_APPLIED vertical_fov=50 distance=2.95")

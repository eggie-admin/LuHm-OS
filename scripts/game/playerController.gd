extends CharacterBody3D

const MOVE_SPEED := 5.8
const ACCELERATION := 18.0
const GRAVITY := 18.0
const RESPAWN_Y := -8.0

var touch_axis := Vector2.ZERO
var controls_locked := false
var world_active := false
var spawn_point := Vector3.ZERO

var camera_yaw: Node3D
var camera_pitch: Node3D
var spring_arm: SpringArm3D
var camera: Camera3D
var visual: Node3D

var _yaw := 0.0
var _pitch := -0.12
var _camera_home_yaw := 0.0
var _camera_home_pitch := -0.12
var _camera_home_length := 5.2
var _camera_tween: Tween

func _ready() -> void:
    spawn_point = position
    _build_body()
    _build_camera()

func _notification(what: int) -> void:
    if what == NOTIFICATION_APPLICATION_FOCUS_OUT or what == NOTIFICATION_APPLICATION_PAUSED:
        touch_axis = Vector2.ZERO
        velocity = Vector3.ZERO
        Input.mouse_mode = Input.MOUSE_MODE_VISIBLE

func _physics_process(delta: float) -> void:
    if not world_active:
        velocity = Vector3.ZERO
        return

    var axis := Vector2.ZERO if controls_locked else _read_move_axis()
    var basis := Basis(Vector3.UP, _yaw)
    var direction := basis * Vector3(axis.x, 0.0, axis.y)
    if direction.length_squared() > 0.0001:
        direction = direction.normalized()
        velocity.x = move_toward(velocity.x, direction.x * MOVE_SPEED, ACCELERATION * delta)
        velocity.z = move_toward(velocity.z, direction.z * MOVE_SPEED, ACCELERATION * delta)
        if visual != null:
            visual.rotation.y = lerp_angle(visual.rotation.y, atan2(-direction.x, -direction.z), minf(delta * 12.0, 1.0))
    else:
        velocity.x = move_toward(velocity.x, 0.0, ACCELERATION * delta)
        velocity.z = move_toward(velocity.z, 0.0, ACCELERATION * delta)

    if not is_on_floor():
        velocity.y -= GRAVITY * delta
    else:
        velocity.y = 0.0

    move_and_slide()
    if global_position.y < RESPAWN_Y:
        global_position = spawn_point
        velocity = Vector3.ZERO

func _unhandled_input(event: InputEvent) -> void:
    if not world_active or controls_locked:
        return
    if event is InputEventScreenDrag:
        var size := get_viewport().get_visible_rect().size
        if event.position.x > size.x * 0.36:
            orbit_by(event.relative * Vector2(0.0042, 0.0036))
    elif event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
        orbit_by(event.relative * Vector2(0.003, 0.003))
    elif event is InputEventMouseButton and event.pressed:
        Input.mouse_mode = Input.MOUSE_MODE_CAPTURED

func _build_body() -> void:
    var collision := CollisionShape3D.new()
    collision.name = "PlayerCollision"
    var capsule := CapsuleShape3D.new()
    capsule.radius = 0.42
    capsule.height = 1.8
    collision.shape = capsule
    add_child(collision)

    visual = Node3D.new()
    visual.name = "PlayerVisual"
    add_child(visual)

    var body := MeshInstance3D.new()
    var body_mesh := CapsuleMesh.new()
    body_mesh.radius = 0.28
    body_mesh.height = 1.35
    body.mesh = body_mesh
    body.position.y = 0.05
    var mat := StandardMaterial3D.new()
    mat.albedo_color = Color("17101f")
    mat.metallic = 0.28
    mat.roughness = 0.48
    body.material_override = mat
    body.visible = false # collision/camera proxy only; Lum is the visible character authority
    visual.add_child(body)

func _build_camera() -> void:
    camera_yaw = Node3D.new()
    camera_yaw.name = "CameraYaw"
    camera_yaw.position = Vector3(0.0, 1.35, 0.0)
    add_child(camera_yaw)

    camera_pitch = Node3D.new()
    camera_pitch.name = "CameraPitch"
    camera_yaw.add_child(camera_pitch)

    spring_arm = SpringArm3D.new()
    spring_arm.name = "SpringArm3D"
    spring_arm.spring_length = _camera_home_length
    spring_arm.collision_mask = 1
    spring_arm.margin = 0.2
    camera_pitch.add_child(spring_arm)

    camera = Camera3D.new()
    camera.name = "Camera3D"
    camera.current = true
    camera.fov = 68.0
    spring_arm.add_child(camera)
    _apply_orbit()

func _read_move_axis() -> Vector2:
    var keyboard := Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
    var axis := keyboard if keyboard.length() >= touch_axis.length() else touch_axis
    return axis.normalized() if axis.length() > 1.0 else axis

func orbit_by(delta: Vector2) -> void:
    _yaw -= delta.x
    _pitch = clampf(_pitch - delta.y, -0.62, 0.38)
    _apply_orbit()

func _apply_orbit() -> void:
    if camera_yaw != null:
        camera_yaw.rotation.y = _yaw
    if camera_pitch != null:
        camera_pitch.rotation.x = _pitch

func set_touch_axis(axis: Vector2) -> void:
    touch_axis = Vector2.ZERO if controls_locked else axis

func set_controls_locked(locked: bool) -> void:
    controls_locked = locked
    if locked:
        touch_axis = Vector2.ZERO
        velocity.x = 0.0
        velocity.z = 0.0

func set_world_active(active: bool) -> void:
    world_active = active
    if not active:
        touch_axis = Vector2.ZERO
        velocity = Vector3.ZERO

func focus_camera(target: Vector3, duration: float) -> void:
    _kill_camera_tween()
    _camera_home_yaw = _yaw
    _camera_home_pitch = _pitch
    _camera_home_length = spring_arm.spring_length

    var local_target := target - global_position
    var flat := Vector2(local_target.x, local_target.z)
    var target_yaw := atan2(-local_target.x, -local_target.z)
    var target_pitch := -atan2(local_target.y - 1.2, maxf(flat.length(), 0.001))
    target_pitch = clampf(target_pitch, -0.55, 0.28)

    _camera_tween = create_tween()
    _camera_tween.set_parallel(true)
    _camera_tween.set_trans(Tween.TRANS_SINE)
    _camera_tween.set_ease(Tween.EASE_IN_OUT)
    _camera_tween.tween_method(_set_yaw, _yaw, target_yaw, maxf(duration, 0.05))
    _camera_tween.tween_method(_set_pitch, _pitch, target_pitch, maxf(duration, 0.05))
    _camera_tween.tween_property(spring_arm, "spring_length", 3.2, maxf(duration, 0.05))

func restore_camera(duration: float) -> void:
    _kill_camera_tween()
    if duration <= 0.0:
        _set_yaw(_camera_home_yaw)
        _set_pitch(_camera_home_pitch)
        spring_arm.spring_length = _camera_home_length
        return
    _camera_tween = create_tween()
    _camera_tween.set_parallel(true)
    _camera_tween.set_trans(Tween.TRANS_SINE)
    _camera_tween.set_ease(Tween.EASE_IN_OUT)
    _camera_tween.tween_method(_set_yaw, _yaw, _camera_home_yaw, duration)
    _camera_tween.tween_method(_set_pitch, _pitch, _camera_home_pitch, duration)
    _camera_tween.tween_property(spring_arm, "spring_length", _camera_home_length, duration)

func _set_yaw(value: float) -> void:
    _yaw = value
    _apply_orbit()

func _set_pitch(value: float) -> void:
    _pitch = value
    _apply_orbit()

func _kill_camera_tween() -> void:
    if _camera_tween != null and _camera_tween.is_valid():
        _camera_tween.kill()
    _camera_tween = null

extends Node3D

@export var shot_id := "yumeCutsceneFactoryProof"
@export_enum("dayShift", "afterHours") var presentation_mode := "dayShift"
@export_range(0.5, 30.0, 0.1) var duration_seconds := 4.5

@onready var hero_proxy: MeshInstance3D = $HeroProxy
@onready var camera_rig: Node3D = $CameraRig
@onready var key_light: DirectionalLight3D = $KeyLight
@onready var world_environment: WorldEnvironment = $WorldEnvironment

var elapsed := 0.0

func _ready() -> void:
    var requested_mode := OS.get_environment("LUHM_PRESENTATION_MODE").strip_edges()
    if requested_mode in ["dayShift", "afterHours"]:
        presentation_mode = requested_mode
    _apply_presentation_mode()
    print("YUME_SHOT_READY id=%s mode=%s duration=%.2f" % [shot_id, presentation_mode, duration_seconds])

func _process(delta: float) -> void:
    elapsed += delta
    var t := clampf(elapsed / duration_seconds, 0.0, 1.0)
    var ease := t * t * (3.0 - 2.0 * t)
    hero_proxy.rotation.y = lerpf(-0.42, 0.30, ease)
    camera_rig.position.z = lerpf(0.15, -0.35, ease)
    if elapsed >= duration_seconds:
        print("YUME_SHOT_FINISHED id=%s mode=%s" % [shot_id, presentation_mode])
        get_tree().quit(0)

func _apply_presentation_mode() -> void:
    var environment := world_environment.environment
    if environment == null:
        return
    if presentation_mode == "afterHours":
        environment.background_color = Color(0.025, 0.008, 0.035, 1.0)
        environment.ambient_light_color = Color(0.25, 0.08, 0.28, 1.0)
        key_light.light_color = Color(1.0, 0.30, 0.58, 1.0)
        key_light.light_energy = 2.2
    else:
        environment.background_color = Color(0.025, 0.045, 0.070, 1.0)
        environment.ambient_light_color = Color(0.16, 0.28, 0.38, 1.0)
        key_light.light_color = Color(0.72, 0.90, 1.0, 1.0)
        key_light.light_energy = 1.8

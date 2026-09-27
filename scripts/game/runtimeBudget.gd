extends Node

signal quality_changed(previous: String, current: String, reason: String)

const SAMPLE_SECONDS := 1.0
const LOW_FPS_BALANCED := 50.0
const LOW_FPS_SAFE := 35.0
const RECOVER_FPS := 57.0
const LOW_SAMPLES_REQUIRED := 3
const RECOVER_SAMPLES_REQUIRED := 8

var _world: Node3D
var _viewport: Viewport
var _renderer := "UNKNOWN"
var _quality := "HIGH"
var _elapsed := 0.0
var _low_samples := 0
var _good_samples := 0
var _last_fps := 0.0
var _adaptive_enabled := false

func configure(world: Node3D, viewport: Viewport, renderer: String) -> void:
    _world = world
    _viewport = viewport
    _renderer = renderer
    _adaptive_enabled = OS.get_name() == "Android"
    if _adaptive_enabled:
        Engine.max_fps = 60
    _apply_quality("HIGH", "initial-profile")
    set_process(true)

func _process(delta: float) -> void:
    if not _adaptive_enabled:
        return
    _elapsed += delta
    if _elapsed < SAMPLE_SECONDS:
        return
    _elapsed = 0.0
    _last_fps = float(Engine.get_frames_per_second())

    if _last_fps < LOW_FPS_SAFE:
        _low_samples += 1
        _good_samples = 0
        if _low_samples >= LOW_SAMPLES_REQUIRED:
            _apply_quality("SAFE", "sustained-fps-below-35")
            _low_samples = 0
        return

    if _last_fps < LOW_FPS_BALANCED:
        _low_samples += 1
        _good_samples = 0
        if _low_samples >= LOW_SAMPLES_REQUIRED and _quality == "HIGH":
            _apply_quality("BALANCED", "sustained-fps-below-50")
            _low_samples = 0
        return

    _low_samples = 0
    if _last_fps >= RECOVER_FPS:
        _good_samples += 1
        if _good_samples >= RECOVER_SAMPLES_REQUIRED:
            if _quality == "SAFE":
                _apply_quality("BALANCED", "sustained-recovery")
            elif _quality == "BALANCED":
                _apply_quality("HIGH", "sustained-recovery")
            _good_samples = 0
    else:
        _good_samples = 0

func get_summary() -> Dictionary:
    return {
        "quality": _quality,
        "renderer": _renderer,
        "adaptive": _adaptive_enabled,
        "last_fps": _last_fps,
        "target_fps": 60,
        "sample_seconds": SAMPLE_SECONDS,
        "low_samples_required": LOW_SAMPLES_REQUIRED,
        "recover_samples_required": RECOVER_SAMPLES_REQUIRED,
    }

func _apply_quality(next_quality: String, reason: String) -> void:
    if _viewport == null:
        return
    var previous := _quality
    _quality = next_quality

    match next_quality:
        "SAFE":
            _set_if(_viewport, "msaa_3d", 0)
            _set_if(_viewport, "screen_space_aa", 1)
            _set_environment_glow(false)
            _set_directional_shadow_distance(24.0)
        "BALANCED":
            _set_if(_viewport, "msaa_3d", 1)
            _set_if(_viewport, "screen_space_aa", 1)
            _set_environment_glow(true)
            _set_directional_shadow_distance(36.0)
        _:
            _set_if(_viewport, "msaa_3d", 2 if _renderer != "gl_compatibility" else 1)
            _set_if(_viewport, "screen_space_aa", 1 if _renderer != "gl_compatibility" else 0)
            _set_environment_glow(true)
            _set_directional_shadow_distance(48.0)

    if previous != _quality:
        print("LUHM_RENDER_BUDGET quality=%s fps=%.1f reason=%s" % [_quality, _last_fps, reason])
        quality_changed.emit(previous, _quality, reason)

func _set_environment_glow(enabled: bool) -> void:
    if _world == null:
        return
    var env_node := _world.get_node_or_null("WorldEnvironment") as WorldEnvironment
    if env_node != null and env_node.environment != null:
        env_node.environment.glow_enabled = enabled

func _set_directional_shadow_distance(distance: float) -> void:
    if _world == null:
        return
    for node in _world.find_children("*", "DirectionalLight3D", true, false):
        var light := node as DirectionalLight3D
        if light != null and light.shadow_enabled:
            _set_if(light, "directional_shadow_max_distance", distance)

func _set_if(object: Object, property_name: String, value: Variant) -> void:
    if object == null:
        return
    for entry in object.get_property_list():
        if str(entry.get("name", "")) == property_name:
            object.set(property_name, value)
            return

extends Node

const PbrMaterialForge := preload("res://scripts/game/pbrMaterialForge.gd")
const SecondaryMotionRig := preload("res://scripts/game/secondaryMotionRig.gd")
const FacialRigDriver := preload("res://scripts/game/facialRigDriver.gd")
const PrivateModRegistry := preload("res://scripts/game/privateModRegistry.gd")
const RuntimeBudget := preload("res://scripts/game/runtimeBudget.gd")
const ASSET_REGISTRY_PATH := "res://assets/registry/BETA_ASSET_SOURCES_V1.json"
const PBR_SIDECAR_PATH := "res://assets/beta_external/pbr/materials.json"

var _summary: Dictionary = {}
var _runtime_budget: Node

func _ready() -> void:
    call_deferred("_boot_beta_engine")

func _boot_beta_engine() -> void:
    var runtime_root := get_parent()
    if runtime_root == null:
        push_warning("BetaEngineDirector: runtime root unavailable")
        return

    var world: Node3D
    for _frame in range(16):
        world = runtime_root.get_node_or_null("NeonWorld") as Node3D
        if world != null:
            break
        await get_tree().process_frame
    if world == null:
        push_warning("BetaEngineDirector: NeonWorld unavailable")
        return

    var renderer := RenderingServer.get_current_rendering_method()
    var driver := RenderingServer.get_current_rendering_driver_name()
    _configure_viewport(renderer)
    _configure_environment(world, renderer)
    _configure_lights(world, renderer)
    _install_runtime_budget(world, renderer)

    var lum := world.get_node_or_null("LumAvatarSocket") as Node3D
    var pbr_summary := PbrMaterialForge.apply_sidecar(lum, PBR_SIDECAR_PATH)
    var face_summary := FacialRigDriver.inspect(lum)
    var motion_summary := SecondaryMotionRig.install(lum)
    var mod_summary := PrivateModRegistry.inspect()

    _summary = {
        "renderer": renderer,
        "driver": driver,
        "asset_registry": ASSET_REGISTRY_PATH,
        "pbr": pbr_summary,
        "facial": face_summary,
        "secondary_motion": motion_summary,
        "private_mods": mod_summary,
        "runtime_budget": _runtime_budget.call("get_summary") if _runtime_budget != null else {"quality":"UNKNOWN"},
    }
    print("GODOT4_BETA_ENGINE=READY renderer=%s driver=%s pbr=%s face=%s motion=%s budget=%s" % [
        renderer,
        driver,
        str(pbr_summary.get("status", "unknown")),
        str(face_summary.get("status", "unknown")),
        str(motion_summary.get("status", "unknown")),
        str(_summary.get("runtime_budget", {}).get("quality", "UNKNOWN")),
    ])

func get_beta_summary() -> Dictionary:
    var current := _summary.duplicate(true)
    if _runtime_budget != null:
        current["runtime_budget"] = _runtime_budget.call("get_summary")
    return current

func _install_runtime_budget(world: Node3D, renderer: String) -> void:
    if _runtime_budget != null:
        return
    _runtime_budget = RuntimeBudget.new()
    _runtime_budget.name = "RuntimeBudget"
    add_child(_runtime_budget)
    _runtime_budget.call("configure", world, get_viewport(), renderer)

func _configure_viewport(renderer: String) -> void:
    var viewport := get_viewport()
    _set_if_property(viewport, "msaa_3d", 2 if renderer != "gl_compatibility" else 1)
    _set_if_property(viewport, "screen_space_aa", 1 if renderer != "gl_compatibility" else 0)
    _set_if_property(viewport, "use_debanding", renderer != "gl_compatibility")

func _configure_environment(world: Node3D, renderer: String) -> void:
    var env_node := world.get_node_or_null("WorldEnvironment") as WorldEnvironment
    if env_node == null or env_node.environment == null:
        return
    var env := env_node.environment
    env.tonemap_mode = Environment.TONE_MAPPER_ACES
    env.adjustment_enabled = true
    env.adjustment_brightness = 1.02
    env.adjustment_contrast = 1.08
    env.adjustment_saturation = 1.06
    env.glow_enabled = true
    _set_if_property(env, "glow_intensity", 0.85)
    _set_if_property(env, "glow_strength", 1.05)
    _set_if_property(env, "glow_bloom", 0.12)
    env.fog_enabled = true
    env.fog_density = minf(env.fog_density, 0.010)

    if renderer == "forward_plus":
        _set_if_property(env, "ssao_enabled", true)
        _set_if_property(env, "ssao_radius", 1.5)
        _set_if_property(env, "ssao_intensity", 1.15)
        _set_if_property(env, "ssil_enabled", true)
        _set_if_property(env, "ssr_enabled", true)
        _set_if_property(env, "volumetric_fog_enabled", true)
        _set_if_property(env, "volumetric_fog_density", 0.018)
    else:
        _set_if_property(env, "ssil_enabled", false)
        _set_if_property(env, "ssr_enabled", false)
        _set_if_property(env, "volumetric_fog_enabled", false)

func _configure_lights(world: Node3D, renderer: String) -> void:
    var first_directional := true
    for node in world.find_children("*", "DirectionalLight3D", true, false):
        var light := node as DirectionalLight3D
        if light == null:
            continue
        light.shadow_enabled = first_directional
        if first_directional:
            _set_if_property(light, "directional_shadow_max_distance", 48.0)
            _set_if_property(light, "shadow_bias", 0.035)
            _set_if_property(light, "shadow_normal_bias", 1.0)
            first_directional = false

    for node in world.find_children("*", "OmniLight3D", true, false):
        var omni := node as OmniLight3D
        if omni != null:
            omni.shadow_enabled = false

    var lum := world.get_node_or_null("LumAvatarSocket") as Node3D
    if lum == null:
        return

    if world.get_node_or_null("BetaLumHeroKey") == null:
        var key := SpotLight3D.new()
        key.name = "BetaLumHeroKey"
        key.position = lum.position + Vector3(-2.4, 3.5, -2.8)
        key.light_color = Color("ffd1b5")
        key.light_energy = 3.0 if renderer != "gl_compatibility" else 2.2
        key.spot_range = 9.0
        key.spot_angle = 42.0
        key.shadow_enabled = renderer == "forward_plus"
        world.add_child(key)
        key.look_at(lum.global_position + Vector3(0.0, 1.15, 0.0), Vector3.UP)

    if world.get_node_or_null("BetaLumFill") == null:
        var fill := OmniLight3D.new()
        fill.name = "BetaLumFill"
        fill.position = lum.position + Vector3(2.0, 2.0, -1.0)
        fill.light_color = Color("72c8ff")
        fill.light_energy = 1.4
        fill.omni_range = 6.5
        fill.shadow_enabled = false
        world.add_child(fill)

func _set_if_property(object: Object, property_name: String, value: Variant) -> void:
    if object == null:
        return
    for entry in object.get_property_list():
        if str(entry.get("name", "")) == property_name:
            object.set(property_name, value)
            return

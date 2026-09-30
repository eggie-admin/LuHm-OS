extends Node3D

# Final Cathedral install architecture:
# Godot owns the native renderer/world. The Android WebView is movable WebGlass UI,
# not a literal 3D stage. Headless/desktop keeps the native HUD as a deterministic fallback.
const NeonWorldScript := preload("res://scripts/game/neonWorld.gd")
const PlayerControllerScript := preload("res://scripts/game/playerController.gd")
const GameHudScript := preload("res://scripts/game/gameHud.gd")
const CutsceneDirectorScript := preload("res://scripts/cutsceneDirector.gd")
const CutsceneBridgeScript := preload("res://scripts/game/cutsceneBridge.gd")
const KaiWebViewBridgeScript := preload("res://scripts/platform/kaiWebViewBridge.gd")
const CharacterCreatorRuntimeScript := preload("res://scripts/game/characterCreatorRuntime.gd")
const INTRO_CUTSCENE_PATH := "res://cutscenes/lumBeaconIntro.json"

var neon_world: Node3D
var player_controller: CharacterBody3D
var game_hud: CanvasLayer
var cutscene_director: Node
var cutscene_bridge: Node
var kai_webview_bridge: Node
var character_creator: Node
var intro_played := false

func _ready() -> void:
    _build_runtime()
    _wire_runtime()
    enterWorldMode()
    if _webglass_available():
        game_hud.set_status("♛ CROWNED // GODOT WORLD + WEBGLASS")
        kai_webview_bridge.show_cockpit("compact")
    else:
        game_hud.set_status("CROWN · AMBER // NATIVE FALLBACK")

func _build_runtime() -> void:
    neon_world = NeonWorldScript.new()
    neon_world.name = "NeonWorld"
    add_child(neon_world)

    player_controller = PlayerControllerScript.new()
    player_controller.name = "PlayerController"
    player_controller.position = neon_world.player_spawn
    add_child(player_controller)

    game_hud = GameHudScript.new()
    game_hud.name = "GameHud"
    add_child(game_hud)

    cutscene_director = CutsceneDirectorScript.new()
    cutscene_director.name = "CutsceneDirector"
    add_child(cutscene_director)

    cutscene_bridge = CutsceneBridgeScript.new()
    cutscene_bridge.name = "CutsceneBridge"
    add_child(cutscene_bridge)
    cutscene_bridge.configure(cutscene_director, player_controller, neon_world, game_hud)

    kai_webview_bridge = KaiWebViewBridgeScript.new()
    kai_webview_bridge.name = "KaiWebViewBridge"
    add_child(kai_webview_bridge)

    character_creator = CharacterCreatorRuntimeScript.new()
    character_creator.name = "CharacterCreatorRuntime"
    add_child(character_creator)
    character_creator.configure(neon_world, kai_webview_bridge)

func _wire_runtime() -> void:
    game_hud.world_requested.connect(enterWorldMode)
    game_hud.backend_requested.connect(_enter_backend)
    game_hud.move_axis_changed.connect(player_controller.set_touch_axis)
    if kai_webview_bridge != null:
        kai_webview_bridge.world_requested.connect(enterWorldMode)
        kai_webview_bridge.toy_action_requested.connect(_on_toy_action)
        kai_webview_bridge.move_axis_changed.connect(player_controller.set_touch_axis)
        kai_webview_bridge.camera_delta_requested.connect(_on_web_camera_delta)
        kai_webview_bridge.quit_requested.connect(_on_quit_requested)

func _webglass_available() -> bool:
    return kai_webview_bridge != null and bool(kai_webview_bridge.call("is_available"))

func _hide_native_hud_for_webglass() -> void:
    if game_hud == null:
        return
    if game_hud.world_root != null:
        game_hud.world_root.visible = false
    if game_hud.backend_root != null:
        game_hud.backend_root.visible = false

func enterWorldMode() -> void:
    game_hud.show_world()
    player_controller.set_world_active(true)
    if _webglass_available():
        _hide_native_hud_for_webglass()
        kai_webview_bridge.show_cockpit("compact")
    if not intro_played:
        intro_played = true
        call_deferred("_play_intro")

func _enter_backend() -> void:
    if cutscene_bridge != null:
        cutscene_bridge.cancel()
        cutscene_bridge.restore_now()
    if player_controller != null:
        player_controller.set_world_active(false)
    if _webglass_available():
        # Android: Cathedral is HTML/CSS/jQuery/Vue glass over the still-rendered Godot world.
        _hide_native_hud_for_webglass()
        kai_webview_bridge.show_cockpit("fullscreen")
    elif game_hud != null:
        # CI/headless/desktop fallback preserves deterministic audit coverage.
        game_hud.show_backend()

func _on_web_camera_delta(delta: Vector2) -> void:
    if player_controller != null:
        player_controller.orbit_by(delta * Vector2(0.0038, 0.0034))

func _on_toy_action(action: String) -> void:
    match action:
        "pet_lum":
            if neon_world.has_method("pet_lum"):
                neon_world.pet_lum()
            game_hud.set_status("♥ LUM PET // HAPPY CORE PULSE")
        "oni_pop":
            if neon_world.has_method("oni_pop"):
                neon_world.oni_pop()
            game_hud.set_status("👹 ONI POP // HELPERS DEPLOYED")
        "crown_pulse":
            if neon_world.has_method("crown_pulse"):
                neon_world.crown_pulse()
            game_hud.set_status("♛ CROWN PULSE // PROFESSOR AUTHORITY")
        "chat_glass":
            _enter_backend()
        _:
            game_hud.set_status("KAI 9000 // UNKNOWN TOY ACTION BLOCKED")

func _on_quit_requested() -> void:
    get_tree().quit()

func _play_intro() -> void:
    await cutscene_bridge.play_path(INTRO_CUTSCENE_PATH)

extends Node3D

const NeonWorldScript := preload("res://scripts/game/neonWorld.gd")
const PlayerControllerScript := preload("res://scripts/game/playerController.gd")
const GameHudScript := preload("res://scripts/game/gameHud.gd")
const CutsceneDirectorScript := preload("res://scripts/cutsceneDirector.gd")
const CutsceneBridgeScript := preload("res://scripts/game/cutsceneBridge.gd")
const KaiWebViewBridgeScript := preload("res://scripts/platform/kaiWebViewBridge.gd")
const INTRO_CUTSCENE_PATH := "res://cutscenes/lumBeaconIntro.json"

var neon_world: Node3D
var player_controller: CharacterBody3D
var game_hud: CanvasLayer
var cutscene_director: Node
var cutscene_bridge: Node
var kai_webview_bridge: Node
var intro_played := false

func _ready() -> void:
    _build_runtime()
    _wire_runtime()
    _enter_world()
    game_hud.set_status("♛ CROWNED CATHEDRAL // KAI 9000 TOY MODE")

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

func _wire_runtime() -> void:
    game_hud.world_requested.connect(_enter_world)
    game_hud.backend_requested.connect(_enter_backend)
    game_hud.move_axis_changed.connect(player_controller.set_touch_axis)
    game_hud.toy_action_requested.connect(_on_toy_action)
    if kai_webview_bridge != null:
        kai_webview_bridge.world_requested.connect(_enter_world)
        kai_webview_bridge.toy_action_requested.connect(_on_toy_action)

func _enter_world() -> void:
    if kai_webview_bridge != null:
        kai_webview_bridge.hide_cockpit()
    game_hud.show_world()
    player_controller.set_world_active(true)
    if not intro_played:
        intro_played = true
        call_deferred("_play_intro")

func _enter_backend() -> void:
    if cutscene_bridge != null:
        cutscene_bridge.cancel()
        cutscene_bridge.restore_now()
    if player_controller != null:
        player_controller.set_world_active(false)
    if game_hud != null:
        game_hud.show_backend()
    if kai_webview_bridge != null:
        kai_webview_bridge.show_cockpit()

func _on_toy_action(action: String) -> void:
    match action:
        "pet_lum":
            neon_world.pet_lum()
            game_hud.set_status("♥ LUM PET // HAPPY CORE PULSE")
        "oni_pop":
            neon_world.oni_pop()
            game_hud.set_status("👹 ONI POP // THREE LITTLE HELPERS DEPLOYED")
        "crown_pulse":
            neon_world.crown_pulse()
            game_hud.set_status("♛ CROWN PULSE // PROFESSOR AUTHORITY CONFIRMED")
        "chat_glass":
            _enter_backend()
        _:
            game_hud.set_status("KAI 9000 // UNKNOWN TOY ACTION BLOCKED")

func _play_intro() -> void:
    await cutscene_bridge.play_path(INTRO_CUTSCENE_PATH)

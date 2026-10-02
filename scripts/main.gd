extends Node3D

const NeonWorldScript := preload("res://scripts/game/neonWorld.gd")
const PlayerControllerScript := preload("res://scripts/game/playerController.gd")
const GameHudScript := preload("res://scripts/game/gameHud.gd")
const CutsceneDirectorScript := preload("res://scripts/cutsceneDirector.gd")
const CutsceneBridgeScript := preload("res://scripts/game/cutsceneBridge.gd")
const INTRO_CUTSCENE_PATH := "res://cutscenes/lumBeaconIntro.json"

var neon_world: Node3D
var player_controller: CharacterBody3D
var game_hud: CanvasLayer
var cutscene_director: Node
var cutscene_bridge: Node
var intro_played := false
var android_web3_plugin = null
var android_web3_version := "unavailable"

func _ready() -> void:
    _build_runtime()
    _wire_runtime()
    _wire_android_web3()
    _enter_backend()

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

func _wire_runtime() -> void:
    game_hud.world_requested.connect(enterWorldMode)
    game_hud.backend_requested.connect(_enter_backend)
    game_hud.move_axis_changed.connect(player_controller.set_touch_axis)

func _wire_android_web3() -> void:
    if OS.get_name() != "Android":
        return
    if not Engine.has_singleton("AndroidWeb3Cockpit"):
        push_warning("AndroidWeb3Cockpit plugin is not staged in this build")
        return
    android_web3_plugin = Engine.get_singleton("AndroidWeb3Cockpit")
    android_web3_plugin.connect("world_requested", enterWorldMode)
    android_web3_plugin.connect("cockpit_ready", _on_android_web3_ready)
    android_web3_plugin.connect("bridge_error", _on_android_web3_error)

func _on_android_web3_ready(version: String) -> void:
    android_web3_version = version
    print("ANDROID_WEB3_COCKPIT_READY webview=", version)

func _on_android_web3_error(reason: String) -> void:
    push_error("ANDROID_WEB3_COCKPIT_ERROR: " + reason)

func enterWorldMode() -> void:
    if android_web3_plugin != null:
        android_web3_plugin.hideCockpit()
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
    if android_web3_plugin != null:
        android_web3_plugin.showCockpit()

func _play_intro() -> void:
    await cutscene_bridge.play_path(INTRO_CUTSCENE_PATH)

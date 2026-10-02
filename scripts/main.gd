extends Node3D
# Crown Cathedral Toy candidate 1.0.23 · exact-head CI stamp

const NeonWorldScript := preload("res://scripts/game/neonWorld.gd")
const PlayerControllerScript := preload("res://scripts/game/playerController.gd")
const GameHudScript := preload("res://scripts/game/gameHud.gd")
const CutsceneDirectorScript := preload("res://scripts/cutsceneDirector.gd")
const CutsceneBridgeScript := preload("res://scripts/game/cutsceneBridge.gd")
const PetWindowControllerScript := preload("res://scripts/game/petWindowController.gd")
const PetHudOverlayScript := preload("res://scripts/game/petHudOverlay.gd")
const INTRO_CUTSCENE_PATH := "res://cutscenes/lumBeaconIntro.json"

var neon_world: Node3D
var player_controller: CharacterBody3D
var game_hud: CanvasLayer
var cutscene_director: Node
var cutscene_bridge: Node
var pet_window_controller: Node
var pet_hud_overlay: CanvasLayer
var intro_played := false

func _ready() -> void:
    _build_runtime()
    _wire_runtime()
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

    pet_window_controller = PetWindowControllerScript.new()
    pet_window_controller.name = "PetWindowController"
    add_child(pet_window_controller)

    pet_hud_overlay = PetHudOverlayScript.new()
    pet_hud_overlay.name = "PetHudOverlay"
    add_child(pet_hud_overlay)
    pet_hud_overlay.configure(pet_window_controller)

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

func enterWorldMode() -> void:
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

func _play_intro() -> void:
    await cutscene_bridge.play_path(INTRO_CUTSCENE_PATH)

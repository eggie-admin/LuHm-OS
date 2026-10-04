extends Node3D

const WorldFactoryScript := preload("res://scripts/game/worldFactory.gd")
const PlayerControllerScript := preload("res://scripts/game/playerController.gd")
const GameHudScript := preload("res://scripts/game/gameHud.gd")
const CutsceneDirectorScript := preload("res://scripts/cutsceneDirector.gd")
const CutsceneBridgeScript := preload("res://scripts/game/cutsceneBridge.gd")
const CharacterRosterScript := preload("res://scripts/game/characterRoster.gd")
const QuestDirectorScript := preload("res://scripts/game/questDirector.gd")
const OniSummonBeaconScript := preload("res://scripts/game/oniSummonBeacon.gd")
const OniEchoCompanionScript := preload("res://scripts/game/oniEchoCompanion.gd")

const INTRO_CUTSCENE_PATH := "res://cutscenes/lumBeaconIntro.json"
const FIRST_NIGHT_QUEST_PATH := "res://game/story/firstNightQuest.json"
const INTERACTION_RANGE := 2.8

var neon_world: Node3D
var active_world: Node3D
var active_world_id := "neonRiverwalk"
var player_controller: CharacterBody3D
var game_hud: CanvasLayer
var cutscene_director: Node
var cutscene_bridge: Node
var character_roster: Node
var quest_director: Node
var nearest_interactable: Area3D
var intro_played := false
var android_web3_plugin = null
var android_web3_version := "unavailable"
var active_oni_beacon: Area3D
var active_oni_companion: Node3D

func _ready() -> void:
    _build_runtime()
    _wire_runtime()
    _wire_android_web3()
    _enter_backend()

func _process(_delta: float) -> void:
    _update_interaction_target()

func _unhandled_input(event: InputEvent) -> void:
    if event.is_action_pressed("ui_accept") and player_controller != null and player_controller.world_active:
        _interact()

func _build_runtime() -> void:
    neon_world = WorldFactoryScript.new().createWorld("neonRiverwalk")
    add_child(neon_world)
    active_world = neon_world

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
    cutscene_bridge.configure(cutscene_director, player_controller, active_world, game_hud)

    character_roster = CharacterRosterScript.new()
    character_roster.name = "CharacterRoster"
    add_child(character_roster)

    quest_director = QuestDirectorScript.new()
    quest_director.name = "QuestDirector"
    add_child(quest_director)


func _wire_runtime() -> void:
    game_hud.world_requested.connect(enterWorldMode)
    game_hud.backend_requested.connect(_enter_backend)
    game_hud.world_destination_requested.connect(switchWorld)
    game_hud.lum_talk_requested.connect(game_hud.show_dialogue.bind("Lum: Pick a door, Professor. Coffee is hot; architecture is questionable. ♡"))
    game_hud.interact_requested.connect(_interact)
    game_hud.move_axis_changed.connect(player_controller.set_touch_axis)

    quest_director.quest_changed.connect(_on_quest_changed)
    quest_director.quest_completed.connect(_on_quest_completed)
    game_hud.set_fast_travel_enabled(false)
    if not quest_director.load_quest(FIRST_NIGHT_QUEST_PATH):
        game_hud.set_status("QUEST SOURCE · UNAVAILABLE")

func _wire_android_web3() -> void:
    if OS.get_name() != "Android":
        return
    if not Engine.has_singleton("AndroidWeb3Cockpit"):
        push_warning("AndroidWeb3Cockpit plugin is not staged in this build")
        return
    android_web3_plugin = Engine.get_singleton("AndroidWeb3Cockpit")
    android_web3_plugin.connect("world_requested", enterWorldMode)
    android_web3_plugin.connect("oni_requested", _on_android_oni_requested)
    android_web3_plugin.connect("cockpit_ready", _on_android_web3_ready)
    android_web3_plugin.connect("bridge_error", _on_android_web3_error)

func _on_android_web3_ready(version: String) -> void:
    android_web3_version = version
    print("ANDROID_WEB3_COCKPIT_READY webview=", version)

func _on_android_oni_requested(name: String) -> void:
    print("ANDROID_WEB3_ONI_REQUESTED name=", name)
    if android_web3_plugin != null:
        android_web3_plugin.hideCockpit()
    if game_hud != null:
        game_hud.show_world()
        game_hud.show_oni_request(name)
    if player_controller != null:
        player_controller.set_world_active(true)
    _spawn_oni_beacon(name)
    _update_interaction_target()

func _spawn_oni_beacon(name: String) -> void:
    if active_world == null or player_controller == null:
        return
    if active_oni_beacon != null and is_instance_valid(active_oni_beacon):
        active_oni_beacon.queue_free()
    if active_oni_companion != null and is_instance_valid(active_oni_companion):
        active_oni_companion.queue_free()
        active_oni_companion = null
    var beacon = OniSummonBeaconScript.new()
    beacon.configure(name)
    active_world.add_child(beacon)
    beacon.global_position = player_controller.global_position + Vector3(1.4, 0.0, 0.0)
    active_oni_beacon = beacon

func _spawn_oni_companion(name: String) -> void:
    if active_world == null or player_controller == null:
        return
    if active_oni_companion != null and is_instance_valid(active_oni_companion):
        active_oni_companion.queue_free()
    var companion = OniEchoCompanionScript.new()
    companion.configure(name, player_controller)
    active_world.add_child(companion)
    companion.global_position = player_controller.global_position + Vector3(0.8, 1.3, 0.0)
    active_oni_companion = companion

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
    nearest_interactable = null
    if cutscene_bridge != null:
        cutscene_bridge.cancel()
        cutscene_bridge.restore_now()
    if player_controller != null:
        player_controller.set_world_active(false)
    if game_hud != null:
        game_hud.set_interaction_prompt("", false)
        game_hud.show_backend()
    if android_web3_plugin != null:
        android_web3_plugin.showCockpit()

func _play_intro() -> void:
    await cutscene_bridge.play_path(INTRO_CUTSCENE_PATH)

func switchWorld(world_id: String) -> bool:
    if world_id == active_world_id:
        return true

    var next_world: Node3D = WorldFactoryScript.new().createWorld(world_id)
    if next_world == null:
        return false

    nearest_interactable = null
    if cutscene_bridge != null:
        cutscene_bridge.cancel()
        cutscene_bridge.restore_now()
    if active_world != null:
        active_world.queue_free()

    add_child(next_world)
    active_world = next_world
    neon_world = next_world if world_id == "neonRiverwalk" else null
    active_world_id = world_id
    player_controller.global_position = active_world.player_spawn
    player_controller.spawn_point = active_world.player_spawn
    player_controller.velocity = Vector3.ZERO
    cutscene_bridge.world = active_world
    game_hud.set_interaction_prompt("", false)
    _update_interaction_target()
    return true

func _update_interaction_target() -> void:
    if game_hud == null or player_controller == null or active_world == null:
        return
    if not player_controller.world_active or quest_director == null or quest_director.is_complete():
        nearest_interactable = null
        game_hud.set_interaction_prompt("", false)
        _set_all_interaction_markers(false)
        return
    if not active_world.has_method("get_interaction_points"):
        nearest_interactable = null
        game_hud.set_interaction_prompt("", false)
        return

    var expected_event := quest_director.current_event()
    var closest: Area3D = null
    var closest_distance := INF
    var candidates: Array = []
    var raw_points = active_world.call("get_interaction_points")
    if raw_points is Array:
        candidates.append_array(raw_points)
    if active_oni_beacon != null and is_instance_valid(active_oni_beacon):
        candidates.append(active_oni_beacon)
    for raw_node in candidates:
        var node := raw_node as Area3D
        if node == null:
            continue
        var event_name := str(node.call("get_event_name")) if node.has_method("get_event_name") else ""
        var relevant := event_name == expected_event or event_name.begins_with("travel:") or event_name.begins_with("oni:")
        if node.has_method("set_active"):
            node.call("set_active", relevant)
        if not relevant:
            continue
        var distance := player_controller.global_position.distance_to(node.global_position)
        if distance < closest_distance:
            closest_distance = distance
            closest = node

    nearest_interactable = closest if closest_distance <= INTERACTION_RANGE else null
    if nearest_interactable != null and nearest_interactable.has_method("get_prompt"):
        game_hud.set_interaction_prompt(str(nearest_interactable.call("get_prompt")), true)
    else:
        game_hud.set_interaction_prompt("", false)

func _set_all_interaction_markers(active: bool) -> void:
    if active_world == null or not active_world.has_method("get_interaction_points"):
        return
    var raw_points = active_world.call("get_interaction_points")
    if raw_points is Array:
        for raw_node in raw_points:
            var node := raw_node as Area3D
            if node != null and node.has_method("set_active"):
                node.call("set_active", active)

func _interact() -> void:
    if nearest_interactable == null or quest_director == null:
        return
    var event_name := str(nearest_interactable.call("get_event_name"))
    if event_name.begins_with("travel:"):
        var destination := event_name.trim_prefix("travel:")
        if switchWorld(destination):
            game_hud.show_dialogue("Transit gate linked: %s" % destination)
        return
    if event_name.begins_with("oni:"):
        var oni_name := event_name.trim_prefix("oni:")
        if player_controller.has_method("pulse_effect"):
            player_controller.call("pulse_effect", Color("b783ff"))
        _spawn_oni_companion(oni_name)
        game_hud.show_dialogue("Lum: %s echo linked for eight seconds. Presence only; still no worker started." % oni_name)
        if nearest_interactable.has_method("dismiss"):
            nearest_interactable.call("dismiss")
        active_oni_beacon = null
        nearest_interactable = null
        game_hud.set_interaction_prompt("", false)
        return
    if event_name == "clearStaticWisp" and player_controller.has_method("pulse_effect"):
        player_controller.call("pulse_effect", Color("ff3c9d"))
    var result: Dictionary = quest_director.apply_event(event_name)
    var message := str(result.get("message", ""))
    if not message.is_empty():
        game_hud.show_dialogue(message)
    _update_interaction_target()

func _on_quest_changed(title: String, objective: String, current_step: int, total_steps: int) -> void:
    game_hud.set_quest(title, objective, current_step, total_steps)

func _on_quest_completed(_quest_id: String, message: String) -> void:
    game_hud.set_quest("First Night Complete", "Circuit closed. Fast travel unlocked.", 5, 5)
    game_hud.set_fast_travel_enabled(true)
    game_hud.set_interaction_prompt("", false)
    if not message.is_empty():
        game_hud.show_dialogue(message)

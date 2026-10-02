extends Node
class_name CockpitChatBridge

signal worldRequested(worldId: String)
signal questRequested(questId: String)

const ScriptedChatDirectorScript := preload("res://scripts/game/scriptedChatDirector.gd")
var hud: CanvasLayer
var scriptedChat: Node

func configure(gameHud: CanvasLayer) -> void:
    hud = gameHud
    scriptedChat = ScriptedChatDirectorScript.new()
    add_child(scriptedChat)

func submit(text: String, chaosSeed: String) -> void:
    var cleanText := text.strip_edges().substr(0, 512)
    if cleanText.is_empty() or hud == null or scriptedChat == null: return
    var reply: Dictionary = scriptedChat.submit(cleanText, chaosSeed)
    hud.show_dialogue(str(reply.get("text", "Lum: ...")))
    var action: Dictionary = reply.get("action", {})
    match str(action.get("type", "presentationOnly")):
        "worldRequest": worldRequested.emit(str(action.get("worldId", "")))
        "questRequest": questRequested.emit(str(action.get("questId", "")))
        _: pass

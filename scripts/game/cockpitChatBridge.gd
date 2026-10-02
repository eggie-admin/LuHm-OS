extends Node
class_name CockpitChatBridge

const ScriptedChatDirectorScript := preload("res://scripts/game/scriptedChatDirector.gd")
var hud: CanvasLayer
var scriptedChat: Node

func configure(gameHud: CanvasLayer) -> void:
    hud = gameHud
    scriptedChat = ScriptedChatDirectorScript.new()
    add_child(scriptedChat)

func submit(text: String, chaosSeed: String) -> void:
    var cleanText := text.strip_edges().substr(0, 512)
    if cleanText.is_empty() or hud == null or scriptedChat == null:
        return
    var reply: Dictionary = scriptedChat.submit(cleanText, chaosSeed)
    hud.show_dialogue(str(reply.get("text", "Lum: ...")))

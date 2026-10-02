extends Node
class_name CockpitChatBridge

var hud: CanvasLayer

func configure(gameHud: CanvasLayer) -> void:
    hud = gameHud

func submit(text: String, chaosSeed: String) -> void:
    var cleanText := text.strip_edges().substr(0, 512)
    if cleanText.is_empty() or hud == null:
        return
    print("LUHM_CHAT_SUBMITTED seed=", chaosSeed, " text=", cleanText)
    hud.show_dialogue("Lum: I heard you, Professor. " + cleanText)

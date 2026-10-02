extends Node
class_name ScriptedChatDirector

signal replyReady(speaker: String, text: String, mood: String, action: Dictionary)

const CAST := {
    "lum": {"name":"Lum","mood":"oniBoss"},
    "urd": {"name":"Urd","mood":"traceStorm"},
    "belldandy": {"name":"Belldandy","mood":"sanityBloom"},
    "skuld": {"name":"Skuld","mood":"buildGremlin"}
}

func submit(rawText: String, chaosSeed: String = "") -> Dictionary:
    var text := rawText.strip_edges().substr(0, 512)
    var lower := text.to_lower()
    var speaker := "lum"
    if "urd" in lower or "broke" in lower or "trace" in lower: speaker = "urd"
    elif "belldandy" in lower or "sanity" in lower or "doctrine" in lower: speaker = "belldandy"
    elif "skuld" in lower or "build" in lower or "fix" in lower: speaker = "skuld"
    var result := _scriptedReply(speaker, lower, chaosSeed)
    replyReady.emit(result.speaker, result.text, result.mood, result.action)
    return result

func _scriptedReply(speaker: String, text: String, chaosSeed: String) -> Dictionary:
    var name: String = CAST[speaker].name
    var mood: String = CAST[speaker].mood
    var line := ""
    var action: Dictionary = {"type":"presentationOnly","chaosSeed":chaosSeed}
    if "coffee" in text:
        line = "Coffee protocol engaged. Nobody touch the build until I find the good mug."
        action["event"] = "coffeeEmergency"
    elif "cat" in text:
        line = "Cat Hat Protocol accepted. This changes absolutely no source truth."
        action["event"] = "catHatProtocol"
    elif "what broke" in text or "broke" in text:
        line = "Trace says something broke. I can point at the smoke; deterministic evidence names the fire."
        action["event"] = "traceFlutter"
    elif "build" in text or "fix" in text:
        line = "Build lane armed. Scripted me gets the wrench; real mutations still answer to Professor Crown."
        action["event"] = "wrenchSpark"
    elif "doctrine" in text or "sanity" in text:
        line = "Doctrine check: fun may be chaotic; authority may not."
        action["event"] = "sanityBloom"
    else:
        line = "Cathedral link heard you. Pick a goddess, a world, coffee, cats, or trouble."
        action["event"] = "cathedralPing"
    return {"speaker":name,"text":name + ": " + line,"mood":mood,"action":action}

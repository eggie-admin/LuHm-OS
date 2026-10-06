extends Node
class_name ScriptedChatDirector

signal replyReady(speaker: String, text: String, mood: String, action: Dictionary)

const CAST := {
    "lum": {"name":"Lum","mood":"oniBoss"},
    "urd": {"name":"Urd","mood":"traceStorm"},
    "belldandy": {"name":"Belldandy","mood":"sanityBloom"},
    "skuld": {"name":"Skuld","mood":"buildGremlin"}
}
const WORLDS := {"riverwalk":"neonRiverwalk","cathedral":"cathedral","coffee":"lumCoffeeHouse"}

func submit(rawText: String, chaosSeed: String = "") -> Dictionary:
    var text := rawText.strip_edges().substr(0, 512)
    var lower := text.to_lower()
    var speaker := _speaker(lower)
    var result := _scriptedReply(speaker, lower, chaosSeed)
    replyReady.emit(result.speaker, result.text, result.mood, result.action)
    return result

func _speaker(text: String) -> String:
    if "urd" in text or "broke" in text or "trace" in text: return "urd"
    if "belldandy" in text or "sanity" in text or "doctrine" in text: return "belldandy"
    if "skuld" in text or "build" in text or "fix" in text: return "skuld"
    return "lum"

func _scriptedReply(speaker: String, text: String, chaosSeed: String) -> Dictionary:
    var name: String = CAST[speaker].name
    var mood: String = CAST[speaker].mood
    var line := ""
    var action: Dictionary = {"type":"presentationOnly","chaosSeed":chaosSeed}
    for token in WORLDS:
        if token in text:
            line = "Door selected: %s. Keep your hands inside the Cathedral at all times." % token
            action = {"type":"worldRequest","worldId":WORLDS[token],"chaosSeed":chaosSeed}
            return _result(name,mood,line,action)
    if "roll" in text or "dice" in text:
        var roll := _d20(chaosSeed + text)
        line = "The sacred plastic math rock says %d." % roll
        action["event"] = "diceBurst"; action["roll"] = roll
    elif "quest" in text:
        line = "Tiny quest: find the suspicious coffee cup before it becomes management."
        action = {"type":"questRequest","questId":"suspiciousCoffee","chaosSeed":chaosSeed}
    elif "coffee" in text:
        line = "Coffee protocol engaged. Nobody touch the build until I find the good mug."
        action["event"] = "coffeeEmergency"
    elif "cat" in text:
        line = "Cat Hat Protocol accepted. This changes absolutely no source truth."
        action["event"] = "catHatProtocol"
    elif "broke" in text:
        line = "Trace says something broke. I point at smoke; deterministic evidence names the fire."
        action["event"] = "traceFlutter"
    elif "build" in text or "fix" in text:
        line = "Build lane armed. Scripted me gets the wrench; real mutations answer to Professor Crown."
        action["event"] = "wrenchSpark"
    elif "doctrine" in text or "sanity" in text:
        line = "Doctrine check: fun may be chaotic; authority may not."
        action["event"] = "sanityBloom"
    else:
        line = "Cathedral link heard you. Try a goddess, a world, quest, dice, coffee, cats, or trouble."
        action["event"] = "cathedralPing"
    return _result(name,mood,line,action)

func _result(name: String, mood: String, line: String, action: Dictionary) -> Dictionary:
    return {"speaker":name,"text":name + ": " + line,"mood":mood,"action":action}

func _d20(seedText: String) -> int:
    var value := 2166136261
    for byte in seedText.to_utf8_buffer():
        value = int((value ^ byte) * 16777619) & 0x7fffffff
    return 1 + (value % 20)

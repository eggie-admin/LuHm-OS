extends RefCounted
# Finite, deterministic replay using existing reachable First Night interactions.
# This does not generate replacement character art, publish media or spawn agents.
const CANONICAL_QUEST_PATH := "res://game/story/firstNightQuest.json"
const MAX_NIGHTS := 3
const ENCORE_SEED := 20261101

func build_quest(night_index: int, seed_value: int = ENCORE_SEED) -> Dictionary:
    if night_index < 1 or night_index > MAX_NIGHTS:
        return {}
    if not FileAccess.file_exists(CANONICAL_QUEST_PATH):
        return {}
    var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(CANONICAL_QUEST_PATH))
    if not parsed is Dictionary:
        return {}
    var source_steps: Variant = parsed.get("steps", [])
    if not source_steps is Array or source_steps.size() != 5:
        return {}
    var known: Dictionary = {}
    for step in source_steps:
        if not step is Dictionary or not step.has("stepId"):
            return {}
        known[str(step["stepId"])] = step.duplicate(true)
    for required in ["meetLum", "recoverSignalShard", "coffeeRun", "clearStaticWisp", "cathedralSeal"]:
        if not known.has(required):
            return {}
    var choices: Array[String] = ["recoverSignalShard", "coffeeRun", "clearStaticWisp"]
    var rng := RandomNumberGenerator.new()
    rng.seed = seed_value + night_index * 4099
    for i in range(choices.size() - 1, 0, -1):
        var j := rng.randi_range(0, i)
        var old: String = choices[i]
        choices[i] = choices[j]
        choices[j] = old
    var steps: Array[Dictionary] = [
        known["meetLum"].duplicate(true),
        known[choices[0]].duplicate(true),
        known[choices[1]].duplicate(true),
        known["cathedralSeal"].duplicate(true)
    ]
    steps[0]["response"] = "Lum: Night Shift %d. Four beats, then we close the circuit. Follow me." % night_index
    steps[3]["response"] = "Night Shift %d sealed. Every circuit gets a real ending." % night_index
    return {
        "schema": "luhmOs.gameQuest.v1",
        "status": "proceduralPrivateDemo",
        "questId": "nightShiftEncore%d" % night_index,
        "title": "Night Shift %d / %d" % [night_index, MAX_NIGHTS],
        "seed": seed_value,
        "nightIndex": night_index,
        "rules": {
            "linear": true, "autosave": false,
            "externalNetwork": false, "publicationAuthority": false, "crownAuthority": false
        },
        "steps": steps,
        "completion": {
            "title": "Encore Complete",
            "message": "Lum: Night Shift %d complete. No endless errands, Professor." % night_index
        }
    }

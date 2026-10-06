extends Node
class_name AdventureDirector

signal adventure_started(adventureId: String)
signal quest_updated(questId: String, state: String)
signal dialogue_presented(prompt: String, choices: Array)
signal encounter_started(encounterId: String)
signal skill_resolved(skill: String, roll: int, target: int, success: bool)

var activeAdventure := ""
var questState: Dictionary = {}
var encounterState: Dictionary = {}
var chaosSeed := 1

func startAdventure(adventureId: String, seed: int = 1) -> void:
    activeAdventure = adventureId
    chaosSeed = maxi(seed, 1)
    questState.clear()
    encounterState.clear()
    adventure_started.emit(adventureId)

func setQuest(questId: String, state: String) -> void:
    questState[questId] = state
    quest_updated.emit(questId, state)

func presentChoice(prompt: String, choices: Array) -> Dictionary:
    var safeChoices := choices.duplicate()
    dialogue_presented.emit(prompt, safeChoices)
    return {"prompt": prompt, "choices": safeChoices}

func skillCheck(skill: String, modifier: int, target: int) -> Dictionary:
    var roll := _nextRoll() + modifier
    var success := roll >= target
    skill_resolved.emit(skill, roll, target, success)
    return {"skill": skill, "roll": roll, "target": target, "success": success}

func startEncounter(encounterId: String) -> void:
    encounterState = {"id": encounterId, "state": "active"}
    encounter_started.emit(encounterId)

func resolveEncounter(outcome: String) -> void:
    if encounterState.is_empty():
        return
    encounterState["state"] = "resolved"
    encounterState["outcome"] = outcome

func snapshot() -> Dictionary:
    return {"activeAdventure": activeAdventure,"questState": questState.duplicate(true),"encounterState": encounterState.duplicate(true),"chaosSeed": chaosSeed}

func _nextRoll() -> int:
    chaosSeed = int((1103515245 * chaosSeed + 12345) & 0x7fffffff)
    return 1 + (chaosSeed % 20)

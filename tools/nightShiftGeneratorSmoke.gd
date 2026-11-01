extends SceneTree

const Generator := preload("res://scripts/game/nightShiftGenerator.gd")
const Director := preload("res://scripts/game/questDirector.gd")

func _initialize() -> void:
    var generator = Generator.new()
    var base: Dictionary = generator.build_quest(1)
    if base.is_empty() or base != generator.build_quest(1):
        _fail("non deterministic first night")
        return
    if not generator.build_quest(0).is_empty() or not generator.build_quest(4).is_empty():
        _fail("generation exceeds finite limits")
        return
    var seen: Dictionary = {}
    for night in range(1, Generator.MAX_NIGHTS + 1):
        var quest: Dictionary = generator.build_quest(night)
        var steps: Array = quest.get("steps", [])
        if steps.size() != 4 or str(steps[0].get("event", "")) != "talkLumRiverwalk" or str(steps[3].get("event", "")) != "sealFirstNight":
            _fail("invalid four-step replay")
            return
        var director = Director.new()
        get_root().add_child(director)
        if not director.load_quest_data(quest):
            _fail("director rejected generated quest")
            return
        for step in steps:
            var event_name := str(step.get("event", ""))
            if not director.accepts_event(event_name):
                _fail("generated objective not accepted")
                return
            var result: Dictionary = director.apply_event(event_name)
            if not bool(result.get("accepted", false)):
                _fail("generated objective did not advance")
                return
        if not director.is_complete() or director.apply_event("talkLumRiverwalk").get("accepted", true):
            _fail("quest did not stop at completion")
            return
        seen[str(quest.get("questId", ""))] = true
        director.queue_free()
    if seen.size() != Generator.MAX_NIGHTS:
        _fail("missing unique night IDs")
        return
    print("NIGHT_SHIFT_GENERATOR_GREEN_SOURCE_SMOKE: 3 finite deterministic 4-step quests")
    quit(0)

func _fail(reason: String) -> void:
    push_error("NIGHT_SHIFT_GENERATOR_RED: " + reason)
    quit(1)

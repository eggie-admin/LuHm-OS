extends RefCounted
## Deterministic relationship state. Never accepts freeform model commands.
const RULES_PATH := "res://game/demo/relationshipRulesV2.json"
const EVENT_NAMES := ["talk", "help", "explore", "flirtElsewhere", "listen", "questComplete", "apologize"]
const STAT_NAMES := ["trust", "affection", "jealousy"]
var identity := ""
var display_name := ""
var lines: Dictionary = {}
var stats: Dictionary = {"trust":25,"affection":15,"jealousy":0}
var journal: Array = []
var _rules: Dictionary = {}

func configure(profile: Dictionary) -> bool:
    var loaded = JSON.parse_string(FileAccess.get_file_as_string(RULES_PATH))
    if not loaded is Dictionary or loaded.get("schema", "") != "luhmOs.relationshipRules.v2":
        return false
    _rules = loaded
    if profile.get("adult", false) != true:
        return false
    var key := str(profile.get("id", ""))
    var title := str(profile.get("displayName", ""))
    var dialogue = profile.get("dialogue", {})
    if key.is_empty() or not key.is_valid_identifier() or key.length() > 40 or title.is_empty() or title.length() > 60 or not dialogue is Dictionary:
        return false
    var events = _rules.get("events", {})
    if not events is Dictionary or events.size() != EVENT_NAMES.size():
        return false
    for event_id in EVENT_NAMES:
        if not events.has(event_id) or not dialogue.has(event_id) or not dialogue[event_id] is String or dialogue[event_id].is_empty() or dialogue[event_id].length() > 220:
            return false
        for stat in STAT_NAMES:
            if not events[event_id].has(stat) or not events[event_id][stat] is int:
                return false
    identity = key
    display_name = title
    lines = dialogue.duplicate(true)
    stats = _rules["initial"].duplicate(true)
    journal.clear()
    return true

func apply_event(event_id: String) -> Dictionary:
    if identity.is_empty() or not EVENT_NAMES.has(event_id) or not _rules["events"].has(event_id):
        return {"accepted":false,"reason":"eventNotAllowed"}
    var change: Dictionary = _rules["events"][event_id]
    for stat in STAT_NAMES:
        stats[stat] = clampi(int(stats[stat]) + int(change[stat]), 0, 100)
    journal.append(event_id)
    while journal.size() > 32:
        journal.pop_front()
    var state := snapshot()
    return {"accepted":true,"reaction":str(lines[event_id]),"stats":stats.duplicate(true),
        "bondTier":state["bondTier"],"rewards":state["rewards"],"authority":"localGodotOnly"}

func snapshot() -> Dictionary:
    var score := clampi((int(stats["trust"]) + int(stats["affection"]) - int(stats["jealousy"])) / 2, 0, 100)
    var tier := "newcomer"
    for row in _rules.get("tiers", []):
        if score >= int(row["minScore"]):
            tier = str(row["id"])
    var unlocks: Array = []
    for row in _rules.get("rewards", []):
        if score >= int(row["minScore"]):
            unlocks.append(str(row["id"]))
    return {"schema":"luhmOs.relationshipSnapshot.v2","id":identity,"stats":stats.duplicate(true),
        "bondScore":score,"bondTier":tier,"rewards":unlocks,"journal":journal.duplicate()}

func restore(snapshot_value: Dictionary) -> bool:
    if snapshot_value.get("schema", "") != "luhmOs.relationshipSnapshot.v2" or str(snapshot_value.get("id", "")) != identity:
        return false
    var new_stats = snapshot_value.get("stats", {})
    var saved_events = snapshot_value.get("journal", [])
    if not new_stats is Dictionary or not saved_events is Array or saved_events.size() > 32:
        return false
    for stat in STAT_NAMES:
        if not new_stats.has(stat) or not new_stats[stat] is int or new_stats[stat] < 0 or new_stats[stat] > 100:
            return false
    for event_id in saved_events:
        if not event_id is String or not EVENT_NAMES.has(event_id):
            return false
    stats = new_stats.duplicate(true)
    journal = saved_events.duplicate()
    return true

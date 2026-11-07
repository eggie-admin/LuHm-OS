extends RefCounted
const CHANGES := {
    "talk": {"trust": 1, "affection": 1, "jealousy": 0},
    "help": {"trust": 5, "affection": 2, "jealousy": -1},
    "explore": {"trust": 2, "affection": 1, "jealousy": 0},
    "flirtElsewhere": {"trust": 0, "affection": -1, "jealousy": 3}
}
var identity := ""
var display_name := ""
var lines: Dictionary = {}
var stats: Dictionary = {"trust": 25, "affection": 15, "jealousy": 0}
func configure(profile: Dictionary) -> bool:
    if profile.get("adult", false) != true:
        return false
    var key := str(profile.get("id", ""))
    var title := str(profile.get("displayName", ""))
    var dialogue = profile.get("dialogue", {})
    if key.is_empty() or not key.is_valid_identifier() or key.length() > 40 or title.is_empty() or title.length() > 60 or not dialogue is Dictionary:
        return false
    for event_id in CHANGES:
        if not dialogue.has(event_id) or not dialogue[event_id] is String or dialogue[event_id].is_empty() or dialogue[event_id].length() > 220:
            return false
    identity = key
    display_name = title
    lines = dialogue.duplicate(true)
    stats = {"trust": 25, "affection": 15, "jealousy": 0}
    return true
func apply_event(event_id: String) -> Dictionary:
    if identity.is_empty() or not CHANGES.has(event_id):
        return {"accepted": false}
    var change: Dictionary = CHANGES[event_id]
    for key in ["trust","affection","jealousy"]:
        stats[key] = clampi(int(stats[key]) + int(change[key]), 0, 100)
    return {"accepted": true, "reaction": str(lines[event_id]), "stats": stats.duplicate(true), "authority": "localGodotOnly"}

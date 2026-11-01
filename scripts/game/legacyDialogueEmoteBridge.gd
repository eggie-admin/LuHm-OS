extends RefCounted
## Synthetic IPS semantic text/emote adapter. No firmware or binary I/O.

signal emote_requested(emote_name: String)

const SOURCE_DIGEST := "5a72de5b146432410326710619c6e791f56cc694207ce0eabbc3fdf2309e6893"
const PATCH_DIGEST := "5c2459ad9c9a6abef129492191bc3522600fbebab37c4b30b5ea86a2f4a1887c"
const TARGET_DIGEST := "e6ab558e7a41ba12247d9702fc281cad1f7eb1107d44ce9f15b541905c37bb82"

func decode_tokens(tokens: Variant) -> Dictionary:
    if not (tokens is Array) or tokens.is_empty() or tokens.size() > 128:
        return {"ok": false}
    var value := ""
    var emote := ""
    var ended := false
    for index in range(tokens.size()):
        var token: Variant = tokens[index]
        if not (token is String):
            return {"ok": false}
        if token == "<END>":
            if index != tokens.size() - 1:
                return {"ok": false}
            ended = true
            break
        if token == "<EMOTE_HAPPY>" or token == "<EMOTE_ANGRY>":
            if not emote.is_empty():
                return {"ok": false}
            emote = "happy" if token == "<EMOTE_HAPPY>" else "angry"
        elif token == "<NEWLINE>":
            value += "\n"
        elif token == " " or (token.length() == 1 and "ABCDEFGHIJKLMNOPQRSTUVWXYZ".contains(token)):
            value += token
        else:
            return {"ok": false}
    if not ended or emote.is_empty() or value.length() > 2048:
        return {"ok": false}
    return {"ok": true, "text": value, "emote": emote}

func validate_receipt(receipt: Dictionary) -> bool:
    if receipt.get("schema") != "luhmOs.legacyIpsTextBridge.v1":
        return false
    if receipt.get("status") != "SYNTHETIC_SOURCE_ONLY" or receipt.get("crownStatus") != "STOP":
        return false
    if receipt.get("deviceFirmwareTouched") != false or receipt.get("publicRelease") != false:
        return false
    if receipt.get("sourceSha256") != SOURCE_DIGEST or receipt.get("patchSha256") != PATCH_DIGEST:
        return false
    if receipt.get("targetSha256") != TARGET_DIGEST or receipt.get("changedBytes") != 1:
        return false
    var before: Variant = receipt.get("before")
    var after: Variant = receipt.get("after")
    if not (before is Array) or not (after is Array):
        return false
    if before.size() != 2 or after.size() != 2:
        return false
    for i in range(2):
        if not (before[i] is Dictionary) or not (after[i] is Dictionary):
            return false
        var identity := "dialogue%d" % i
        var expected_offset := 16 if i == 0 else 24
        if before[i].get("dialogueId") != identity or after[i].get("dialogueId") != identity:
            return false
        if before[i].get("offset") != expected_offset or after[i].get("offset") != expected_offset:
            return false
        var p: Dictionary = decode_tokens(before[i].get("tokens"))
        var q: Dictionary = decode_tokens(after[i].get("tokens"))
        if not bool(p.get("ok", false)) or not bool(q.get("ok", false)):
            return false
    if before[1] != after[1]:
        return false
    var old: Dictionary = decode_tokens(before[0].get("tokens"))
    var changed: Dictionary = decode_tokens(after[0].get("tokens"))
    return old.get("emote") == "happy" and changed.get("emote") == "angry" and old.get("text") == changed.get("text")

func stage_preview(receipt: Dictionary, hud: CanvasLayer) -> bool:
    if not validate_receipt(receipt) or hud == null or not hud.has_method("show_dialogue"):
        return false
    var event: Dictionary = decode_tokens(receipt["after"][0]["tokens"])
    hud.call("show_dialogue", "%s\n[EMOTE: %s]" % [event["text"], str(event["emote"]).to_upper()])
    emote_requested.emit(str(event["emote"]))
    return true

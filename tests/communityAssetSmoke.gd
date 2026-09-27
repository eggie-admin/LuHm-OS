extends SceneTree

const MANIFEST_PATH := "res://assets/community/selected-assets.json"
const RUNTIME_ROOT := "res://assets/community/runtime"

func _initialize() -> void:
    call_deferred("_run")

func _run() -> void:
    if not FileAccess.file_exists(MANIFEST_PATH):
        push_error("COMMUNITY MANIFEST MISSING")
        quit(1)
        return

    var decoded = JSON.parse_string(FileAccess.get_file_as_string(MANIFEST_PATH))
    if not (decoded is Dictionary):
        push_error("COMMUNITY MANIFEST INVALID")
        quit(1)
        return

    var groups = decoded.get("groups", {})
    if not (groups is Dictionary):
        push_error("COMMUNITY MANIFEST GROUPS INVALID")
        quit(1)
        return

    var loaded := 0
    var expected := 0
    var seen: Dictionary = {}

    for group_name in groups:
        var names = groups[group_name]
        if not (names is Array):
            push_error("COMMUNITY GROUP INVALID: %s" % String(group_name))
            quit(1)
            return

        for raw_name in names:
            var asset_name := String(raw_name)
            var path := "%s/%s/%s" % [RUNTIME_ROOT, String(group_name), asset_name]
            expected += 1

            if seen.has(path):
                push_error("COMMUNITY ASSET DUPLICATE: %s" % path)
                quit(1)
                return
            seen[path] = true

            if not ResourceLoader.exists(path):
                push_error("COMMUNITY ASSET MISSING: %s" % path)
                quit(1)
                return

            var resource = load(path)
            if not (resource is PackedScene):
                push_error("COMMUNITY ASSET NOT PACKEDSCENE: %s" % path)
                quit(1)
                return

            var instance := (resource as PackedScene).instantiate()
            if instance == null:
                push_error("COMMUNITY ASSET INSTANTIATE FAILED: %s" % path)
                quit(1)
                return

            instance.free()
            loaded += 1

    if expected != 77:
        push_error("COMMUNITY ASSET COUNT DRIFT: expected doctrine 77 got %d" % expected)
        quit(1)
        return

    print("COMMUNITY_ASSET_SMOKE=PASS loaded=%d expected=%d" % [loaded, expected])
    quit(0)

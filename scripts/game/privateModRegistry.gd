extends RefCounted

const ROOT := "user://mods"
const MANIFEST := "user://mods/enabled.json"

static func inspect() -> Dictionary:
    var directory := DirAccess.open(ROOT)
    if directory == null:
        return {"status":"NO_MOD_DIRECTORY","root":ROOT,"packs":[]}
    var packs: Array[String] = []
    directory.list_dir_begin()
    while true:
        var name := directory.get_next()
        if name.is_empty():
            break
        if directory.current_is_dir():
            continue
        var lower := name.to_lower()
        if lower.ends_with(".zip") or lower.ends_with(".pck") or lower.ends_with(".glb") or lower.ends_with(".gltf"):
            packs.append(name)
    directory.list_dir_end()
    packs.sort()
    var enabled: Array = []
    if FileAccess.file_exists(MANIFEST):
        var parsed = JSON.parse_string(FileAccess.get_file_as_string(MANIFEST))
        if parsed is Dictionary and parsed.get("enabled", []) is Array:
            enabled = parsed.get("enabled", [])
    return {"status":"READY","root":ROOT,"packs":packs,"enabled":enabled,"auto_load":false,"runtime_network":false,"third_party_scripts":false}

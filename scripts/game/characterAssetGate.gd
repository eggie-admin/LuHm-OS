extends Node

const MANIFEST_PATH := "res://game/assets/CHARACTER_ASSET_INGEST_V1.json"

func validate_required_assets() -> Dictionary:
    var manifest := _load_json(MANIFEST_PATH)
    var missing: Array[String] = []
    var characters = manifest.get("characters", {})
    if characters is Dictionary:
        for character_id in characters:
            var spec = characters[character_id]
            if not spec is Dictionary:
                continue
            var root := String(spec.get("root", ""))
            for filename in spec.get("required", []):
                var path := root + String(filename)
                if not FileAccess.file_exists(path):
                    missing.append(path)
    return {"green": missing.is_empty(), "missing": missing, "manifestStatus": manifest.get("status", "UNKNOWN")}

func _load_json(path: String) -> Dictionary:
    if not FileAccess.file_exists(path):
        return {}
    var file := FileAccess.open(path, FileAccess.READ)
    if file == null:
        return {}
    var parsed = JSON.parse_string(file.get_as_text())
    return parsed if parsed is Dictionary else {}

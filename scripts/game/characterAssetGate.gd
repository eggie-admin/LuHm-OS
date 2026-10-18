extends Node

const MANIFEST_PATH := "res://game/assets/CHARACTER_ASSET_INGEST_V1.json"

func validate_required_assets() -> Dictionary:
    var manifest := _load_json(MANIFEST_PATH)
    var missing: Array[String] = []
    var errors: Array[String] = []
    var characters = manifest.get("characters", {})

    if manifest.is_empty():
        errors.append("manifestMissingOrInvalid")
    if not characters is Dictionary or characters.is_empty():
        errors.append("charactersMissingOrEmpty")
    else:
        for character_id in characters:
            var spec = characters[character_id]
            if not spec is Dictionary:
                errors.append("invalidCharacterSpec:" + String(character_id))
                continue
            var root := String(spec.get("root", ""))
            var required = spec.get("required", [])
            if not root.begins_with("res://game/assets/characters/"):
                errors.append("invalidCharacterRoot:" + String(character_id))
                continue
            if not required is Array or required.is_empty():
                errors.append("requiredAssetsMissing:" + String(character_id))
                continue
            for filename in required:
                var name := String(filename)
                if name.is_empty() or "/" in name or "\\" in name or name == "..":
                    errors.append("invalidAssetFilename:" + String(character_id))
                    continue
                var path := root + name
                if not FileAccess.file_exists(path):
                    missing.append(path)
    return {
        "green": errors.is_empty() and missing.is_empty(),
        "missing": missing,
        "errors": errors,
        "manifestStatus": manifest.get("status", "UNKNOWN")
    }

func _load_json(path: String) -> Dictionary:
    if not FileAccess.file_exists(path):
        return {}
    var file := FileAccess.open(path, FileAccess.READ)
    if file == null:
        return {}
    var parsed = JSON.parse_string(file.get_as_text())
    return parsed if parsed is Dictionary else {}

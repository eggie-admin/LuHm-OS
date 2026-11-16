extends SceneTree
## Read-only import smoke for an external, procedural Blender proof GLB.
## No private character asset is copied into res:// or an export package.

const EXPECTED_SCHEMA := "luhm-os.blender-godot-handoff.v1"
const EXPECTED_FILE := "proof-marker.glb"

func _initialize() -> void:
    var receipt_path: String = OS.get_environment("LUHM_HANDOFF_MANIFEST")
    if receipt_path.is_empty() or not receipt_path.is_absolute_path():
        _red("RED_HANDOFF_MANIFEST_ABSOLUTE_PATH_REQUIRED")
        return
    if not FileAccess.file_exists(receipt_path):
        _red("RED_HANDOFF_MANIFEST_NOT_FOUND")
        return

    var parsed = JSON.parse_string(FileAccess.get_file_as_string(receipt_path))
    if not parsed is Dictionary:
        _red("RED_HANDOFF_MANIFEST_NOT_JSON_OBJECT")
        return
    var manifest: Dictionary = parsed
    if manifest.get("schema", "") != EXPECTED_SCHEMA:
        _red("RED_HANDOFF_SCHEMA_MISMATCH")
        return
    if manifest.get("status", "") != "LOCAL_EXPERIMENT_NOT_CROWN":
        _red("RED_HANDOFF_STATUS_MISMATCH")
        return
    if manifest.get("origin", "") != "new-procedural-marker-only":
        _red("RED_HANDOFF_ORIGIN_MISMATCH")
        return
    if manifest.get("privateArtworkIncluded", true) != false:
        _red("RED_HANDOFF_PRIVATE_ARTWORK_FLAG")
        return
    if manifest.get("assetFile", "") != EXPECTED_FILE:
        _red("RED_HANDOFF_UNEXPECTED_FILENAME")
        return

    var glb_path: String = receipt_path.get_base_dir().path_join(EXPECTED_FILE)
    if not FileAccess.file_exists(glb_path):
        _red("RED_HANDOFF_GLB_MISSING")
        return
    if FileAccess.get_size(glb_path) <= 0 or FileAccess.get_size(glb_path) != int(manifest.get("byteSize", -1)):
        _red("RED_HANDOFF_SIZE_MISMATCH")
        return
    if FileAccess.get_sha256(glb_path) != String(manifest.get("sha256", "")):
        _red("RED_HANDOFF_SHA256_MISMATCH")
        return

    var document := GLTFDocument.new()
    var state := GLTFState.new()
    var import_result: int = document.append_from_file(glb_path, state)
    if import_result != OK:
        _red("RED_HANDOFF_GLTF_IMPORT_FAILED_" + str(import_result))
        return
    var scene := document.generate_scene(state)
    if scene == null:
        _red("RED_HANDOFF_SCENE_NOT_GENERATED")
        return
    var mesh_count: int = _count_meshes(scene)
    scene.free()
    if mesh_count != 2:
        _red("RED_HANDOFF_EXPECTED_TWO_PROCEDURAL_MESHES_" + str(mesh_count))
        return
    print("GREEN_GODOT_PROCEDURAL_GLB_IMPORT_MESHES_2")
    print("UNVERIFIED: interactive viewport, Samsung touch, full character rigs, Crown")
    quit(0)


func _count_meshes(node: Node) -> int:
    var count: int = 1 if node is MeshInstance3D else 0
    for child in node.get_children():
        count += _count_meshes(child)
    return count


func _red(message: String) -> void:
    push_error(message)
    quit(1)

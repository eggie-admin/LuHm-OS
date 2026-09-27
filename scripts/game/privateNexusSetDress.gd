extends Node3D

# Optional local/private Nexus sidecar.
# The public GitHub/CI candidate never downloads Nexus payloads and never requires
# them. Only already-authorized locally staged GLB files may be instantiated.

const RECEIPT_PATH := "res://assets/nexus/runtime/PROVENANCE.json"
const RUNTIME_PREFIX := "res://assets/nexus/runtime/"
const MAX_PRIVATE_ASSETS := 32

var loaded_count := 0
var blocked_count := 0

func _ready() -> void:
    name = "PrivateNexusSetDress"
    if not FileAccess.file_exists(RECEIPT_PATH):
        return
    var decoded = JSON.parse_string(FileAccess.get_file_as_string(RECEIPT_PATH))
    if not decoded is Dictionary:
        push_warning("Nexus provenance receipt malformed; private sidecar disabled")
        return
    var receipt: Dictionary = decoded
    var assets = receipt.get("assets", [])
    if not assets is Array:
        return
    var count := 0
    for raw in assets:
        if count >= MAX_PRIVATE_ASSETS:
            break
        if raw is Dictionary and _place(raw):
            count += 1

func _place(spec: Dictionary) -> bool:
    var rights := str(spec.get("rights_mode", ""))
    if rights not in ["PRIVATE_PERSONAL_REFERENCE", "REDISTRIBUTABLE_WITH_EVIDENCE"]:
        blocked_count += 1
        return false
    var path := str(spec.get("runtime_path", ""))
    if not path.begins_with(RUNTIME_PREFIX) or not path.ends_with(".glb"):
        blocked_count += 1
        return false
    if not ResourceLoader.exists(path):
        blocked_count += 1
        return false
    var packed := load(path)
    if not packed is PackedScene:
        blocked_count += 1
        return false
    var instance := (packed as PackedScene).instantiate()
    if not instance is Node3D:
        instance.queue_free()
        blocked_count += 1
        return false

    var node := instance as Node3D
    node.name = "NexusPrivate_%02d_%s" % [loaded_count, path.get_file().get_basename()]
    var placement = spec.get("placement", {})
    if placement is Dictionary:
        var p: Dictionary = placement
        node.position = Vector3(float(p.get("x", 0.0)), float(p.get("y", 0.0)), float(p.get("z", 14.0)))
        node.rotation_degrees.y = float(p.get("yaw", 0.0))
        var s := clampf(float(p.get("scale", 1.0)), 0.05, 20.0)
        node.scale = Vector3.ONE * s
    add_child(node)
    loaded_count += 1
    return true

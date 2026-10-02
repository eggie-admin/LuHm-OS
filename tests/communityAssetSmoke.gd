extends SceneTree

const REQUIRED := [
    "res://assets/community/runtime/city-industrial/building-a.glb",
    "res://assets/community/runtime/city-industrial/chimney-large.glb",
    "res://assets/community/runtime/city-industrial/detail-tank.glb",
    "res://assets/community/runtime/factory/catwalk-straight.glb",
    "res://assets/community/runtime/factory/crane.glb",
    "res://assets/community/runtime/factory/pipe-large-valve.glb",
    "res://assets/community/runtime/factory/robot-arm-a.glb",
    "res://assets/community/runtime/furniture/kitchenBar.glb",
    "res://assets/community/runtime/furniture/stoolBar.glb",
    "res://assets/community/runtime/furniture/loungeSofaLong.glb",
    "res://assets/community/runtime/furniture/radio.glb",
    "res://assets/community/runtime/furniture/televisionVintage.glb"
]

func _initialize() -> void:
    call_deferred("_run")

func _run() -> void:
    var loaded := 0
    for path in REQUIRED:
        if not ResourceLoader.exists(path):
            push_error("COMMUNITY ASSET MISSING: %s" % path)
            quit(1)
            return
        var resource = load(path)
        if not resource is PackedScene:
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
    print("COMMUNITY_ASSET_SMOKE=PASS loaded=%d" % loaded)
    quit(0)

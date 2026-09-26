extends Node3D

# Build-time staged CC0 props. No runtime network access.
# Missing assets fail soft for ordinary source checkouts; CI and APK smoke require them.
var loaded_count := 0
var missing_count := 0

const PLACEMENTS := [
    # Detroit industrial skyline / river machinery
    {"path":"res://assets/community/runtime/city-industrial/building-a.glb", "pos":Vector3(-19.0,0.0,-4.0), "rot":18.0, "scale":3.0},
    {"path":"res://assets/community/runtime/city-industrial/building-c.glb", "pos":Vector3(20.0,0.0,-11.0), "rot":-20.0, "scale":3.2},
    {"path":"res://assets/community/runtime/city-industrial/building-e.glb", "pos":Vector3(-21.0,0.0,13.0), "rot":30.0, "scale":2.8},
    {"path":"res://assets/community/runtime/city-industrial/chimney-large.glb", "pos":Vector3(-17.0,0.0,-20.0), "rot":0.0, "scale":3.2},
    {"path":"res://assets/community/runtime/city-industrial/chimney-medium.glb", "pos":Vector3(18.0,0.0,-22.0), "rot":0.0, "scale":3.0},
    {"path":"res://assets/community/runtime/city-industrial/detail-tank.glb", "pos":Vector3(15.5,0.0,-14.0), "rot":14.0, "scale":2.2},
    {"path":"res://assets/community/runtime/city-industrial/building-h.glb", "pos":Vector3(-15.5,0.0,-13.0), "rot":-12.0, "scale":2.4},

    # Factory machinery framing the walk
    {"path":"res://assets/community/runtime/factory/catwalk-straight.glb", "pos":Vector3(-8.5,1.0,-1.0), "rot":90.0, "scale":1.7},
    {"path":"res://assets/community/runtime/factory/catwalk-stairs.glb", "pos":Vector3(-10.0,0.0,3.5), "rot":90.0, "scale":1.6},
    {"path":"res://assets/community/runtime/factory/conveyor-long.glb", "pos":Vector3(8.5,0.0,8.0), "rot":-90.0, "scale":1.4},
    {"path":"res://assets/community/runtime/factory/crane.glb", "pos":Vector3(10.2,0.0,-5.0), "rot":-30.0, "scale":1.5},
    {"path":"res://assets/community/runtime/factory/crane-magnet.glb", "pos":Vector3(7.5,0.0,-7.0), "rot":0.0, "scale":1.4},
    {"path":"res://assets/community/runtime/factory/machine.glb", "pos":Vector3(-8.0,0.0,12.0), "rot":20.0, "scale":1.4},
    {"path":"res://assets/community/runtime/factory/machine-bed.glb", "pos":Vector3(-9.5,0.0,9.0), "rot":-15.0, "scale":1.3},
    {"path":"res://assets/community/runtime/factory/machine-connection-pipe.glb", "pos":Vector3(-7.0,0.0,6.5), "rot":90.0, "scale":1.5},
    {"path":"res://assets/community/runtime/factory/pipe-large-long.glb", "pos":Vector3(11.0,2.1,2.0), "rot":90.0, "scale":1.8},
    {"path":"res://assets/community/runtime/factory/pipe-large-bend.glb", "pos":Vector3(11.0,2.1,-2.0), "rot":90.0, "scale":1.8},
    {"path":"res://assets/community/runtime/factory/pipe-large-valve.glb", "pos":Vector3(11.0,1.7,-5.0), "rot":90.0, "scale":1.8},
    {"path":"res://assets/community/runtime/factory/robot-arm-a.glb", "pos":Vector3(-6.5,0.0,-10.0), "rot":40.0, "scale":1.5},
    {"path":"res://assets/community/runtime/factory/screen-wide.glb", "pos":Vector3(5.8,1.0,-7.0), "rot":-25.0, "scale":1.5},
    {"path":"res://assets/community/runtime/factory/warning-traffic.glb", "pos":Vector3(3.8,0.0,3.0), "rot":0.0, "scale":1.5},

    # Demon-bar / lounge setpiece around the Cathedral side of the riverwalk
    {"path":"res://assets/community/runtime/furniture/rugRectangle.glb", "pos":Vector3(0.0,0.02,12.0), "rot":0.0, "scale":2.0},
    {"path":"res://assets/community/runtime/furniture/kitchenBar.glb", "pos":Vector3(0.0,0.0,15.0), "rot":180.0, "scale":1.7},
    {"path":"res://assets/community/runtime/furniture/kitchenBarEnd.glb", "pos":Vector3(-2.9,0.0,15.0), "rot":180.0, "scale":1.7},
    {"path":"res://assets/community/runtime/furniture/kitchenBarEnd.glb", "pos":Vector3(2.9,0.0,15.0), "rot":0.0, "scale":1.7},
    {"path":"res://assets/community/runtime/furniture/stoolBar.glb", "pos":Vector3(-1.8,0.0,12.8), "rot":0.0, "scale":1.5},
    {"path":"res://assets/community/runtime/furniture/stoolBarSquare.glb", "pos":Vector3(0.0,0.0,12.8), "rot":15.0, "scale":1.5},
    {"path":"res://assets/community/runtime/furniture/stoolBar.glb", "pos":Vector3(1.8,0.0,12.8), "rot":0.0, "scale":1.5},
    {"path":"res://assets/community/runtime/furniture/loungeSofaLong.glb", "pos":Vector3(-5.5,0.0,15.0), "rot":90.0, "scale":1.45},
    {"path":"res://assets/community/runtime/furniture/loungeChair.glb", "pos":Vector3(5.2,0.0,14.0), "rot":-75.0, "scale":1.45},
    {"path":"res://assets/community/runtime/furniture/tableRound.glb", "pos":Vector3(4.5,0.0,11.5), "rot":0.0, "scale":1.35},
    {"path":"res://assets/community/runtime/furniture/speaker.glb", "pos":Vector3(-3.8,0.0,16.5), "rot":25.0, "scale":1.55},
    {"path":"res://assets/community/runtime/furniture/speaker.glb", "pos":Vector3(3.8,0.0,16.5), "rot":-25.0, "scale":1.55},
    {"path":"res://assets/community/runtime/furniture/radio.glb", "pos":Vector3(0.0,1.05,15.0), "rot":180.0, "scale":1.2},
    {"path":"res://assets/community/runtime/furniture/televisionVintage.glb", "pos":Vector3(-5.6,0.5,10.5), "rot":70.0, "scale":1.4},
    {"path":"res://assets/community/runtime/furniture/lampSquareFloor.glb", "pos":Vector3(5.8,0.0,10.0), "rot":0.0, "scale":1.6},
    {"path":"res://assets/community/runtime/furniture/pottedPlant.glb", "pos":Vector3(-5.0,0.0,11.0), "rot":0.0, "scale":1.3},
    {"path":"res://assets/community/runtime/furniture/ceilingFan.glb", "pos":Vector3(0.0,4.0,13.8), "rot":0.0, "scale":1.7}
]

func _ready() -> void:
    name = "CommunityCathedralSetDress"
    for spec in PLACEMENTS:
        _place(spec)
    print("COMMUNITY_SET_DRESS loaded=%d missing=%d" % [loaded_count, missing_count])

func _place(spec: Dictionary) -> void:
    var path := str(spec["path"])
    if not ResourceLoader.exists(path):
        missing_count += 1
        return
    var resource = load(path)
    if not resource is PackedScene:
        missing_count += 1
        return
    var instance := (resource as PackedScene).instantiate()
    if not instance is Node3D:
        instance.queue_free()
        missing_count += 1
        return
    var node := instance as Node3D
    node.name = "Community_%s" % path.get_file().get_basename()
    node.position = spec["pos"] as Vector3
    node.rotation_degrees.y = float(spec["rot"])
    var uniform_scale := float(spec["scale"])
    node.scale = Vector3.ONE * uniform_scale
    add_child(node)
    loaded_count += 1

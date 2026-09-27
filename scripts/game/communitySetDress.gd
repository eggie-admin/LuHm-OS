extends Node3D

# Crown Cathedral runtime set dressing.
# Every asset in assets/community/selected-assets.json is instantiated once.
# Assets are CC0, fetched only at build time, and never downloaded at runtime.

var loaded_count := 0
var missing_count := 0

const CITY_ASSETS := [
    "building-a.glb", "building-b.glb", "building-c.glb", "building-d.glb", "building-e.glb",
    "building-f.glb", "building-g.glb", "building-h.glb", "building-i.glb", "building-j.glb",
    "building-k.glb", "building-l.glb", "building-m.glb", "building-n.glb", "building-o.glb",
    "building-p.glb", "building-q.glb", "building-r.glb", "building-s.glb", "building-t.glb",
    "chimney-basic.glb", "chimney-large.glb", "chimney-medium.glb", "chimney-small.glb", "detail-tank.glb"
]

const FACTORY_ASSETS := [
    "catwalk-corner.glb", "catwalk-cross.glb", "catwalk-junction.glb", "catwalk-stairs-loop.glb", "catwalk-stairs.glb", "catwalk-straight.glb",
    "conveyor.glb", "conveyor-corner.glb", "conveyor-long.glb",
    "crane.glb", "crane-lift.glb", "crane-magnet.glb",
    "door-wide-open.glb", "floor-large.glb",
    "hopper-high-round.glb", "hopper-high-square.glb",
    "lever-double.glb", "lever-single.glb",
    "machine.glb", "machine-bed.glb", "machine-connection-pipe.glb", "machine-window.glb",
    "pipe-large-bend.glb", "pipe-large-cross.glb", "pipe-large-curve.glb", "pipe-large-junction.glb", "pipe-large-long.glb", "pipe-large-side.glb", "pipe-large-valve.glb",
    "robot-arm-a.glb", "screen-wide.glb", "warning-traffic.glb"
]

const FURNITURE_PLACEMENTS := [
    {"name":"bench.glb", "pos":Vector3(-5.0,0.0,11.2), "rot":90.0, "scale":1.35},
    {"name":"chair.glb", "pos":Vector3(4.4,0.0,12.0), "rot":-32.0, "scale":1.30},
    {"name":"chairCushion.glb", "pos":Vector3(3.4,0.0,15.7), "rot":205.0, "scale":1.35},
    {"name":"kitchenBar.glb", "pos":Vector3(0.0,0.0,16.4), "rot":180.0, "scale":1.55},
    {"name":"kitchenBarEnd.glb", "pos":Vector3(-2.75,0.0,16.4), "rot":180.0, "scale":1.55},
    {"name":"stoolBar.glb", "pos":Vector3(-1.5,0.0,14.2), "rot":8.0, "scale":1.38},
    {"name":"stoolBarSquare.glb", "pos":Vector3(0.2,0.0,14.25), "rot":-8.0, "scale":1.38},
    {"name":"table.glb", "pos":Vector3(-4.5,0.0,13.3), "rot":90.0, "scale":1.28},
    {"name":"tableRound.glb", "pos":Vector3(4.35,0.0,13.4), "rot":0.0, "scale":1.28},
    {"name":"loungeSofaLong.glb", "pos":Vector3(-5.4,0.0,16.4), "rot":90.0, "scale":1.34},
    {"name":"loungeChair.glb", "pos":Vector3(5.1,0.0,15.4), "rot":-70.0, "scale":1.35},
    {"name":"speaker.glb", "pos":Vector3(-3.65,0.0,17.5), "rot":20.0, "scale":1.40},
    {"name":"radio.glb", "pos":Vector3(0.5,1.03,16.2), "rot":180.0, "scale":1.08},
    {"name":"televisionVintage.glb", "pos":Vector3(-5.65,0.48,10.5), "rot":68.0, "scale":1.30},
    {"name":"lampWall.glb", "pos":Vector3(5.9,2.35,18.7), "rot":-90.0, "scale":1.20},
    {"name":"lampSquareFloor.glb", "pos":Vector3(5.6,0.0,10.7), "rot":0.0, "scale":1.42},
    {"name":"sideTable.glb", "pos":Vector3(3.2,0.0,11.0), "rot":12.0, "scale":1.20},
    {"name":"rugRectangle.glb", "pos":Vector3(0.0,0.025,13.1), "rot":0.0, "scale":1.85},
    {"name":"pottedPlant.glb", "pos":Vector3(-5.6,0.0,18.0), "rot":0.0, "scale":1.25},
    {"name":"ceilingFan.glb", "pos":Vector3(0.0,4.05,14.4), "rot":0.0, "scale":1.55}
]

func _ready() -> void:
    name = "CommunityCathedralSetDress"
    _place_city_ring()
    _place_factory_ring()
    _place_furniture_core()
    print("COMMUNITY_SET_DRESS loaded=%d missing=%d expected=77" % [loaded_count, missing_count])

func _place_city_ring() -> void:
    for i in range(CITY_ASSETS.size()):
        var angle := (float(i) / float(CITY_ASSETS.size())) * TAU
        var radius := 25.0 + float(i % 4) * 2.1
        var pos := Vector3(sin(angle) * radius, 0.0, cos(angle) * radius + 3.0)
        var scale_value := 2.1 + float(i % 5) * 0.18
        if i >= 20:
            scale_value = 2.4 + float(i % 3) * 0.22
        _place_asset("city-industrial", CITY_ASSETS[i], pos, -rad_to_deg(angle) + 180.0, scale_value)

func _place_factory_ring() -> void:
    for i in range(FACTORY_ASSETS.size()):
        var side := -1.0 if i % 2 == 0 else 1.0
        var row := int(i / 2)
        var x := side * (10.0 + float(row % 4) * 1.15)
        var z := -13.0 + float(row) * 2.55
        var y := 0.0
        if FACTORY_ASSETS[i].begins_with("pipe-large"):
            y = 1.7 + float(i % 3) * 0.35
        var rot := 90.0 * side + float((i % 5) - 2) * 7.0
        var scale_value := 1.18 + float(i % 4) * 0.10
        _place_asset("factory", FACTORY_ASSETS[i], Vector3(x, y, z), rot, scale_value)

func _place_furniture_core() -> void:
    for spec in FURNITURE_PLACEMENTS:
        _place_asset(
            "furniture",
            str(spec["name"]),
            spec["pos"] as Vector3,
            float(spec["rot"]),
            float(spec["scale"])
        )

func _place_asset(group: String, asset_name: String, pos: Vector3, rot_y: float, uniform_scale: float) -> void:
    var path := "res://assets/community/runtime/%s/%s" % [group, asset_name]
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
    node.name = "Community_%s_%02d" % [asset_name.get_basename(), loaded_count]
    node.position = pos
    node.rotation_degrees.y = rot_y
    node.scale = Vector3.ONE * uniform_scale
    add_child(node)
    loaded_count += 1

func get_runtime_asset_summary() -> Dictionary:
    return {
        "loaded": loaded_count,
        "missing": missing_count,
        "expected": CITY_ASSETS.size() + FACTORY_ASSETS.size() + FURNITURE_PLACEMENTS.size()
    }

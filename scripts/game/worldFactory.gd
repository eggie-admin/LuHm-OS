extends RefCounted

const NeonWorldScript := preload("res://scripts/game/neonWorld.gd")
const LumCoffeeHouseScript := preload("res://scripts/game/lumCoffeeHouseScene.gd")
const CathedralWorldScript := preload("res://scripts/game/cathedralWorld.gd")
const AramoorWorldScript := preload("res://scripts/world/aramoorArchipelagoBuilder.gd")

func createWorld(worldId: String) -> Node3D:
    var world: Node3D
    match worldId:
        "neonRiverwalk":
            world = NeonWorldScript.new()
            world.name = "NeonWorld"
        "lumCoffeeHouse":
            world = LumCoffeeHouseScript.new()
            world.name = "LumCoffeeHouse"
        "cathedral":
            world = CathedralWorldScript.new()
            world.name = "CathedralWorld"
        "aramoorArchipelago":
            world = AramoorWorldScript.new()
            world.name = "AramoorArchipelago"
        _:
            return null
    return world

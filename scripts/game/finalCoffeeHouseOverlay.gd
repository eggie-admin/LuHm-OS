extends Node3D

const CoffeeHouseSetDressScript := preload("res://scripts/game/coffeeHouseSetDress.gd")
const PrivateNexusSetDressScript := preload("res://scripts/game/privateNexusSetDress.gd")

var applied := false

func _ready() -> void:
    call_deferred("_apply_final_mutation")

func _apply_final_mutation() -> void:
    if applied:
        return
    var runtime_root := get_parent()
    if runtime_root == null:
        return
    var world := runtime_root.get_node_or_null("NeonWorld") as Node3D
    if world == null:
        await get_tree().process_frame
        world = runtime_root.get_node_or_null("NeonWorld") as Node3D
    if world == null:
        push_warning("FinalCoffeeHouseMutation: NeonWorld unavailable")
        return

    if world.get_node_or_null("CoffeeHouseSetDress") == null:
        var coffee := CoffeeHouseSetDressScript.new()
        coffee.name = "CoffeeHouseSetDress"
        world.add_child(coffee)

    if world.get_node_or_null("PrivateNexusSetDress") == null:
        var nexus := PrivateNexusSetDressScript.new()
        nexus.name = "PrivateNexusSetDress"
        world.add_child(nexus)

    var lum := world.get_node_or_null("LumAvatarSocket") as Node3D
    if lum != null:
        lum.position = Vector3(0.0, 0.05, 13.1)

    var halo := world.get_node_or_null("LumHalo") as OmniLight3D
    if halo != null:
        halo.position = Vector3(0.0, 3.0, 13.1)
        halo.light_color = Color("ffb56b")
        halo.light_energy = 1.55
        halo.omni_range = 6.5

    applied = true
    print("FINAL_COFFEE_HOUSE_MUTATION=APPLIED")

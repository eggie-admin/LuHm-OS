extends Node3D

const CoffeeHouseSetDressScript := preload("res://scripts/game/coffeeHouseSetDress.gd")
const CrownCathedralSetDressScript := preload("res://scripts/game/crownCathedralSetDress.gd")
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

    if world.get_node_or_null("CrownCathedralSetDress") == null:
        var crown := CrownCathedralSetDressScript.new()
        crown.name = "CrownCathedralSetDress"
        world.add_child(crown)

    if world.get_node_or_null("PrivateNexusSetDress") == null:
        var nexus := PrivateNexusSetDressScript.new()
        nexus.name = "PrivateNexusSetDress"
        world.add_child(nexus)

    var lum := world.get_node_or_null("LumAvatarSocket") as Node3D
    if lum != null:
        lum.position = Vector3(0.0, 0.05, 13.35)
        lum.rotation_degrees.y = 180.0

    var halo := world.get_node_or_null("LumHalo") as OmniLight3D
    if halo != null:
        halo.position = Vector3(0.0, 3.0, 13.35)
        halo.light_color = Color("ffb56b")
        halo.light_energy = 1.85
        halo.omni_range = 7.2

    # Author the player's first readable view toward the Cathedral.
    # The previous default yaw looked away from the +Z coffeehouse volume.
    var player := runtime_root.get_node_or_null("PlayerController") as CharacterBody3D
    if player != null:
        player.position = Vector3(0.0, 1.15, 6.8)
        player.set("spawn_point", player.position)
        if player.has_method("orbit_by"):
            player.call("orbit_by", Vector2(-PI, -0.04))
        var spring := player.get_node_or_null("CameraYaw/CameraPitch/SpringArm3D") as SpringArm3D
        if spring != null:
            spring.spring_length = 6.4

    applied = true
    print("CROWN_CATHEDRAL_MUTATION=APPLIED")

extends Node3D

const CoffeeHouseSetDressScript := preload("res://scripts/game/coffeeHouseSetDress.gd")
const CrownCathedralSetDressScript := preload("res://scripts/game/crownCathedralSetDress.gd")
const CrownDonorGalleryScript := preload("res://scripts/game/crownDonorGallery.gd")
const PrivateNexusSetDressScript := preload("res://scripts/game/privateNexusSetDress.gd")
const TARGET_LUM_HEIGHT := 1.90
const LumFocus := preload("res://scripts/game/lumFocus.gd")

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

    if world.get_node_or_null("CrownDonorGallery") == null:
        var gallery := CrownDonorGalleryScript.new()
        gallery.name = "CrownDonorGallery"
        world.add_child(gallery)

    if world.get_node_or_null("PrivateNexusSetDress") == null:
        var nexus := PrivateNexusSetDressScript.new()
        nexus.name = "PrivateNexusSetDress"
        world.add_child(nexus)

    var lum := world.get_node_or_null("LumAvatarSocket") as Node3D
    if lum != null:
        lum.position = Vector3(0.0, 0.05, 13.35)
        lum.rotation_degrees.y = 180.0
        _normalize_visual_height(lum, TARGET_LUM_HEIGHT)

    var halo := world.get_node_or_null("LumHalo") as OmniLight3D
    if halo != null:
        halo.position = Vector3(0.0, 3.0, 13.35)
        halo.light_color = Color("ffb56b")
        halo.light_energy = 1.85
        halo.omni_range = 7.2

    # A presentation module owns initial framing; movement and world stay intact.
    var player := runtime_root.get_node_or_null("PlayerController") as CharacterBody3D
    if player != null and lum != null:
        LumFocus.apply(player, lum)

    applied = true
    print("CROWN_CATHEDRAL_MUTATION=APPLIED")

func _normalize_visual_height(root_node: Node3D, target_height: float) -> void:
    var measured: float = _measure_visual_height(root_node)
    if measured <= 0.001:
        push_warning("CrownCathedral: Lum visual bounds unavailable")
        return
    var factor: float = clampf(target_height / measured, 0.05, 200.0)
    root_node.scale *= factor
    if root_node.has_method("commit_presentation_scale"):
        root_node.call("commit_presentation_scale")
    var final_height: float = _measure_visual_height(root_node)
    print("CROWN_LUM_HEIGHT raw=%.4f factor=%.4f final=%.4f" % [measured, factor, final_height])

func _measure_visual_height(root_node: Node3D) -> float:
    # Measure what the renderer sees in world coordinates. Do not transform back
    # into the avatar root, because doing so would cancel the corrective root scale.
    var min_y: float = 1.0e20
    var max_y: float = -1.0e20
    var found: bool = false
    var axis_values: Array[float] = [0.0, 1.0]
    for child in root_node.find_children("*", "MeshInstance3D", true, false):
        var mesh_instance := child as MeshInstance3D
        if mesh_instance == null or mesh_instance.mesh == null:
            continue
        var box: AABB = mesh_instance.get_aabb()
        for xi in axis_values:
            for yi in axis_values:
                for zi in axis_values:
                    var local_corner: Vector3 = box.position + Vector3(box.size.x * xi, box.size.y * yi, box.size.z * zi)
                    var point: Vector3 = mesh_instance.global_transform * local_corner
                    min_y = minf(min_y, point.y)
                    max_y = maxf(max_y, point.y)
                    found = true
    return max_y - min_y if found else 0.0

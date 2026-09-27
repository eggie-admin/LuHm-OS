extends Node3D

# LuHm OS full-game donor gallery.
# KAI9000 is provenance/donor inventory only; these two textures are rights-gated,
# hash-pinned LuHm-owned/generated derivatives staged at build time.

const CATHEDRAL_ARCHIVE := preload("res://assets/donor/runtime/cathedral_hub_archive.webp")
const LUM_RETRO_SHRINE := preload("res://assets/donor/runtime/lum_ps1_float_shrine.webp")

func _ready() -> void:
    name = "CrownDonorGallery"
    _add_holo_panel(
        "CathedralArchiveHolo",
        CATHEDRAL_ARCHIVE,
        Vector3(-5.25, 2.55, 13.55),
        Vector3(0.0, 90.0, 0.0),
        0.0038,
        "CATHEDRAL ARCHIVE // LUHM OS"
    )
    _add_holo_panel(
        "LumRetroShrine",
        LUM_RETRO_SHRINE,
        Vector3(5.18, 2.20, 13.75),
        Vector3(0.0, -90.0, 0.0),
        0.0037,
        "LUM // PROJECT HYDRA RETRO SHRINE"
    )

func _add_holo_panel(
    panel_name: String,
    texture: Texture2D,
    pos: Vector3,
    rot: Vector3,
    pixel_size: float,
    caption: String
) -> void:
    var anchor := Node3D.new()
    anchor.name = panel_name
    anchor.position = pos
    anchor.rotation_degrees = rot
    add_child(anchor)

    var backing := MeshInstance3D.new()
    backing.name = "ArchiveBacking"
    var box := BoxMesh.new()
    box.size = Vector3(0.08, 3.25, 2.35)
    backing.mesh = box
    backing.position = Vector3(0.05, 0.0, 0.0)
    var frame_mat := StandardMaterial3D.new()
    frame_mat.albedo_color = Color("120d18")
    frame_mat.metallic = 0.55
    frame_mat.roughness = 0.32
    frame_mat.emission_enabled = true
    frame_mat.emission = Color("4a1739")
    frame_mat.emission_energy_multiplier = 0.45
    backing.material_override = frame_mat
    anchor.add_child(backing)

    var sprite := Sprite3D.new()
    sprite.name = "ArchiveTexture"
    sprite.texture = texture
    sprite.pixel_size = pixel_size
    sprite.shaded = false
    sprite.double_sided = true
    sprite.position = Vector3(-0.02, 0.0, 0.0)
    anchor.add_child(sprite)

    var label := Label3D.new()
    label.name = "ArchiveCaption"
    label.text = caption
    label.position = Vector3(-0.05, -1.88, 0.0)
    label.rotation_degrees = Vector3(0.0, -90.0, 0.0)
    label.font_size = 28
    label.modulate = Color("ffd4ec")
    label.outline_size = 5
    label.outline_modulate = Color("130812")
    anchor.add_child(label)

func get_donor_summary() -> Dictionary:
    return {
        "expected": 2,
        "loaded": 2 if CATHEDRAL_ARCHIVE != null and LUM_RETRO_SHRINE != null else 0,
        "scope": "LUHM_OS_FULL_GAME_ONLY",
        "kai9000_authority": false
    }

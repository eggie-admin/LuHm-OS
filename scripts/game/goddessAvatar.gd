extends Node3D

const MorphControllerScript := preload("res://scripts/game/characterMorphController.gd")
const ComponentAssemblerScript := preload("res://scripts/game/characterComponentAssembler.gd")

@export_enum("lum", "urd", "belldandy", "skuld") var character_id := "lum"
@export var assemble_on_ready := false
@export var apply_morph_preset_on_ready := false

var component_assembler: Node
var morph_controller: Node
var component_receipt: Dictionary = {}
var morph_receipt: Dictionary = {}

func _ready() -> void:
    component_assembler = ComponentAssemblerScript.new()
    component_assembler.name = "ComponentAssembler"
    add_child(component_assembler)
    component_assembler.configure(self)

    morph_controller = MorphControllerScript.new()
    morph_controller.name = "MorphController"
    add_child(morph_controller)
    morph_controller.configure(self)

    if assemble_on_ready:
        component_receipt = component_assembler.assemble_character(character_id)
    if apply_morph_preset_on_ready:
        morph_receipt = morph_controller.apply_preset(character_id)

func assemble() -> Dictionary:
    component_receipt = component_assembler.assemble_character(character_id)
    return component_receipt.duplicate(true)

func apply_morph_preset() -> Dictionary:
    morph_receipt = morph_controller.apply_preset(character_id)
    return morph_receipt.duplicate(true)

func runtime_summary() -> Dictionary:
    return {
        "schema": "luhmOs.goddessAvatarRuntimeSummary.v1",
        "character": character_id,
        "componentReceipt": component_receipt.duplicate(true),
        "morphReceipt": morph_receipt.duplicate(true),
        "canonPromoted": false,
        "crownAuthority": false
    }

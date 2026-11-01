extends Node3D
## Isolated art-studio proof: fixed camera + 2D precomposed art + live 3D actor.
## Never imports private assets, changes firmware or alters the canonical Main scene.

@onready var actor: Node3D = $Actor
@onready var status_label: Label = $HUD/Panel/Margin/VBox/Status
var steps: int = 0

func _ready() -> void:
    status_label.text = "First Night 2.5D: move the live 3D placeholder across the static Cathedral."
    print("FIRST_NIGHT_25D_STAGE_READY")

func _move(direction: int) -> void:
    actor.position.x = clampf(actor.position.x + float(direction) * 0.9, -3.2, 3.2)
    steps += 1
    status_label.text = "3D actor moved; position x=%.1f | steps=%d" % [actor.position.x, steps]

func _on_return_pressed() -> void:
    get_tree().change_scene_to_file("res://scenes/Main.tscn")

func _on_left_pressed() -> void:
    _move(-1)

func _on_right_pressed() -> void:
    _move(1)

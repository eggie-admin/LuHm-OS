"""Source-only fast checks for the private Proposed Godot goddess showcase.

Does not run Godot, build/export assets, fetch Drive content, or grant Crown.
Actual runtime evidence requires an exact-source, Professor-authorized CAST.
"""
from pathlib import Path

GAME = Path(__file__).resolve().parents[1] / "scripts/game/goddessRehearsal.gd"
text = GAME.read_text(encoding="utf-8")

required = (
    "const LumAvatarScene := preload",
    "func _build_actor(i: int)",
    'sparkles.name = "ProposedSparkles"',
    "var sparkles := CPUParticles3D.new()",
    "sparkles.one_shot = true",
    "sparkles.mesh = spark_mesh",
    "func _cast_sparks() -> void:",
    "func _dance() -> void:",
    "func _talk() -> void:",
    "func _tap_actor(screen_point: Vector2)",
    "func _unhandled_input(event: InputEvent)",
    "get_tree().change_scene_to_file",
    'art_state = "PROTOTYPE STAND-IN · MODEL PENDING"',
)
for token in required:
    assert token in text, f"Missing Proposed showcase contract: {token}"

assert text.count("func _cast_sparks()") == 1
assert text.count("func _dance()") == 1
assert text.count("func _talk()") == 1
assert text.count("ProposedSparkles") == 1
assert "HTTPClient" not in text and "load_external_asset" not in text

# First real session interaction loop: not just static dialogue or HUD skeleton.
for token in ("var _bond_points := [0, 0, 0, 0]",
    "const ROUTE_LINES :=",
    "func _route_status() -> String:",
    "\"CATHEDRAL CIRCLE COMPLETE\"",
    "mini(9, _bond_points[active_index] + 1)",
    "_action_grid.columns = 1 if narrow else 3",
    "elif event.keycode == KEY_T:",
    "elif event.keycode == KEY_D:",
    "elif event.keycode == KEY_ESCAPE:",):
    assert token in text, f"Missing playable interaction: {token}"
assert text.count("func _route_status()") == 1
assert "FileAccess.open_encrypted" not in text

print("PROPOSED_GODDESS_INTERACTION_SOURCE=PASS (SOURCE ONLY, NO EXPORT OR DEVICE PROOF)")

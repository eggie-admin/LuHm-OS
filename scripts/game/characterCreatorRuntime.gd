extends Node

const BodyForgeControllerScript := preload("res://scripts/game/bodyForgeController.gd")

var world: Node3D
var bridge: Node
var forge: Node
var _bind_attempts := 0

func configure(world_node: Node3D, bridge_node: Node) -> void:
    world = world_node
    bridge = bridge_node
    if bridge != null:
        bridge.avatar_tune_requested.connect(_on_tune_requested)
        bridge.avatar_reset_requested.connect(_on_reset_requested)
        bridge.avatar_inspect_requested.connect(_on_inspect_requested)
    call_deferred("_bind_avatar")

func _bind_avatar() -> void:
    if forge != null or world == null:
        return
    var target := world.get("lum_avatar") as Node3D
    if target == null:
        _bind_attempts += 1
        if _bind_attempts < 12:
            call_deferred("_bind_avatar")
        return
    forge = BodyForgeControllerScript.new()
    forge.name = "LumBodyForge"
    add_child(forge)
    forge.call("configure", target)

func _on_tune_requested(key: String, value: float) -> void:
    if forge != null:
        forge.call("set_slider", key, value)

func _on_reset_requested() -> void:
    if forge != null:
        forge.call("reset_profile")

func _on_inspect_requested() -> void:
    if bridge == null:
        return
    var payload: Dictionary
    if forge == null:
        payload = {
            "schema": "luhm.avatar.creator.summary.v1",
            "mode": "binding",
            "supported_sliders": [],
            "profile": {}
        }
    else:
        payload = forge.call("get_summary")
    bridge.call("post_reply", {
        "schema": "luhm.bridge.reply.v1",
        "type": "avatar.summary",
        "payload": payload
    })

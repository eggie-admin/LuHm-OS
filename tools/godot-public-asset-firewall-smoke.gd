extends SceneTree

const forbidden_resources := [
    "res://assets/lum/luhm.glb",
    "res://assets/lum/luhmRunning.glb",
]

func _initialize() -> void:
    for resource_path in forbidden_resources:
        if FileAccess.file_exists(resource_path) or ResourceLoader.exists(resource_path):
            push_error("RED_PUBLIC_GODOT_ASSET_FIREWALL: " + resource_path)
            quit(1)
            return
    print("GREEN_PUBLIC_GODOT_ASSET_FIREWALL_RUNTIME")
    quit(0)

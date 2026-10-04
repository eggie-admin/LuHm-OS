@tool
extends EditorPlugin

var export_plugin: AndroidExportPlugin

func _enter_tree() -> void:
    export_plugin = AndroidExportPlugin.new()
    add_export_plugin(export_plugin)

func _exit_tree() -> void:
    remove_export_plugin(export_plugin)
    export_plugin = null

class AndroidExportPlugin extends EditorExportPlugin:
    var _plugin_name := "KAIWebView"

    func _supports_platform(platform) -> bool:
        return platform is EditorExportPlatformAndroid

    func _get_name() -> String:
        return _plugin_name

    func _library_path(debug: bool) -> String:
        var relative := "kai_webview/bin/kaiwebview-debug.aar" if debug else "kai_webview/bin/kaiwebview-release.aar"
        var project_path := "res://addons/" + relative
        return relative if FileAccess.file_exists(project_path) else ""

    func _get_android_libraries(platform, debug) -> PackedStringArray:
        var library := _library_path(debug)
        if library.is_empty():
            # Native-only CI/install lanes intentionally fall back to the Godot HUD
            # when the caged WebGlass AAR has not been explicitly staged.
            return PackedStringArray()
        return PackedStringArray([library])

    func _get_android_dependencies(platform, debug) -> PackedStringArray:
        if _library_path(debug).is_empty():
            return PackedStringArray()
        return PackedStringArray(["androidx.webkit:webkit:1.17.1"])

    func _get_android_dependencies_maven_repos(platform, debug) -> PackedStringArray:
        if _library_path(debug).is_empty():
            return PackedStringArray()
        return PackedStringArray(["https://maven.google.com"])

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

    func _get_android_libraries(platform, debug) -> PackedStringArray:
        if debug:
            return PackedStringArray(["kai_webview/bin/kaiwebview-debug.aar"])
        return PackedStringArray(["kai_webview/bin/kaiwebview-release.aar"])

    func _get_android_dependencies(platform, debug) -> PackedStringArray:
        return PackedStringArray(["androidx.webkit:webkit:1.17.1"])

    func _get_android_dependencies_maven_repos(platform, debug) -> PackedStringArray:
        return PackedStringArray(["https://maven.google.com"])

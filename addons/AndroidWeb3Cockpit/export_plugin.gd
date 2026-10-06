@tool
extends EditorPlugin

var export_plugin: AndroidExportPlugin

func _enter_tree():
    export_plugin = AndroidExportPlugin.new()
    add_export_plugin(export_plugin)

func _exit_tree():
    remove_export_plugin(export_plugin)
    export_plugin = null

class AndroidExportPlugin extends EditorExportPlugin:
    var _plugin_name = "AndroidWeb3Cockpit"

    func _supports_platform(platform):
        return platform is EditorExportPlatformAndroid

    func _get_android_libraries(_platform, debug):
        if debug:
            return PackedStringArray(["AndroidWeb3Cockpit/bin/debug/AndroidWeb3Cockpit-debug.aar"])
        return PackedStringArray(["AndroidWeb3Cockpit/bin/release/AndroidWeb3Cockpit-release.aar"])

    func _get_android_dependencies(_platform, _debug):
        return PackedStringArray(["androidx.webkit:webkit:1.17.1"])

    func _get_name():
        return _plugin_name

extends Node
class_name PetWindowController

signal mode_changed(mode_name: String)
signal android_bubble_requested
signal android_background_requested
signal exit_requested

enum Mode {
    FULLSCREEN,
    MINI_PLAYER,
    PET_INSPECT,
    CHAT_HEAD,
    BACKGROUND,
    EXITING,
}

const MINI_SIZE := Vector2i(420, 120)
const INSPECT_SIZE := Vector2i(520, 700)
const CHAT_HEAD_SIZE := Vector2i(320, 320)

var mode: int = Mode.FULLSCREEN

func request_mode(next_mode: int) -> bool:
    if next_mode < Mode.FULLSCREEN or next_mode > Mode.EXITING:
        return false
    if mode == Mode.EXITING:
        return false

    match next_mode:
        Mode.FULLSCREEN:
            _apply_fullscreen()
        Mode.MINI_PLAYER:
            _apply_desktop_window(MINI_SIZE, true)
        Mode.PET_INSPECT:
            _apply_desktop_window(INSPECT_SIZE, true)
        Mode.CHAT_HEAD:
            if OS.has_feature("android"):
                android_bubble_requested.emit()
            else:
                _apply_desktop_window(CHAT_HEAD_SIZE, true)
        Mode.BACKGROUND:
            if OS.has_feature("android"):
                android_background_requested.emit()
            else:
                get_window().visible = false
        Mode.EXITING:
            mode = Mode.EXITING
            mode_changed.emit(mode_label(mode))
            exit_requested.emit()
            get_tree().quit()
            return true

    mode = next_mode
    mode_changed.emit(mode_label(mode))
    return true

func restore_visible() -> void:
    if not OS.has_feature("android"):
        get_window().visible = true

func mode_label(value: int) -> String:
    match value:
        Mode.FULLSCREEN:
            return "FULLSCREEN"
        Mode.MINI_PLAYER:
            return "MINI_PLAYER"
        Mode.PET_INSPECT:
            return "PET_INSPECT"
        Mode.CHAT_HEAD:
            return "CHAT_HEAD"
        Mode.BACKGROUND:
            return "BACKGROUND"
        Mode.EXITING:
            return "EXITING"
    return "UNKNOWN"

func _apply_fullscreen() -> void:
    restore_visible()
    if OS.has_feature("android"):
        return
    _reset_desktop_flags()
    DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN)

func _apply_desktop_window(size: Vector2i, always_on_top: bool) -> void:
    restore_visible()
    if OS.has_feature("android"):
        return

    DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)
    _reset_desktop_flags()
    DisplayServer.window_set_flag(DisplayServer.WINDOW_FLAG_BORDERLESS, true)
    DisplayServer.window_set_flag(DisplayServer.WINDOW_FLAG_ALWAYS_ON_TOP, always_on_top)
    DisplayServer.window_set_size(size)

    var screen := DisplayServer.window_get_current_screen()
    var usable := DisplayServer.screen_get_usable_rect(screen)
    var target := usable.position + Vector2i(
        maxi(usable.size.x - size.x - 24, 0),
        maxi(usable.size.y - size.y - 24, 0)
    )
    DisplayServer.window_set_position(target)

func _reset_desktop_flags() -> void:
    if OS.has_feature("android"):
        return
    DisplayServer.window_set_flag(DisplayServer.WINDOW_FLAG_BORDERLESS, false)
    DisplayServer.window_set_flag(DisplayServer.WINDOW_FLAG_ALWAYS_ON_TOP, false)
    DisplayServer.window_set_flag(DisplayServer.WINDOW_FLAG_TRANSPARENT, false)
    DisplayServer.window_set_flag(DisplayServer.WINDOW_FLAG_NO_FOCUS, false)

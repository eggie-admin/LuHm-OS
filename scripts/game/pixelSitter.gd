extends Control
class_name PixelSitter

var _time := 0.0
var _blink := false
var _mood := "IDLE"

func _ready() -> void:
    custom_minimum_size = Vector2(144, 144)
    mouse_filter = Control.MOUSE_FILTER_STOP
    set_process(true)
    queue_redraw()

func set_mood(value: String) -> void:
    _mood = value.to_upper()
    queue_redraw()

func _process(delta: float) -> void:
    _time += delta
    _blink = fmod(_time, 4.2) > 3.96
    queue_redraw()

func _px(rect: Rect2, color: Color) -> void:
    draw_rect(rect, color, true)

func _draw() -> void:
    var unit := maxf(minf(size.x, size.y) / 18.0, 1.0)
    var ox := (size.x - 18.0 * unit) * 0.5
    var oy := (size.y - 18.0 * unit) * 0.5
    var p := Vector2(ox, oy)

    var shadow := Color("300d2c")
    var hair := Color("7c3146")
    var hair_hi := Color("c65a70")
    var skin := Color("ffd0bc")
    var horn := Color("54f1e8")
    var ink := Color("14101d")
    var eye := Color("3df5eb")
    var suit := Color("122d36")
    var accent := Color("ff4aa5")

    # horns
    _px(Rect2(p + Vector2(4, 1) * unit, Vector2(2, 3) * unit), horn)
    _px(Rect2(p + Vector2(12, 1) * unit, Vector2(2, 3) * unit), horn)
    _px(Rect2(p + Vector2(5, 2) * unit, Vector2(8, 2) * unit), hair)

    # hair + head
    _px(Rect2(p + Vector2(4, 3) * unit, Vector2(10, 8) * unit), hair)
    _px(Rect2(p + Vector2(5, 4) * unit, Vector2(8, 7) * unit), skin)
    _px(Rect2(p + Vector2(4, 4) * unit, Vector2(2, 5) * unit), hair_hi)
    _px(Rect2(p + Vector2(12, 4) * unit, Vector2(2, 5) * unit), hair)
    _px(Rect2(p + Vector2(6, 3) * unit, Vector2(6, 2) * unit), hair_hi)

    # eyes
    var eye_h := 1.0 if not _blink else 0.35
    _px(Rect2(p + Vector2(6, 7.0 + (1.0-eye_h)*0.5) * unit, Vector2(2, eye_h) * unit), eye)
    _px(Rect2(p + Vector2(10, 7.0 + (1.0-eye_h)*0.5) * unit, Vector2(2, eye_h) * unit), eye)
    _px(Rect2(p + Vector2(8, 9) * unit, Vector2(2, 0.6) * unit), accent)

    # body / little executive oni outfit
    _px(Rect2(p + Vector2(5, 11) * unit, Vector2(8, 5) * unit), suit)
    _px(Rect2(p + Vector2(7, 11) * unit, Vector2(4, 2) * unit), skin)
    _px(Rect2(p + Vector2(8, 12) * unit, Vector2(2, 4) * unit), accent)
    _px(Rect2(p + Vector2(4, 12) * unit, Vector2(2, 3) * unit), shadow)
    _px(Rect2(p + Vector2(12, 12) * unit, Vector2(2, 3) * unit), shadow)

    # bat-wing hints + tail pixel
    _px(Rect2(p + Vector2(2, 11) * unit, Vector2(2, 2) * unit), shadow)
    _px(Rect2(p + Vector2(14, 11) * unit, Vector2(2, 2) * unit), shadow)
    _px(Rect2(p + Vector2(14, 15) * unit, Vector2(2, 1) * unit), accent)
    _px(Rect2(p + Vector2(15, 14) * unit, Vector2(1, 1) * unit), accent)

    if _mood == "ALERT":
        _px(Rect2(p + Vector2(2, 2) * unit, Vector2(2, 1) * unit), accent)
        _px(Rect2(p + Vector2(14, 2) * unit, Vector2(2, 1) * unit), accent)
    elif _mood == "SLEEP":
        _px(Rect2(p + Vector2(14, 5) * unit, Vector2(2, 1) * unit), Color("a5b4fc"))
        _px(Rect2(p + Vector2(15, 4) * unit, Vector2(2, 1) * unit), Color("a5b4fc"))

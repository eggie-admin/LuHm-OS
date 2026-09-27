extends SceneTree

const DoctrineGateScript := preload("res://scripts/core/doctrineGate.gd")

var failures: Array[String] = []

func _initialize() -> void:
    call_deferred("_run")

func _run() -> void:
    var gate := DoctrineGateScript.new()
    root.add_child(gate)

    _check(gate.is_valid(), "runtime doctrine loads")
    _check(gate.source_law() == "AI proposes. Policy authorizes. CI proves. Human promotes.", "source law exact")
    _check(gate.get_allowed_rituals() == ["crown_wake", "oni_trinity", "witching_hour"], "three ritual allowlist")
    _check(gate.allows_toy_action("pet_lum"), "pet action allowed")
    _check(not gate.allows_toy_action("shell_exec"), "unknown toy action blocked")
    _check(gate.allows_message_type("system.capabilities"), "capability query allowed")
    _check(not gate.allows_message_type("shell.exec"), "shell bridge blocked")
    _check(not gate.allows_message_type("fs.write"), "filesystem bridge blocked")

    var snapshot: Dictionary = gate.snapshot()
    var constraints = snapshot.get("constraints", {})
    _check(typeof(constraints) == TYPE_DICTIONARY, "constraints present")
    _check(String(constraints.get("network", "")) == "dark", "network dark")
    _check(not bool(constraints.get("root", true)), "root disabled")
    _finish()

func _check(condition: bool, label: String) -> void:
    if condition:
        print("GREEN: ", label)
    else:
        failures.append(label)
        push_error("RED: %s" % label)

func _finish() -> void:
    if failures.is_empty():
        print("LUHM RUNTIME DOCTRINE GATE SMOKE GREEN")
        quit(0)
    else:
        push_error("LUHM RUNTIME DOCTRINE GATE SMOKE RED: %s" % ", ".join(failures))
        quit(1)

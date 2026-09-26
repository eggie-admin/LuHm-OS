extends SceneTree

const ModifierScript := preload("res://scripts/game/bodyProportionModifier.gd")

var failures: Array[String] = []

func _initialize() -> void:
    call_deferred("_run")

func _run() -> void:
    var skeleton := Skeleton3D.new()
    root.add_child(skeleton)

    var names := [
        "Hips", "Spine", "Spine01", "Spine02", "neck", "Head",
        "LeftUpLeg", "LeftLeg", "LeftFoot", "LeftToeBase",
        "RightUpLeg", "RightLeg", "RightFoot", "RightToeBase",
        "LeftShoulder", "LeftArm", "LeftForeArm", "LeftHand",
        "RightShoulder", "RightArm", "RightForeArm", "RightHand"
    ]
    for name in names:
        skeleton.add_bone(name)

    var mapping := {
        "hips": "Hips",
        "spine": "Spine",
        "chest": "Spine01",
        "upper_chest": "Spine02",
        "neck": "neck",
        "head": "Head",
        "left_upper_leg": "LeftUpLeg",
        "left_lower_leg": "LeftLeg",
        "left_foot": "LeftFoot",
        "left_toes": "LeftToeBase",
        "right_upper_leg": "RightUpLeg",
        "right_lower_leg": "RightLeg",
        "right_foot": "RightFoot",
        "right_toes": "RightToeBase",
        "left_shoulder": "LeftShoulder",
        "left_upper_arm": "LeftArm",
        "left_lower_arm": "LeftForeArm",
        "left_hand": "LeftHand",
        "right_shoulder": "RightShoulder",
        "right_upper_arm": "RightArm",
        "right_lower_arm": "RightForeArm",
        "right_hand": "RightHand"
    }

    var modifier := ModifierScript.new()
    skeleton.add_child(modifier)
    modifier.configure(mapping)
    _check(modifier.set_normalized("head", 1.0), "head slider accepted")
    _check(modifier.set_normalized("shoulders", 1.0), "shoulder slider accepted")
    _check(modifier.set_normalized("torso", 1.0), "torso slider accepted")
    _check(not modifier.set_normalized("shell", 1.0), "unknown slider rejected")
    modifier._process_modification_with_delta(0.0)

    var head_scale := skeleton.get_bone_pose_scale(skeleton.find_bone("Head"))
    var shoulder_scale := skeleton.get_bone_pose_scale(skeleton.find_bone("LeftShoulder"))
    var spine_scale := skeleton.get_bone_pose_scale(skeleton.find_bone("Spine"))
    _check(head_scale.x > 1.10 and head_scale.y > 1.10, "head proportion applied")
    _check(shoulder_scale.x > 1.10, "shoulder width applied")
    _check(spine_scale.y > 1.05, "torso length applied")

    _finish()

func _check(condition: bool, label: String) -> void:
    if condition:
        print("GREEN: ", label)
    else:
        failures.append(label)
        push_error("RED: %s" % label)

func _finish() -> void:
    if failures.is_empty():
        print("ONI ATELIER BODYFORGE SMOKE GREEN")
        quit(0)
    else:
        push_error("ONI ATELIER BODYFORGE SMOKE RED: %s" % ", ".join(failures))
        quit(1)

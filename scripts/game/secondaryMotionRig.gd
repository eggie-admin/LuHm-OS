extends RefCounted

# Secondary-motion runtime is intentionally parked for the current Phase 1 rig lane.
# The canonical Phase 1 doctrine excludes dynamic spring-chain mutation until a later,
# separately proved rig milestone. Keep this API as a deterministic no-op so callers
# can inspect capability without smuggling a future rig feature into the current APK.
static func install(avatar: Node3D) -> Dictionary:
    if avatar == null:
        return {"status": "NO_AVATAR", "installed": []}
    return {
        "status": "PARKED_PHASE1",
        "installed": [],
        "reason": "secondary motion requires a later separately proved rig milestone"
    }

# Character inspection milestone

The dedicated Godot Web export accepts `?studio=inspect`. The default First Night
game stays unchanged. The existing standalone cockpit's **Inspect 3D** button
uses its one existing Godot iframe; the separate-page link is the fallback when
the host cannot mount a nested player.

This milestone provides front/side/back/three-quarter cameras, drag orbit,
wheel or two-finger pinch zoom, clay/material switching, neutral/stage light,
actual AnimationPlayer clip enumeration, paused initial playback, play/pause,
speed, seek, 30 fps frame stepping, and user-requested PNG/JSON downloads.
Controls scroll horizontally on narrow screens. Character assets are read from
the existing component contract. The original technical proxy has three real
diagnostic transform clips; it is never labelled an approved Goddess model.
Selecting an unassigned character clears prior geometry and disables playback.

No private art, donor GLB, reference photograph, soundtrack, credentials or
rights-pending asset is added to the public package. No provider calls, agent
activation, external uploads or durable server writes occur. JSON export is a
session observation, not a source/deploy identity receipt or Canon approval.

Not implemented: private GLB intake, hair/cloth simulation, bone editing,
expression controls, automatic bounds-based camera fitting, persistent storage,
ChatGPT Site tool discovery updates, or private-asset authorization. Those need
separate asset/runtime milestones. Concept art does not constitute a 3D rig.

Validation: Godot import/parse plus `tests/characterInspectorSmoke.gd`, followed
by the exported Web route in a real browser. Desktop browser proof does not
certify Samsung touch, ChatGPT inline mounting or a signed APK.

Rollback: revert the inspector change; no external schema or saved user data is
modified. Source base: `b60ac4ef0299c267df06638e505109bae9af8713`.

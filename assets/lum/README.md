# Lum 3D Asset Socket

The Godot runtime owns a stable model slot at:

`res://assets/lum/luhm.glb`

`LumAvatar` loads that GLB when present. If the asset is absent, invalid, or not yet committed, the game uses a lightweight procedural Lum fallback so gameplay and APK CI remain deterministic.

## Current external candidate

The conversation-supplied `luhm.glb` is a valid glTF 2.0 binary, but it is currently a **static model only**:

- SHA-256: `fa757ceb86358d6489f217c7d2624ac1d1d3e1d7e9c91601095d509131e9ec04`
- size: 56,240,120 bytes
- generator: `meshy-scene`
- meshes: 1
- skins: 0
- animations: 0

It is therefore **not** described as rigged yet.

## Rig-ready contract

Future reviewed Lum assets should preserve the same filename/socket and may add:

- humanoid skeleton + skin weights
- `AnimationPlayer` clips such as `idleBreath`, `talkSoft`, `greet`, `think`
- face blend shapes such as `blink`, `smile`, `jawOpen` / `mouth_open`
- visemes for A/E/I/O/U plus consonant groups
- hair/accessory secondary-motion bones

The runtime deliberately discovers optional animation and expression features instead of requiring them for boot. This keeps the game playable while the art asset evolves.

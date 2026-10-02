# LuHm OS Godot World/System Boundary

This directory is an architectural boundary marker, not a duplicate runtime tree.

For the Android Web3 cockpit milestone, the existing native Godot layer is **no longer the primary user-facing cockpit**. It becomes the scene/game and native world/system boundary behind the WebView shell:

- scene authority: `scenes/Main.tscn`
- runtime/controller: `scripts/main.gd`
- native Cathedral: preserved scene/system surface
- native 3D Detroit riverwalk: backend-owned native world/diagnostic surface for this milestone

The files remain in their proven canonical paths so Android/Godot build wiring is not broken merely to create a prettier directory tree.

## Front/backend contract

The jQuery front end emits `luhm:backend:open`. The Android/WebView wrapper is expected to translate that typed event through a narrow allowlisted native boundary. That wrapper is **not implemented on current main**, so this candidate does not fake runtime proof and does not expose shell execution.

No frontend plugin receives backend authority. Consequential actions remain Crown-gated.

# LuHm OS Backend GUI — Dry Run

This directory is an architectural boundary marker, not a duplicate runtime tree.

For the jQuery GUI split dry run, the **existing native Godot cockpit is the backend/system GUI**:

- scene authority: `scenes/Main.tscn`
- runtime/controller: `scripts/main.gd`
- native Cathedral: backend/system cockpit
- native 3D Detroit riverwalk: backend-owned native world/diagnostic surface for this milestone

The files remain in their proven canonical paths so Android/Godot build wiring is not broken merely to create a prettier directory tree.

## Front/backend contract

The jQuery front end emits `luhm:backend:open`. A future Android/WebView/native bridge may translate that typed event into opening the native Backend Cathedral. The dry run does **not** fake that bridge and does not expose shell execution.

No frontend plugin receives backend authority. Consequential actions remain Crown-gated.

# Godot 4 Web export target

The hardened harness expects a Godot 4 Web export at:

`host/harness/godot-export/index.html`

The active `Web Harness` export preset targets this directory with Web threads disabled. That keeps the first embedded viewer compatible with ordinary HTTPS without requiring `SharedArrayBuffer`/cross-origin isolation.

This directory intentionally contains no claimed build artifact until an exact-source Godot export is produced and verified.

# LuHm-OS Nightglass: One Character Vertical Slice

This feature is an **optional original game scene**, not a new game engine, ChatGPT app, cloud worker, public deploy, or change to the First Night Circuit default.

## What works in the proposed source
- From the existing Godot backend Cathedral menu, press **NIGHTGLASS BAR · TALK TO VESPER**.
- A standalone Godot 4 scene opens the **Nightglass Bar** and displays **Vesper Nocturne**, a procedurally modeled original proxy with amethyst hair, velvet cloak, moon rune, head, eyes and a real 3D interaction hitbox.
- The bar opens with a Vesper line already authored in `game/studio/nightglassHubV1.json`; tap **Back to Lum** to branch, then **TALK TO VESPER** to return.
- A two-way travel button changes from the bar to the Echo Shore and back, preserving per-scene dialogue.
- The scene is easy to leave using **RETURN TO FIRST NIGHT**. Godot stays the runtime authority.
- The existing `tools/creatorStudio.py` stores/validates original dialogue JSON in local SQLite, and keeps private-reference artwork and autonomous agents out.

All character art is **new, primitive geometry**. No copyrighted anime or mod meshes, rigging, shaders, external model inference or asset rights are claimed.

## Runtime proof

`.github/workflows/nightglass-playable-scene-audit.yml` runs Python 3 manuscript/SQLite validation and downloads checksum-pinned Godot **4.7.2**. It **runs the Godot engine**, not merely script parsing. The smoke instantiates `Main.tscn`, presses the real HUD's Nightglass menu button, verifies the scene transition, checks Vesper's 3D parts and hitbox, activates dialogue branch buttons, triggers the Talk button and travels bar → shore → bar. It rejects missing rights/quarantine holds and prints `NIGHTGLASS_GODOT_SCENE_SMOKE_GREEN` only on successful execution.

```sh
python3 tools/creatorStudio.py validate game/studio/nightglassHubV1.json
python3 -m unittest discover -s tests -p test_creatorStudio.py
godot --headless --editor --path . --quit
godot --headless --path . --script res://tests/nightglassRuntimeSmoke.gd
```

These commands work in an authorized Godot 4.7.2 checkout. Testing is headless; visual appearance, controller touch, Android install and the ChatGPT-host sandbox remain independent acceptance gates.

## ChatGPT in-chat widget limitation

The connected `luhm_open_cockpit` plugin tool was called on this date and returned **"LuHm cockpit is unavailable."** Its fallback `luhm_open_mobile_cockpit` points at a **browser-memory-only static antenna**. Neither result proves the MCP UI resource mounted, and creating a Godot scene in GitHub does not update a separate deployed Site app. Keep the existing private plugin and Site identity; **do not create a replacement plugin or expose an unauthenticated SQL route**.

To make this scene available inside the installed ChatGPT widget, the existing Site MCP app must expose a valid registered `ui://` resource and a bounded launch/view transport, then the ChatGPT host must successfully render it. The necessary authenticated Site backend editing surface was not available in this GitHub work. Do not substitute local smoke proof for a visible in-chat mount receipt.

## Source Canon

This candidate builds on `main` `8d1517eb38769b4a8da057677c8670489981af96` (Aramoor/WebGL work preserved) and reuses the optional Nightglass manuscript/tools from PR #547. PR #553 covers a **separate draft machine/SQL snapshot**, not a merged runtime. The new scene route is staged separately and does not assert #553 is merged, deployed or Crowned.

## Why this scope is small

The user should be able to open a world and have a conversation before another provider, GPU engine or firmware layer is introduced. This pass intentionally has **one visible original NPC** and a short, tested interaction. Godot's GL Compatibility renderer remains the existing web-safe fallback, rather than a forced Vulkan-only change.

**CAST: STOP. Public release, Android device verification, independent agent execution and promotion: unverified.**

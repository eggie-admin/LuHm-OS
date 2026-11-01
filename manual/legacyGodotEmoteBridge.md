# CAST: IPS byte decoder to Godot semantic emote bridge

This **synthetic, opt-in** source candidate follows PR #467's 32-byte IPS-to-SQL proof. `game/story/legacyIpsEmoteDemoV1.json` is a deterministic receipt from `tools/legacyIpsTextBridge.py`, checked by the existing Python test suite against the real synthetic fixture and exact three SHA-256 digests. The Godot adapter validates those same digests, flags, fixed dialogue IDs/offsets, allowed tokens, and exact one-emote change before any HUD write or event.

`scripts/main.gd::previewLegacyEmote()` loads the packaged synthetic JSON only when explicitly invoked, calls `scripts/game/legacyDialogueEmoteBridge.gd`, and renders `AB\nC\n[EMOTE: ANGRY]` in the **existing** GameHud. A typed `emote_requested("angry")` event is emitted without running a worker or changing the canonical First Night quest / existing Lum banter. Tokens are not code.

The existing gameplay-vertical-slice CI installs/checksums Godot 4.7.2, imports the live Main scene, and launches `tests/legacyGodotEmoteSmoke.gd` to verify actual Godot HUD text, semantic event delivery, and refusal of corrupted/unrecognized tokens. A successful run is **headless Linux Godot source/runtime smoke**, not physical Samsung or avatar blend-shape proof. `scripts/game/lumAvatar.gd` currently lacks a verified angry blend shape, so this bridge exposes a HUD label/event instead of falsely claiming animated angry facial geometry.

## Local repro

```bash
python3 -m unittest discover -s tests -p 'testLegacyIpsTextBridge.py' -v
python3 tools/gameplayVerticalSliceAudit.py
python3 tools/runGodotSmoke.py /path/to/verified/Godot_v4.7.2-stable_linux.x86_64 legacyGodotEmoteSmoke
```

No ROM, firmware, bootloader, signed APK, Android deployment, new package manager, remote API, auto-merge, or Crown.

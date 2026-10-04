# LuHm OS Android WebView Cockpit candidate

This candidate is the next layer above the proven native Godot 4 playable spine.

## Ownership

- **Godot 4** owns the Android activity/game lifecycle and the full-screen 3D canvas.
- **Android WebView** is an overlay glass layer, not the app authority.
- **jQuery + jQuery UI** own draggable/resizable cockpit windows and touch-friendly shell behavior.
- **Bootstrap** supplies layout primitives only.
- **Vue** is an isolated CMS/editor island. It does not replace the shell, Godot runtime, bridge, or authority model.
- **KAI 9000 / Ollama** are reached through narrow typed native requests. The WebView receives no shell, generic filesystem, eval, or arbitrary URL capability.
- **Lum + Oni mesh** remains bounded by the 2026-09-25 agent doctrine. Kanabo Gate is the deterministic executor.

## Layer stack

```text
z=20  jQuery UI windows / Vue CMS island
z=10  caged Android WebView
z=0   Godot 4 full-screen world / Lum / game canvas
```

The production WebView should load packaged cockpit assets through AndroidX `WebViewAssetLoader` at `https://appassets.androidplatform.net/...`. Do not use privileged `file://` shortcuts or arbitrary remote pages.

## Bridge contract

Allowlisted request types in the first pass:

- `chat.send`
- `panel.set`
- `status.request`
- `model.select`
- `cms.select`

Explicitly absent:

- generic `exec`
- shell commands
- arbitrary filesystem paths
- `eval`
- arbitrary URL navigation with bridge privileges

## Build order

1. Preserve the current Godot project and exact 4.7.2 Android build lane.
2. Stage local cockpit dependencies from a committed lockfile with `npm ci`.
3. Add a small Kotlin `KAIWebView` Android plugin using AndroidX WebKit / `WebViewAssetLoader`.
4. Overlay the WebView on the Godot activity while leaving transparent/touch-through world zones where intended.
5. Route only typed bridge messages into Godot/native KAI services.
6. Export ARM64 debug APK through the existing Android Gradle/Godot CI lane.
7. Verify package/version, signer, zipalign, SHA-256 and device smoke on the target Samsung.

## Current proof boundary

This commit is an interactive cockpit source candidate. It is **not** proof that the Android WebView plugin compiles, that an APK contains the overlay, or that device smoke passed. Those remain build gates.

The repository source law still applies: **AI proposes. Policy authorizes. CI proves. Human promotes.**

# LuHm Android Web3 Cockpit plugin source

This directory contains the source-only candidate for the Android System WebView cockpit bridge.

## Boundary

- Godot remains the native scene/game runtime.
- The Android plugin returns a full-screen WebView overlay from the Godot plugin lifecycle.
- Web content is packaged from `frontEnd/` into the plugin AAR.
- `WebViewAssetLoader` serves the cockpit under the HTTPS-like app-owned origin `https://appassets.androidplatform.net/assets/`.
- Requests outside that local origin are blocked instead of falling through to network.
- The JavaScript/native bridge uses origin-scoped `WebViewCompat.addWebMessageListener`.
- Only allowlisted message types are accepted.
- No `addJavascriptInterface`, arbitrary shell, remote content, signing, publication, release, or Crown authority is present.

## Build state

The plugin source is prepared but **no AAR has been built in this milestone mutation**. Building/staging the AAR and exporting an APK remain behind the Forge CAST gate and exact sourceRef proof.

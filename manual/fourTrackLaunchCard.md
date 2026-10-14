# LuHm OS · four-track launch card

Exact-source pipeline: `doctrine/fourTrackReleaseClosureV1.json`
Source-of-truth: `doctrine/currentSourceTruthV3.json`
Professor is the only promoter. No automatic Oni activation or production publication.

## Android, on a non-root Samsung

The historical ARM64 Android debug APK targets Android API 36 and uses package `art.eggiebagelface.luhmos.testing`. The artifact's SHA-256 is pinned in `doctrine/proposedAndroidCastEvidenceV1.json`. A screen recording showed LuHm-branded UI on Samsung but did **not** establish the installed APK's package identity. Never mark first-launch GREEN from that recording alone.

The quick native proof from an already-authorized, USB-debugging-enabled workstation is:

```bash
python3 tools/captureAndroidProof.py --capture --launch
```

This is optional non-root `adb` observation. It verifies the exact installed APK SHA-256 and version, then requests a foreground launch. It does **not** capture screenshots, collect device identity, root the phone, uninstall apps, or prove Godot touch interaction. The user still supplies the actual app-screen result separately. If ADB isn't enabled, the signed candidate remains available for normal Samsung Files install, subject to Android's explicit installation confirmation.

## ChatGPT cockpit and in-chat Godot

Existing read-only MCP endpoint: `https://luhm-os-harness-green.onrender.com/mcp`. The package advertises `luhm_open_cockpit` and `luhm_open_godot_player`; UI resources are `ui://luhm-os/cockpit-v2.html` and `ui://luhm-os/godot-player-v1.html`.

GitHub has `tools/inChatLiveMcpProbe.py` for HTTP MCP initialization, tool listing and UI-resource inspection. A valid external MCP reply is not proof that the plugin is installed in **this** ChatGPT conversation. That requires connection in the user's ChatGPT Plugins settings plus a successful actual tool invocation and mounted UI in this conversation. Host-side permission and installation cannot be faked by GitHub.

The Godot view is hosted on an existing Render origin. The in-chat UI resource already allowlists that origin via `_meta.ui.csp.frameDomains`. Host acceptance and iframe/WebGL/touch must be tested separately.

## Playable Godot Web

Use the existing `.github/workflows/godot-web-harness.yml` only with explicit exact-source Professor CAST. It compiles verified Godot Web HTML/WASM/PCK and now runs `tools/godotBrowserSmoke.py` for integrity, browser canvas, dispatched keyboard inputs and a screenshot. Chromium canvas proof is narrower than a completed interactive quest or actual Samsung touch proof. No automatic Godot build is triggered by a source-only PR.

## Stable public F-Droid distribution

An independent F-Droid binary repository is supported. The release path is:

1. Professor creates and retains the long-lived Android **release** signing key in owner-controlled secure storage, distinct from the disposable debug signer, and separately creates the **repository index** signing key.
2. Build a non-debug, stable-signed APK under the fixed application ID, with monotonic versionCode and Android target API 36. Verify signatures and hashes independently; test upgrades and rollback on a device.
3. Use `tools/publicDistributionGate.py --apk <release.apk> --candidate <receipt.json>` as a fail-closed **preflight only**. Never put either private signing key in GitHub, the ChatGPT prompt, or the APK.
4. On the owner-controlled signer machine initialize F-Droid tools with `fdroid init`, put the **signed release** APK in its `repo/` directory, run `fdroid update`, verify the signed index and fingerprint, and deploy only the public repo artifacts to reviewed HTTPS hosting.
5. Add the resulting public repo URL/fingerprint to the install portal after live HTTPS verification and Professor sign-off. F-Droid then guides installation/updates from that signed repository. A debug APK and a private Google Drive link are **not** substitutes for production distribution.

Official references: `https://f-droid.org/docs/Setup_an_F-Droid_App_Repo/` and `https://f-droid.org/docs/Signing_Process/`.

## Release truth

`SOURCE GREEN` means the contracts and their tests pass. `RENDER LIVE` means the exact server commit deployed. `DEVICE GREEN`, `HOST GREEN`, `GODOT PLAYABLE` and `PUBLIC GREEN` each need **different, independently observed receipts**. A finished source milestone must never falsely roll those up into one GREEN.

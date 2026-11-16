# LuHm-OS · Project Premonition / Neon Cathedral tablet POC

Prototype-only original neon-goth character portrait and existing horned-L brand geometry. The image is an original generated concept made for this test; not a final or owner-approved rig. Tiny preview image is deliberately 128×192 WebP to keep the tablet download light, and can be replaced for later mutation.

**Isolated Android application ID:** art.eggiebagelface.luhmos.premonitionpoc. The test app is distinct from .testing, .canongallery and .aramoorplaytest. Android SDK 36 / arm64-v8a, no internet permission. Existing Godot 4.7.2 Aramoor, Nightglass and Web3 bridge are preserved.

## Install

Open a successful run of **Premonition Neon Cathedral · tablet ARM64 debug-signed POC APK** in GitHub Actions and download `premonition-neon-cathedral-arm64-debug-install` artifact ZIP. Extract `Aramoor-Samsung-arm64-test.apk`, verify with `apk-sha256.txt`, then install the APK from the tablet's file manager. Android may ask you to permit this file manager to install apps. Do not change bootloader or firmware.

**Debug signing:** a disposable per-run Android testing keystore is created in isolated CI, then destroyed. `apksigner verify`, signer SHA-256, Android package name, 16KB zip alignment, ARM64 ABI and bundled art hash are verified. This is a valid debug-signed APK, NOT an owner-persistent release-signed APK or a supported update identity. If the exact POC app package is already installed from a different run, Android can reject the update because signers differ. Do not remove old app data without a deliberate owner decision.

## Proof checklist

Confirm initial LuHm-OS / PROJECT PREMONITION splash with original portrait, touch **PLAY ARAMOOR**, see Godot world, move your character with tablet controls, return to Cathedral, open Canon Gallery, and capture a private screen recording. Physical tablet proof is pending until actually performed.

GitHub Actions artifact is temporary; it is not a production release or an automatically updating installer. SQL agents and firmware remain offline. Crown STOP.

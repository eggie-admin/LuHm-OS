# LuHm-OS: Project Premonition | Hostile 4×4 Mod Forge field notes

**State:** candidate source-only on draft PR #492. Zero device scans, display servers launched, network requests, mod downloads, ROM reads, game patches or git forks. This inventory guides one independent creative game/studio, not an attempt to package every upstream vendor.

## R1–R4 for four source lanes

| Concern lane | R1: source rights | R2: hostile inputs | R3: ephemeral fixture | R4: owner escalation |
| --- | --- | --- | --- | --- |
| Host/display | Observe real Linux/Android/iOS/VM capabilities. Preserve host kernel. | Strict eight-variable `LUHM_*` plan. Reject inherited `DISPLAY`, loader/env overrides and unknown keys supplied by plugin manifests. | Headless/Wayland plan only. Do not create X11/Xwayland services in CI. | Choose real host, renderer and rollback before installation. |
| Device/debug | Audit OEM hardware and app permissions. USB/BT interfaces belong to OS and user. | Parse USB vendor/product as lowercase `0000`–`ffff` and Bluetooth 128-bit service UUID; no MAC or serial storage. | Mock read-only device identities. No usb detach, Bluetooth pairing, camera/mic activation, or kernel logs. | User-initiated permission and per-device proof. |
| Studio/mods | Inventory Blender, GIMP, Godot, ReShade, Nexus assets, BodySlide, SDL and their actual licenses. | Treat mod files, node graphs, shaders, plugins, INI, DLL and Python scripts as hostile until inspected. | Synthetic shader/content/patch *metadata* only. Standalone programs and isolated importers, not an app full of mod loaders. | Owner rights, publisher permissions, source revision, isolated sandbox and compatibility smoke. |
| Rights/source | GitHub owns code/diff/provenance, not binary archive or third-party IP. | Untrusted license and asset provenance claims can never auto-approve. | Synthetic homebrew IPS/BPS/PPF patch metadata with fixed SHA-256 and bounded hexadecimal offset; no original game data. | Rights review before any public patch/source/asset distribution. |

Canonical candidate: `doctrine/hostileModForge4x4V1.json`; offline validator: `tools/hostileModForgeAudit.py`; dedicated regression: `tests/testHostileModForge.py`.

## The anti-X11 approach that actually works

**Default to headless processing, then Wayland when a local desktop is necessary.** Use the host kernel and native drivers; on an existing Linux kiosk consider Weston headless or a properly authorized Wayland compositor. Weston supports `headless` and `drm` backends. Xwayland can still be required for selected older games and windows; it must be an *optional isolated compatibility mode*, not a global OS dependency. Valve's gamescope itself may run Xwayland for legacy applications, so claiming pure Wayland across all game engines would be incorrect.

**Do not** expose display sockets over the web, inject `DISPLAY`/`LD_PRELOAD` from plugin manifests, install root-level Xorg, enumerate monitors, or replace Android/iOS compositor/driver paths. The generic phone/browser client requires no local X11 runtime.

Official references: https://wayland.pages.freedesktop.org/weston/toc/running-weston.html and https://github.com/ValveSoftware/gamescope.

## Minimal config registry

The only accepted source-proposed environment variables are `LUHM_STAGE`, `LUHM_DISPLAY_BACKEND`, `LUHM_RENDER_ENGINE`, `LUHM_INPUT_MODE`, `LUHM_USB_ENABLED`, `LUHM_BLUETOOTH_ENABLED`, `LUHM_DEBUG_PROFILE`, and `LUHM_VENDOR_MODE`. Default is `proposed / headless / software / noDevice / off / off / off / metadataOnly`.

This is a **strict parser for untrusted proposed flags**, not a rewrite of the actual machine environment. Approved production host secrets are controlled separately and never accepted from donor manifests. `LUHM_USB_ENABLED=readOnly` or `LUHM_BLUETOOTH_ENABLED=readOnly` merely requests future permission checks. It does not prove a physical device, open a USB descriptor, scan radio addresses, detach drivers or grant mic/camera permission.

Structured debug receipts contain bounded class/status fields and digests. Do not copy raw USB serial numbers, Bluetooth MAC addresses, audio capture, security tokens, private file paths, ROM data, secrets or kernel logs into a public ChatGPT MCP route. Hashing a low-entropy vendor/product pair is only a stable label, not anonymity or authenticated identity.

## Sanest community tool adoption

Keep the existing Godot editor/scene import and Blender/GIMP asset creation. Original `.blend`, SVG and GIMP masters remain private, while rights-approved glTF 2.0/GLB, images and shaders enter Godot and the small mobile client via the existing asset intake. Preserve `host/api/premonitionAssetLedgerV1.sql` as **metadata-only** and the private file server as the authoritative binary store.

Prefer upstream *interfaces and design ideas* over importing full applications:
- **Godot** is MIT-licensed; SDL 2+/3 is zlib; ReShade is BSD-3-Clause, but Windows injector DLL and shader packs are **not** drop-in Android engine code.
- **Blender** is GPL 2-or-later for its main code; **GIMP** GPLv3-or-later; **BodySlide/Outfit Studio** GPLv3+. Use them as independent, user-controlled creative tools; do not claim their source Apache-2.0.
- **FFmpeg** generally LGPL 2.1+, with GPL and other licensing affected by compiled options; inventory actual build `ffmpeg -buildconf` before redistributing a binary.
- **BlueZ** is Linux-specific Bluetooth stack; **libusb** is LGPL 2.1+. Use only OS-permitted adapters. Android/iOS have their own sanctioned device APIs.
- **Nexus Mods** author permissions are file-specific. Absent permission, seek it. Their content and APIs are not a generic free code/asset mining service. Do not scrape, mass-download, mirror, or transplant proprietary Bethesda/Paradox game assets.
- **RetroArch** is GPLv3 but its libretro API is MIT and individual cores vary, sometimes noncommercial; isolate compatibility research by core. **PCSX2** is GPLv3+. Current **DuckStation** source has CC-BY-NC-ND restrictions on modified redistribution; do not create a public modified fork just because it is hosted on GitHub.

Research sources:
https://godotengine.org/license/
https://www.libsdl.org/license.php
https://github.com/crosire/reshade
https://www.blender.org/about/license/
https://www.gimp.org/docs/userfaq.html
https://ffmpeg.org/legal.html
https://help.nexusmods.com/article/28-file-submission-guidelines
https://github.com/ousnius/BodySlide-and-Outfit-Studio
https://bluez.github.io/
https://github.com/libusb/libusb
https://docs.libretro.com/development/licenses/
https://pcsx2.net/intellectualproperty/
https://github.com/stenzek/duckstation

### Creative Commons and Apache-2.0 are different lanes

The repository root **currently uses GPLv3**. No automatic blanket Apache-2.0 conversion is possible. Apache-2.0, MIT, BSD, and zlib can be good choices for independently authored modules *with verified rights*. Apache-2.0 components can flow into a GPLv3 combined program with obligations, but the reverse direction is not a blanket relicensing right.

Use **CC0 or CC BY 4.0** for suitable, actually authorized *art* when provenance and attribution are checked; CC BY requires credit, license link and a change notice. NC/ND restrict commercial or adapted redistribution. **Creative Commons itself advises against CC licensing for ordinary software code**. Keep per-asset notices, shader attribution, original author consent and private/public flags. A mod being old, delisted or called 'abandonware' does **not** terminate copyright.

References: https://apache.org/licenses/GPL-compatibility.html
https://creativecommons.org/faq/
https://creativecommons.org/licenses/by/4.0/

## Original game vision, not a game clone

Prototype **one** original compact 3D vignette in Godot: gothic character customization, an outfit slider/rigged avatar *we own*, a simple combat-state machine and a tiny data-driven faction/resource overlay. Code Vein's atmospheric character-action design and Stellaris's systems-level modularity are **inspirations**, not licensed sources of characters, textures, mods, audio, factions or game logic. Stage simple original shader effects in Godot's built-in shader language rather than installing ReShade's game-injection runtime.

PS1/PS2 support stays an independent optional preservation/research lane. For ROM translation and hex patch experiments, use original public-domain/homebrew programs or material with **explicit rights**. Capture a manifest with source SHA, input/output SHA-256, patch SHA-256 and bounded `0x...` offset. Never commit or download a proprietary ROM/BIOS/ISO, distribute title assets, bypass copy protection, patch an online game without authorization, or republish someone else's translation. The source-only helper validates these fields and performs no byte patching or emulation.

**Next physical gate:** prove an actual permitted USB/BT device read-only with model info held privately, then a Godot build and real Android tablet install, plus optional isolated headless Linux renderer. No distributed game, mod, ISO, cloud worker, company-agent resume, paid spend or production release is authorized by this pass.

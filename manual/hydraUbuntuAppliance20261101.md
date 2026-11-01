# Hydra Ubuntu creative appliance · proposed reference architecture

Source-only blueprint; **not** a built Ubuntu image, flashed bootloader, running kernel, or installed kiosk.

## Product decision
LuHm-OS is one app with an Ubuntu-derived supported base, not a greenfield kernel rewrite. Keep the base kernel, firmware, Secure Boot, AppArmor, drivers, and unattended security-updates with the operating system vendor. Put the brand and behavior in an unprivileged LuHm package and versioned assets, not firmware patches.

## Four planes
1. **Hardware/kernel:** record exact Ubuntu release, kernel, CPU/GPU/driver/firmware identity and owner recovery medium. Kernel health is proved only on the real target.
2. **Headless:** Python 3 MCP/API and SQLite metadata via supervised, least-privilege service. FFmpeg/Blender/Godot headless jobs start only on demand. No X11, kiosk or NGINX needed for an API process unless a real use case proves otherwise.
3. **Web GUI:** static local HTML/CSS plus bundled jQuery/jQuery UI, one Chromium-compatible kiosk/browser entry point when a display exists, strict CSP, touchscreen, keyboard escape and offline fallback. Android uses the same GUI assets with the existing native WebView app; it is not an Ubuntu kernel on Samsung.
4. **Game/media/AI:** separately pinned Godot 4 Web export and editable scene sources; standard HTML5 audio/video, optional rights-cleared VLC desktop/libVLC adapter, FFmpeg renders, bounded provider adapters under Professor approval.

## Hydra failover law
The motif means resilience **without runaway duplication**. Keep one active process, two *replacement paths* (same-version restart and known-good rollback), two bounded attempts per five-minute window, explicit 5s/30s backoff, and fail closed on repeated failure. Do not promote standby status from a health ping alone. Do not spawn extra AI workers, grant root, disable AppArmor or publish assets after an error.

## Acceptance order
- **Source:** exact-head CI, manifests, negative tests, dependency and license scan. CI does not prove a running Ubuntu kernel.
- **Host prototype:** owner-provided Ubuntu test machine or VM; record distro/kernel/GPU, service UID, loopback API health, browser document and boot logs.
- **Creative slice:** Godot actual scene and input, licensed media open/play/seek, FFmpeg worker receipt, jQuery touch interactions and rollback.
- **One-app kiosk:** boot to GUI, disconnect network, terminate primary once and verify finite recovery, escape back to desktop, upgrade/rollback without lost original art.
- **Promote:** repeat on real target and sign/publish only on an independently authorized release.

No production VM, disk, network or signing operations are authorized by this source document.

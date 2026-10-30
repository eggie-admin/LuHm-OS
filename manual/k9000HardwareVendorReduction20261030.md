# K9000 Crown Cathedral | Hardware-only vendor reduction / universal headless spine

**2026-10-30 | source candidate only | Crown STOP | 15-agent execution quarantine preserved**

## Result
One human-facing `LuHm-OS: Crown Cathedral` cockpit, platform-specific native hardware adapters, a Python 3 standard-library *headless capability core*, optional SQLite storage, and optional cloud/model adapters. The current protected-main Google/OpenAI compatibility precedence remains unchanged: proposing a **local-first data plane with optional OpenAI compatibility** is **not** an automatic Crown-approved reversal of canonical provider priority.

Do not conflate model compatibility with rights. Google LiteRT-LM supports embedded execution on Android/iOS/Linux; **Edge Gallery is the independent showcase**, not a proven headless IPC server. Llama weights have Meta-specific terms and may not be assumed OSI-open-source or shipped in F-Droid. Only embed an exact model after provenance, license, format, RAM/latency and device proof.

## Hardware truth and driver readiness
The private hardware canon remains the equipment source of truth, identified in public source by title only. New user-described devices:
- **Yeti microphone:** exact manufacturer/model, USB connector/firmware, USB Audio Class descriptors and Linux kernel module unproven. Try the ALSA `snd_usb_audio` route with PipeWire + WirePlumber; require real input sample and safe playback comparison before GREEN.
- **Bluetooth audio jack:** 3.5-mm transmitter, receiver, DAC, adapter, codec role and pair state unknown. Try Linux BlueZ + PipeWire/WirePlumber only after the exact device is identified. Capture/monitor duplex mode requires separate tests.
- Existing Altec Lansing HydraMotion 2.0 Bluetooth audio remains a **separate, known inventory entry**. Do not silently combine it with the new jack device.
- **Logitech C930e:** UVC/V4L2 candidate, real frame acquisition unverified.
- **Nikon COOLPIX B500:** media ingest. Neither direct USB webcam nor live HDMI capture is proven.
- **Epson Perfection V39 II:** scan/archive, SANE **exact backend and firmware** must be tested; do not substitute older V39 driver claims.
- Samsung Tab S10 Lite and S24 FE use stock vendor Android, not Linux kernel replacement. Galaxy Tab A8 is a separate companion screen.
- **iPhone:** no exact owned iPhone model/physical QA receipt; Godot iOS requires macOS/Xcode and separate native Apple permissions.

No kernel, bootloader, GParted, Android firmware, package installation, permissions, pairings or scanner motors were changed.

## Runtime division and vendor-fat decisions
| Tier | Required | Optional or separate | Never a default headless requirement |
|---|---|---|---|
| Linux control | Python 3 stdlib, loopback, schema-validated JSON | SQLite in memory/local user-private DB | desktop, Node runtime, Nginx, MariaDB daemon, GParted |
| Android | Godot + local WebView + typed Android bridge | LiteRT-LM, USB UVC adapter on consent, Google Play connector | Python server in APK, Linux distro, admin SQL |
| iOS | Godot iOS/WKWebView/AVFoundation candidate | Swift LiteRT-LM after proof, App Store auth | Android USB APIs or Samsung drivers |
| Studio | opt-in Godot, Blender, FFmpeg, SANE, PipeWire | MariaDB local socket only if justified | public SQL ports or unnecessary services |

**Google audit:** Gmail/Docs/Drive/Cloud/Gemini/Play Store/Edge Gallery/LiteRT-LM are **eight distinct capabilities**, not a single Google account sign-in. Drive is readable from the connected ChatGPT context; no K9000 app OAuth token or Google Cloud IAM, billing, API key, Play Console or Gemini execution has been proved. No automatic Google calls occur.

**OpenAI audit:** optional host-only Responses API adapter. This user request proposes OpenAI as a **secondary** compatibility path to local/offline operation; existing `currentSourceTruthV3.json#activeCompatibilityOrder` still names ChatGPT/OpenAI first. Both facts are retained. Do not claim a provider-order doctrine promotion without review.

## Headless verification on CI
```sh
python3 tools/k9000UniversalHardwareAudit.py
python3 host/api/k9000HeadlessCore.py --smoke
python3 -m unittest tests/testK9000UniversalHardware.py tests/testTypedSqlStub.py tests/testFnCastSqlJson.py -v
python3 tools/architectureRhythmAudit.py
python3 tools/escalationKernelAudit.py
python3 tools/vendorReductionAudit.py
python3 tools/k9000LocalDriverProbe.py
```
`k9000HeadlessCore.py --serve --port 8789` binds **127.0.0.1 only**. Routes are GET-only `/healthz`, `/v1/capabilities`, `/v1/hardware`, `/v1/providers`. There is no inference, pairing, scanning, driver write, SQL endpoint, CORS, authentication/remote bind or actual app-to-service transport. The server is a tested local capability stub and must **not** be placed behind a public reverse proxy without a separate authenticated design/review.

## Physical readiness process on the Linux Mint host (operator-controlled, no root)
```sh
python3 tools/k9000HostReadiness.py
python3 tools/k9000LocalDriverProbe.py --inspect
```
These commands report only command presence and whether read-only enumeration returned successfully, **not raw MAC addresses, private serials, or recorded audio**. A detected module or attached device is *not* a working driver. Separate permission-aware local tests must record input audio sample/latency, actual Bluetooth routing, UVC frames, a successful scanner scan, reconnect behavior, and expected failure modes. Run `lsusb`, `arecord -l`, `wpctl status`, `bluetoothctl devices`, `v4l2-ctl --list-devices`, `scanimage -L` interactively only when needed; do not paste serial/MAC data into public logs.

## 4×4 authority and implementation
Canonical **columns** (package composition): core library, plugin extension, widget/class organization, typed stub/adapters.
Four **integration rows**: hardware/drivers; headless database; provider + native bridge; voice + cockpit. These rows do NOT replace canonical architecture tiers or the four escalation levels.
Four-beat **control loop**: Hear → Resolve → Act → Verify. Escalation tiers 0–3 remain independent and only move on actual evidence. Quarantined roles do not act as autonomous workers.

**Remaining gates:** physical Linux hardware/driver smoke; camera and mic permissions; iOS Mac build and device; native LiteRT-LM integration and model rights; live OpenAI/Google OAuth credentials; complete real APK/DMG and F-Droid release proof. Public/secret-bearing uploads remain blocked.

Official references: https://ubuntu.com/project/docs/release-team/list-of-releases/ ; https://developers.google.com/edge/litert-lm/overview ; https://docs.godotengine.org/en/4.7/tutorials/export/exporting_for_ios.html ; https://pipewire.pages.freedesktop.org/wireplumber/daemon/configuration/bluetooth.html

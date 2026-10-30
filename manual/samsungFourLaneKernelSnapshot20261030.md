# Samsung-first kernel-to-Studio Forge snapshot | October 30, 2026

**Candidate, not deployed.** 4 release tracks, 4 system layers, 4 escalation tiers remain distinct. No firmware, GRUB, GParted, OS upgrade, tablet, cloud VM, DNS or paid-provider action taken. Protected main remains unchanged. Crown STOP.

## Outcome and exact-source target

The next proof is a controlled Samsung app benchmark and a single synthetic Blender motion-capture project on the Linux studio, **not** an overclock/firmware write or an unbounded AI provider integration.

Existing source baseline: draft #452 Apache/vendor ZIP→Java Gradle, stacked above #451 four-source forge, #450 DEV/npm/DMG/APK, #449 Kernel VM500 and #448 Kai Blender. Existing 15 agent routes remain QUARANTINED. User-owned physical devices have no remotely observed runtime receipt in this mutation.

## Four release tracks, not privilege tiers

| Track | Platform | Testing purpose | Allowed change |
| --- | --- | --- | --- |
| **PROPOSED** | Ubuntu 26.10 (released Oct 15, 2026), dev Chromium/Chrome Canary, experimental APIs | ABI breakage, disposable development test | Source and isolated guest only |
| **DATA/BETA** | Chrome Beta, Firefox Beta, vendor-eligible One UI Beta | Metrics collection, feature regressions and explicit physical recovery | Source/CI first; no Samsung beta enrollment or install from here |
| **LTS** | Ubuntu 26.04.1 LTS (released Aug 27, 2026), stable Samsung OTA / browser | Reproducible build and rollback baseline | Current stock kernel preserved; Ubuntu upgrade NOT authorized |
| **STUDIO FORGE** | Current Linux Mint 22.3 Zena, Core i9-12900K | Blender, optional paid AI, 6× webcam capture and Godot/FFmpeg | No host kernel/firmware change; source-only tool and model research |

All profiles are defined in `infra/four-lane/samsung-kernel-profiles.yaml` with `firmware: DENY`, `install: false`, and `deviceAuthority: NONE`. These tracks do not rewrite the canonical 0-3 escalation model, 4/4 Hear-Resolve-Act-Verify, or the four software composition layers.

## Samsung inventory and firmware boundaries

- Galaxy S24 FE **SM-S721U1**: possible DeX phone role, but check exact One UI version, hardware and route before asserting it works. Samsung states DeX *on PC* is not supported for devices updated to One UI 7/Android 15 or later; Linux and ChromeOS PCs are not supported for DeX on PC.
- Galaxy Tab S10 Lite **SM-X400**: explicitly **no standalone DeX, Wireless DeX or HDMI output** according to Samsung; use the DeX-*inspired* HTML5 K9000 cockpit.
- Galaxy Tab A8 **SM-X200**: optional companion UI, not pooled GPU/rendering capacity and no assumed native DeX.
- Beta availability depends on device, carrier/region and enrollment. Official flow uses Samsung Members then Settings > Software update, after Smart Switch backup. Beta rollback via Smart Switch can reset data. **No automatic firmware download/flash or bootloader unlock is permitted.**
- Benchmark plan on each authorized test device: Android Macrobenchmark cold-start TTID/TTFD, frame timing p50/p95, jank, memory, temperature/battery, UI interactions and USB descriptor enumeration. Compare matched ambient temperature, charging state, battery level, app/build SHA and release channel. A GitHub runner cannot produce credible Samsung device numbers.
- Android baseline should use stock firmware, verified boot and app-layer permission APIs. Shizuku/ADB remains separate, opt-in development testing, not an implicit system-root backdoor or F-Droid requirement.

## Workstation firmware to kernel to compositor

1. **BIOS/UEFI:** Intel Core i9-12900K has 8P+8E (16 cores, 24 threads), UHD Graphics 770 listed in the CPU SKU. It **does not carry a Core Ultra NPU**. Test OpenVINO **CPU** first, and GPU only after verified graphics drivers. No invented NPU or local GPU installed proof.
2. **Exact motherboard:** neither ASRock nor ASUS board model/BIOS revision is verified. The vendors' official update tools are model-specific; do not offer an unattended universal flash command. `fwupdmgr get-devices` / `get-updates` can be considered only on the physical workstation after approval and sensitive outputs are redacted. Do not run `fwupdmgr update` via ChatGPT or CI.
3. **GRUB / GParted:** inspect signed boot state and backed-up boot entries before any OS migration; bootloader variables and disk partitions are protected. `lsblk` and read-only diagnostics are the first pass, no `grub-install`, `grub-editenv set`, `update-grub`, `sgdisk`, partition resize or GParted mutation from this candidate.
4. **GDM:** GNOME Display Manager is a local-seat display/login manager, not a dependency for headless Blender. Current Mint may use another manager; do not replace it. Headless Blender uses explicit user-owned background jobs, systemd/containers only after actual host proof.
5. **Damn Small Linux:** official DSL 2024 RC7 is a lightweight 32-bit-compatible antiX/Debian derivative intended for low-spec x86. Its cited June 8, 2024 RC status means it is **sandbox-only research**, not the chosen 2026 security baseline or a Samsung/Raspberry flash target.
6. **APT/dpkg and firmware:** pin distro package versions and preserve signed apt sources. Apache-only licensing is impossible for whole Debian/Ubuntu/Samsung/AOSP stacks; Blender is GPL-family, Godot MIT and FFmpeg build-license-dependent. Current repository GPL-3.0 terms remain intact.

## Six-camera studio motion capture

- **Capture host:** Linux Mint workstation first, not the free-tier remote VM and not the Samsung Lite USB hub as the primary synchronized capture system.
- **Enumeration:** powered USB hubs, USB2/USB3 host controller layout, UVC V4L2 driver, privacy/permission and stable device aliases. Exact camera models and hub topology beyond canonical Logitech candidate are unverified.
- **Timing:** aim for six simultaneous stable streams with documented resolution/FPS, bounded CPU/thermal use, monotonic frame PTS, p95 inter-frame jitter and coarse visual flash synchronization. Need a hardware sync strategy for accurate mocap; consumer webcams aren't inherently genlocked.
- **Calibration:** ChArUco/checkerboard intrinsics and extrinsics, per-camera lens distortion, synchronized markers or LED, human pose inference with consent, Blender armature retarget, Godot GLB import. No capture or pose model has been installed.
- **Implemented source:** `tools/sixCamTimingAudit.py` analyzes **caller-provided numeric timestamp lists** for jitter and startup sync spread, with no camera access. Synthetic positive controls don't prove hardware, real media rights or retargeting quality.

## Blender Forge and one app

- K9000 Studio / Android WebView / ChatGPT-facing MCP are **one logical project** with separate native adapters. Bridge must be origin-checked, typed, consented and reject unsupported commands.
- Python 3 + SQLite STRICT/JSON1 remain the bounded local manifest/evidence path. Base64url with a 44 KiB ceiling is **encoding, not encryption or a worker credential**. Base44 is a separate optional external product, not an encoding.
- Remote Oracle/Google VM can run authenticated lightweight Python services and limited Blender jobs only after real quota, benchmark, secret storage, TLS, and backup evidence. A paid GPU or heavy workstation workflow requires an explicit spend cap, not an assumed free-tier entitlement.
- GitHub DEV/npm/DMG/APK stay independently audited; experimental track versions are not implicitly allowed to replace accepted locked production dependencies. Legal asset/license review precedes public package distribution.
- The combined Lum coordinator remains a *supervised routing design*. No daemon, hidden agent mesh, multi-agent activation or autonomous firmware tool authority.

## Honesty in the 500-slot CAST bridge

`tools/samsungCast500Audit.py` defines **100 unique controls**, 25 in each of firmware/boot, OS/drivers, AI/media and forge/release. It applies them to **five targets** (three Samsung devices, studio Linux host, disposable GitHub runner), resulting in **500 unique target-scoped evidence slots**. A CI runner can report only a handful of its own observed conditions; it cannot claim 500 real hardware passes or that any Samsung firmware was read.

A separate set of source-law checks verifies models, blocked firmware/boot writes, YAML four tracks, realistic Intel/DeX/6-camera claims, licensing and agent quarantine. Passing these means **source green**, not installed firmware/device/runtime green. The earlier Kernel VM500 and Titan 500 source audits remain separate artifacts.

## Field runbook

```bash
# Inside reviewed candidate checkout only; no root or hardware mutation:
python3 tools/samsungCast500Audit.py --runner --output build/samsung500-source.json
python3 -m unittest tests/testSamsungCast500.py -v
python3 tools/sixCamTimingAudit.py
python3 tools/k9000LocalDriverProbe.py
```

For physical performance testing, first capture device model/OS/build fingerprint locally with private redaction; then use Android Studio Macrobenchmark on an authorized stock device and report the actual benchmark result JSON for comparison. Do not send serials, IMEI, MAC addresses or firmware keys to CI.

## Primary official references (checked 2026-10-30)

- Samsung DeX: https://www.samsung.com/us/support/answer/ANS10001972/
- Samsung tablet DeX: https://www.samsung.com/us/support/answer/ANS10003426/
- One UI Beta and backup: https://developer.samsung.com/one-ui-beta
- Ubuntu releases: https://ubuntu.com/project/docs/release-team/list-of-releases/
- Intel 12900K: https://www.intel.com/content/www/us/en/products/sku/134599/intel-core-i912900k-processor-30m-cache-up-to-5-20-ghz/specifications.html
- OpenVINO 2026 requirements: https://docs.openvino.ai/2026/about-openvino/release-notes-openvino/system-requirements.html
- ASRock UEFI: https://www.asrock.com/support/BIOSIG.asp
- ASUS UEFI: https://www.asus.com/us/support/faq/1008279/
- GNU GRUB 2.14: https://www.gnu.org/software/grub/manual/grub/grub.html
- GNU Parted: https://www.gnu.org/software/parted/manual/
- DSL 2024 RC7: https://damnsmalllinux.org/2024-download.html
- Android Macrobenchmark: https://developer.android.com/topic/performance/benchmarking/macrobenchmark-overview
- fwupd: https://github.com/fwupd/fwupd

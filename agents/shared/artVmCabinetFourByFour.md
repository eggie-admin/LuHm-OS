# Art VM Cabinet 4×4 | shared skill review rubric

**Contract:** `doctrine/artVmCabinetFourByFourV1.json`  
**State:** Proposed source guidance only; no provider worker is activated. `doctrine/companyWideOperationalQuarantineV1.json` remains authoritative.

## Four platform surfaces, four boundaries
For each Google VM, Android/Samsung, Apple iOS/iPadOS, and open-source Linux request, inspect exactly: **firmware/boot → guest/host execution → art workflow → client handoff**. Assign logical `0x00..0x0F` index labels; these are not BIOS offsets, registers, PCI IDs, cache lines, native page sizes, or execution permissions.

- **Google VM:** Provider-managed firmware and host kernel. CPU-only virtual display does not prove hardware graphics. GPU VM use requires an explicit cost gate and real acceleration receipt. No new paid resources by default.
- **Android/Samsung:** OEM Android Verified Boot/Knox and GKI/KMI contracts stay intact. An APK is not a distro VM, GRUB image, or permission to load drivers. Require real ABI, permissions, GLES/Vulkan capability, 16 KiB native alignment where relevant, signing and device install evidence.
- **Apple iOS/iPadOS:** Sandboxed client or approved native app, not a general purpose virtualized Linux guest. Apple's macOS Virtualization.framework is a **host macOS facility**, not evidence that iOS permits an arbitrary guest VM.
- **Linux:** Guest toolchain may contain Python 3, in-memory SQLite, Godot, Blender, FFmpeg and HTML UI. Reuse distro-supported kernel and host-approved GPU; do not change GRUB, GParted, module load, partition, driver or firmware from source CI.

## Common thread: typed art packets
`artwork intent → explicit rights/source identity → bounded JSON → Python 3 source tools → typed SQLite receipt → optional Godot/Blender/FFmpeg draft → SHA-256 evidence → human review`.

HTML, CSS and JavaScript are the portable **UI**, not the hardware boundary. Registry means a scoped source-contract inventory, not the Windows registry or physical device enumeration. SHA-256 is **integrity**, not a signature or authorization. A Git sourceRef of 40 hexadecimal characters must never be mistaken for a 64-character SHA-256 payload digest. Normalize and measure UTF-8 by byte length before serializing. Do not store original private media bytes or secrets in public GitHub.

## Sharpen each role, never multiply workers
- **Lum:** Confirm taskId, exact sourceRef, scopeId, target surface, authority, lowest-cost available path, stop conditions; route no more than three distinct support responsibilities. Never claim a worker was actually invoked based on a skill file.
- **Urd:** Review failed steps and warnings, classify historical versus current, create a reproducing negative test and smallest reversible repair. STOP on contradicted evidence, signing, privileged drivers or unknown actual device.
- **Belldandy:** Keep time-ordered source/reference + warning + rights + hash ledger; retain original artist masters. Never rewrite unknown as green or overwrite an original.
- **Skuld:** Research official current platform VM/kernel/ABI docs; differentiate Apple's macOS VM API from iOS app sandbox, and Android GKI vendor KMI from Linux host driver. State support dates and uncertainty.
- **Yume:** Start with private concept/storyboard/asset manifest; verify ownership, media formats, editable sources and target render environment. Prefer CPU rendering fallback and actual preview evidence over imaginary GPU availability.

## Warning and escalation policy
Read current PR exact-head Actions outcomes **before** drawing conclusions from historic runs. Historical failures are learning cases, not proof of current failures or of repair unless exact-head negative checks are green. Test unsupported startup directives, malformed schema keys, Git SHA versus SHA-256 length mix-ups and workflow commit budgets. Do not echo workflow secrets, raw credentials or private donor assets in receipts.

Escalation is **0 → 2×2 → 4×4 → 8×8 → 16×16** only where independently verified. Four source routes are not four physical kernels. Source-only green is not runtime green. Stop when a missing proof gate cannot be satisfied without changing firmware, unlocking bootloaders, starting paid cloud compute, reconfiguring host networking or shipping to the public.

## Standard compact packet
```json
{"taskId":"...","sourceRef":"40 lowercase git hex or UNKNOWN","scopeId":"...",
"surface":"googleVm|androidSamsung|appleIos|openLinux",
"input":{"utf8Bytes":0,"rightsState":"UNKNOWN"},
"candidate":{"language":"python3|json|html|js|sqlite","assetHash":"UNKNOWN"},
"verification":{"source":"UNKNOWN","runtime":"UNVERIFIED","physicalDevice":"UNVERIFIED"},
"warnings":[],"nextGate":"HUMAN_REVIEW","crownStatus":"STOP"}
```

No roster unquarantine, SDK entitlement change, paid API, merge, release signing, or publication is implied by this shared skill. **AI proposes. Policy authorizes. CI proves. Human promotes.**

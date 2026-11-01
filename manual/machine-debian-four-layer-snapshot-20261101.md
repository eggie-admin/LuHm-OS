# LuHm-OS | One Debian machine, four layers · 2026-11-01

**Status: PROPOSED, SOURCE-ONLY.** Owner: Professor. Backend is a hypothetical Debian 13 (Trixie) **host**, not a newly built operating system or a compiled custom Linux kernel. The repository's existing GitHub Codespaces devcontainer is Ubuntu 26.04 and shares its host kernel. Keep it working; do not make its Dockerfile pretend to install a kernel.

## The machine-only four-by-four

| Hex | Layer | Inventory | Bound | Verify | Propose |
| --- | --- | --- | --- | --- | --- |
| **0x00–03** | Kernel | Host ISA, distro kernel and CPU/page size | Secure Boot/driver/module authority | Kconfig/driver/firmware receipts from real owner-approved host | Review configuration delta, not blind fork |
| **0x04–07** | System | Debian 13, Python 3, SQLite, Git | Minimal userspace, no listeners | Python and SQLite STRICT source checks, package inventory on actual host | Small reproducible deployment plan |
| **0x08–0B** | Studio | FFmpeg/ffprobe, optional Godot/Blender | CPU fallback, asset rights, permissions | Real codec test, render benchmark and SHA receipts | Add GPU only on hardware evidence |
| **0x0C–0F** | Interface | Remote HTML kiosk, optional local display | Browser and session privileges | Real phone/WebGL test, keyboard escape and review | Optional desktop choice |

Hex symbols are **logical audit indices**, never memory addresses, chipset offsets, Linux kernel configuration bits or bytecode. Do not turn an index into a tuning parameter.

### Distinguish physical host, VM and container

- **Physical Linux host or VM:** one running Debian distribution kernel, updated and signed under its owner/vendor policy. Start with Debian 13's **6.12 LTS kernel family**. This is not permission to install a mainline 7.x or 6.18 kernel, change UEFI, edit GRUB or enroll signing keys. Document x86-64 versus ARM64 binaries independently and retain a tested boot rollback.
- **GitHub Codespaces / Docker:** one existing **host-owned** kernel shared by all containers. Kernel modules and GPU pass-through require host/provider approval. A custom image changes userland, not the kernel.
- **Android/Samsung:** vendor GKI, AVB and Knox; no Debian GRUB, no generic custom kernel. UI is the signed app or browser only.
- **iOS:** vendor-managed Apple kernel; app/browser client only.

### Desktop and rescue trimming

| Profile | Default? | Decision |
| --- | --- | --- |
| Headless | **YES** | Minimal Python 3 + sqlite3, Git, certificates; on-demand local jobs; no desktop, display manager or public daemon. FFmpeg/ffprobe optional until a media job needs it. |
| Browser kiosk | No | Reuse PR #476 DOM→Babylon progressive web UI. A dedicated graphical browser session may use Wayland or X11, but browser fullscreen is not device lockdown. |
| Studio desktop | No | Choose **one** GNOME or Cinnamon installation only if a real local GUI editor is needed. Do not make either a container or phone requirement. |
| Rescue | No | GParted Live and GRUB rescue are separate operator tools with backup/verification and explicit physical approval. Never bundle into the live art daemon. |

Debian installer **Desktop environment** task is optional; **Standard system utilities** are ordinarily recommended for a functional installed host. Prefer a minimal installation, with package closure and security updates measured before deleting anything. See https://d-i.debian.org/manual/en.amd64/ch06s03.html.

### Emulation lessons, no ROM/BIOS distribution

- **PlayStation 1:** DuckStation research on frame pacing, texture enhancement, input/controller interfaces. Current license and redistributability need per-revision review.
- **PlayStation 2:** PCSX2's open code offers CPU/GPU timing, JIT and renderer studies; **GPL-3.0** and user-owned BIOS/game requirements preclude blind code copy into an Apache-oriented core.
- **GameCube/Wii:** Dolphin's OpenGL/Vulkan and portable client approach is useful. **GPL-2.0-or-later** source cannot be silently copied into our differently licensed code.
- **Libretro:** the interface specification is **MIT**, while RetroArch and cores have independent licenses. Study its portable frontend/core boundary, not an implied universal license.
- **ScummVM:** study original fixed-camera/prerendered environment + realtime 3D technique, never copy commercial art.

We are not building an emulation appliance. Reuse benchmarking, input, state serialization and frame pacing ideas only, within licenses. No BIOS/ROM downloads, game texture extraction, or emulator service in the headless profile.

### Machine-only snapshot

```sh
# From repository root, source-only receipt; runs anywhere with Python 3 and SQLite STRICT
python3 -m unittest discover -s tests -p 'testMachineDebianSnapshot.py' -v
python3 tools/machineDebianSnapshot.py

# ONLY on an owner-authorized Debian/Linux machine:
python3 tools/machineDebianSnapshot.py --host-read-only

# Optional synthetic fixture for tests, clearly marked as artificial:
python3 tools/machineDebianSnapshot.py --fixture path/to/fixture.json
```

The host probe reads only coarse OS, kernel, architecture, CPU, page-size, distribution and non-sensitive memory totals. It does not run `sudo`, `lsblk`, `lspci`, `dmidecode`, `modprobe`, `apt`, `grub-*`, `gparted`, `nvidia-smi`, emulators, FFmpeg or a shell. Tool availability is checked with `shutil.which`, not execution. It does **not** read SMBIOS identifiers, device serials, private media, the kernel command line or credentials. Sources are SHA-256 hashed; a disposable in-memory STRICT SQLite table checks numeric receipt ordering. Use source-only CI by default; a GitHub runner is not the Professor's host.

The snapshot is an **inventory/evidence artifact, not a completed physical deployment or guarantee of GPU codecs**. It does not prove page alignment on Samsung or the physical Debian host firmware, boot policy, cache benchmark or network timing.

### Practical Git unification and existing proposals

- Reuse the existing machine wizard, typed SQLite manifest, artist-first Canon and FFmpeg host adapter. Don't copy agent orchestration into the kernel or add Python network listeners.
- Review sibling drafts [PR #448](https://github.com/eggie-admin/LuHm-OS/pull/448) (K9000 headless), [PR #451](https://github.com/eggie-admin/LuHm-OS/pull/451) (Debian/Pi kiosk/forge), [PR #453](https://github.com/eggie-admin/LuHm-OS/pull/453) (Samsung kernel lanes), [PR #471](https://github.com/eggie-admin/LuHm-OS/pull/471) (hardware 4×4) and [PR #473](https://github.com/eggie-admin/LuHm-OS/pull/473) (compute four-core) by **exact source**. These aren't part of protected main; do not assume their contents are already released.
- PR #475 is a playable browser/Godot demo, and #476 is a browser kiosk candidate. The backend must provide assets only through an explicit rights-reviewed and authenticated upload/download interface later.

### Promotion gates still open

1. Run inventory on **actual authorized Debian host**, confirm CPU arch/kernel release/boot policy and available storage.
2. Verify kernel config, module signature enforcement and driver ABI, without loading modules or changing boot flags.
3. Build a minimal service image on the supported host; prove Python 3/SQLite, FFmpeg CPU encode/decode, Godot headless import, optional Blender preview.
4. Capture CPU p50/p95, memory peak, page size, cache-miss data only if permissions allow, GPU acceleration only when present.
5. Record rollback, costs, license BOM, private asset rights, source SHA and human approval before production or public store delivery.

**CROWN STOP.** This is a complete *source snapshot contract* but not a custom compiled kernel or installed machine backend.

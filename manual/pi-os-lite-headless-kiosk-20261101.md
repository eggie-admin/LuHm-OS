# LuHm-OS | Raspberry Pi OS Lite backend → optional kiosk
**2026-11-01 · Proposed source candidate · CROWN STOP**

## Machine-first choice

Target **Raspberry Pi OS Lite (64-bit), Debian 13 Trixie**, for a headless Pi 4/5 where hardware confirms the ABI and memory budget. The official October 6, 2026 Pi OS Lite image uses the **6.18 Pi kernel family**, unlike our generic Debian 13 baseline that cited **6.12**. Do **not** automatically replace a Pi kernel with the generic Debian kernel or copy an x86_64 image onto ARM. Preserve tested vendor firmware, device tree, overlays and documented boot rollback.

Pi boards do **not** use the conventional PC BIOS/GRUB stack. The boot path is board firmware/EEPROM (board-dependent) → `/boot/firmware/config.txt` and Device Tree → supported Pi kernel → systemd → unprivileged userspace. Never edit `config.txt`, `cmdline.txt`, EEPROM, SD partitions or `/etc` from source CI. Pi 5 may use `kernel_2712.img`, with a different default page-size configuration than an older Pi: read actual page size before tuning. Both `4 KiB` and `16 KiB` are valid observed hardware/OS-dependent values, not software register IDs.

**This repo has not booted an actual Pi**. A successful Debian container test runs on a GitHub-hosted kernel, not a Raspberry Pi kernel.

## Four layers × four review phases

| Logical range | Layer | Inventory | Authority | Safe proof | Proposal |
| --- | --- | --- | --- | --- | --- |
| 0x00–0x03 | Pi firmware & kernel | Pi board generation, boot path, DT, ABI | OEM/owner boot policy | Real read-only OS/kernel config and page size | Targeted *reviewed* config diff, never automatic flash |
| 0x04–0x07 | Headless OS | Pi OS Lite, systemd, Python 3, SQLite, Git | Non-root owner | Package identity, strict typed SQL/sha receipts | Minimal fixed-source runtime |
| 0x08–0x0B | Studio services | FFmpeg, on-demand Godot/Blender | Unprivileged job boundary | CPU codec/frame and memory test; GPU only if present | Optional accelerated worker |
| 0x0C–0x0F | Kiosk & remote UI | DOM/SVG studio; optional labwc/Chromium session | Browser session, not root | Loopback CSP/method audit and real physical phone | Authenticated remote tunnel/edge after approval |

**Namespace:** `piOsMachine:0x00..0x0F` is a *logical audit ID*, not an EEPROM location, I/O register, kernel bitfield or Windows/Android Registry key.

## Minimal profiles and desktop trade-off

**Default: headless.** No Xorg, GDM, GNOME, Cinnamon, desktop manager, login shell autostart, SQL server, Apache, NGINX, Unreal GPU service or exposed web port. Reuse Python 3/SQLite and the existing local npm audit; FFmpeg runs only when needed. GitHub Actions verifies source.

**Optional local HDMI kiosk:** Raspberry Pi's official tutorial uses **labwc Wayland** and Chromium. Use the supported Raspberry Pi OS graphical edition if the required Wayland session packages are absent; **do not blindly install GNOME/GDM onto Lite**. Chromium's `--kiosk` gives a fullscreen browser, **not** OS lockdown. Do not enable unattended autologin, background startup, root browser, or kiosk flags without physical session, input/escape and recovery tests. A phone-only studio does not need a Pi graphical desktop at all.

**Optional GNOME/Cinnamon:** not a minimal Pi baseline; compare only when a real local desktop editor demands one. **GParted/GRUB rescue** are not Pi operating services or routine boot prerequisites. Keep backups and explicit owner approval for recovery workflows.

## The actual candidate now in Git

`tools/pi-kiosk/preview.py` exposes **only** `127.0.0.1:8765` and serves a strictly allowlisted version of the existing session-only HTML studio shortcuts. It uses Python standard-library HTTPServer, not PHP/Apache/NGINX, listens with no root privileges, serves only `GET`/`HEAD`, denies uploads, and refuses symlink traversal and unknown paths.

- The page shows Play, Edit, Assets, Build, Audit and Settings with **session-only usage sorting**, no telemetry, persistent profile, private art fetch, live GPU claims, or task worker activation.
- It sets CSP, `nosniff`, frame-deny, no-referrer, same-origin resource policy, and no-store headers. These are defense-in-depth for a small internal demo, not a substitute for TLS/authentication on remote access.
- A `/healthz` endpoint exposes **no IPs, hardware serials, task history, session tokens or OS details**, and explicitly labels the backend *AMBER LOOPBACK PREVIEW ONLY*.
- `--check` emits hashed sources **without starting a listener**. Tests run a separate temporary loopback instance and verify forbidden methods/paths.

### Read-only sanity tests

```sh
python3 -m unittest discover -s tests -p 'testPiOsLiteKiosk.py' -v
python3 tools/pi-kiosk/preview.py --check
```

### Optional **local operator-controlled** preview, only on a trusted non-root machine

```sh
python3 tools/pi-kiosk/preview.py --port 8765
```

Open `http://127.0.0.1:8765/` in the **same machine's** browser. **A phone cannot reach that loopback port by typing the Pi's LAN IP**; do not change the bind address to `0.0.0.0`. For mobile access, first provision an authenticated private tunnel or an HTTPS gateway with an explicit user identity, origin restriction, TLS, logging minimization, access revocation and network tests. Those are **not** active in this PR.

## Pi remote studio roadmap, small and quiet

1. **Zero privilege:** exact-source and CI green, no Pi board required.
2. **Physical board audit:** learn actual Pi model/RAM, supported kernel, 64-bit ABI, page size, GPU driver/thermal and firmware read-only. Preserve rollback image.
3. **Headless studio:** test actual FFmpeg jobs, Godot headless import and private asset handling under non-root resource quotas. Blender/AI inference only if measured budget permits; larger Unreal renders remain on an approved remote GPU host, not the Pi default.
4. **Remote UI:** open the same HTML cockpit through an authenticated transport; only after that consider a display session for HDMI.
5. **Release:** test phone browser, accessibility, network boundaries, signed builds, compatibility and operator-approved update channels.

## Existing drafts, not yet merged

- #451: Debian/Pi kiosk example and Netplan proposal to reconcile rather than copy blindly.
- #477: Debian headless FFmpeg userland and machine snapshot.
- #478: local npm/Python/SQLite audit.
- #479: typed device registry and mobile session-first UI.
- #475/#476: First Night game and DOM-first Babylon kiosk candidates.

No additional vendor dependencies or boot mutations in this Pi overlay. No automated package/SD installation, SD flashing, remote access rollout, kernel compilation, GDM selection, AI worker activation or production merge.

Official sources:
- https://www.raspberrypi.com/software/raspberry-pi-desktop/
- https://www.raspberrypi.com/documentation/computers/os.html
- https://www.raspberrypi.com/documentation/computers/config_txt.html
- https://www.raspberrypi.com/tutorials/how-to-use-a-raspberry-pi-in-kiosk-mode/

**Source contract is complete only when exact-head CI is green. Physical Pi OS deployment remains UNVERIFIED.**

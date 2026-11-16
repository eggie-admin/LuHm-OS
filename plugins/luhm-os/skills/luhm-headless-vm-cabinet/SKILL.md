---
name: luhm-headless-vm-cabinet
description: Use the LuHm 4x4 headless Raspberry Pi / QEMU-VM / RetroArch-Kodi-Plex / camera-OBS-mocap source matrix. Return evidence-bound plans without installing, streaming, accessing devices or executing independent agents.
---

# Headless machine and universal VM cabinet (draft)

Purpose: keep the existing private ChatGPT/Project Hydra seven-visual-plane cockpit as **thin presentation**, not a privileged GDM daemon, camera app, media host, local root UI or emulator. All machine operations cross the canonical LuHm MCP/Lum proof boundary.

## 4x4 review matrix

Read `doctrine/headlessUniversalVmMatrixV1.json` first. The four lanes are `foundation`, `virtualization`, `emulationMedia`, `captureMotion`. Their stages are `R1` inventory/source, `R2` capability/permissions, `R3` isolated proof/snapshot/benchmark, and `R4` owner review and possible promotion. This is **16 candidate cells**, not 16 running bots.

Use `luhm_machine_matrix_status` for source/schema integrity and `luhm_machine_matrix_plan` for a named lane with exact taskId, 40-character sourceRef and scopeId. Results are source candidates until the actual installed ChatGPT tool and target machine provide independent host receipts. Do not label a source-schema check as a physical device or guest runtime success.

## Hardware and VM

- Raspberry Pi OS Lite has a headless Linux userspace and kernel on real hardware. ARM64 and x86_64 builds are not interchangeable; camera sensor/USB and GPU firmware still depend on physical drivers. No universal VM replaces host device trust.
- Consider session-scope libvirt + QEMU for approved local guest isolation. Use KVM only when supported by hardware and `/dev/kvm`; QEMU TCG is emulation/JIT, not equivalent host speed. Keep the remote WMS vendor unresolved until actual connection proof.
- No raw SSH or libvirt URI in browser parameters. No automatic camera/USB passthrough, guest creation, kernel patching, firmware writing or network exposure.

## Media, retro and studio

- RetroArch/libretro provides a modular reference for frontend/core separation, but RetroArch is GPLv3 and cores have variable licensing, including noncommercial options. Research and compare, **do not copy** without documented license compatibility and distribution plan. BIOS/ROMs need provenance and rights; never fetch or redistribute them automatically. Compare legal open-content homebrew demos first.
- Kodi JSON-RPC is a remote media interface with its own security model. Plex is optional and proprietary, with transcoding resource demands; not part of a mandatory open-source base.
- If the Professor's "OBC" means OBS, use the upstream OBS Studio WebSocket 5.x contract after explicit confirmation. The label `OBC` remains unresolved in Canon until clarified, no guessed credentials or connection.
- F-Droid is Android repository/build infrastructure, **not a universal camera driver**. Review Open Camera for runtime permission UX, external mic behavior and reproducible builds; CameraX for lifecycle binding. Raspberry Pi libcamera/V4L2 capture needs local host consent.
- MediaPipe Pose is a candidate mocap inference plugin, not a proved multi-webcam body-tracking solution. Require calibration, consent, per-camera timestamps, memory/thermal benchmarks, rights and offline reference clips before any live capture.

## Controlled execution / evidence
The machine cycle is `hear → resolve → act → verify`, reusing `doctrine/escalationKernelV1.json` and `doctrine/cryptoBreathingEscalationV1.json`. `tools/headlessMachineMatrixAudit.py` audits Canon and can **simulate** four PASS states to test the code's stop rules. It must not accept simulated PASS as remote hardware proof. Read-only source/CI is permitted; agent workers remain quarantined. Only trusted exact-source machine receipts may support a future separately approved R1-R4 execution adapter. Stop on UNKNOWN, stale evidence, mismatched SHA, missing source rights, absent consent, unverified JIT/USB isolation, or authority escalation.

GitHub is the canonical source authority. SQLite/MariaDB store bounded metadata, private approved storage handles binaries, and cryptographic content hashes do not grant publisher authenticity or owner consent. Never merge, deploy or publish without applicable authority.

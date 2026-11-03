# Operation Staircase: 2×2 → 4×4 → snapshots → CAST distro (2026-10-30)

**Status:** PROPOSED_SOURCE_ONLY; **CROWN=STOP**. Main remains `f0cb6ee54066b490c0e80efc2c96200fec76ee2d`. This is an additive handoff in existing draft PR #461, not a new canonical authority, driver installation, build, host upgrade, or release. Full source-only validation package and hash receipts are retained in the task handoff (not pushed to public GitHub).

## Stage 1 · Foundation 2×2
Rows: **local / remote**. Columns: **hardware+kernel / software+services**.
- Local hardware: Pico firmware, Raspberry Pi OS/kernel, Samsung vendor Android, USB/UVC, Linux BlueZ/Bluetooth.
- Local software: PipeWire/ALSA, V4L2, FFmpeg, Blender, Godot, npm frontend.
- Remote host: VM image, virtual NIC/kernel, recovery console; Codespaces is not an on-premises machine.
- Remote services: GitHub CI, AI provider capability, NGINX/Render/Cloudflare trust boundary, Python/MCP/SQLite.
- **Snapshot 1:** source-bound 4-cell receipt, immutable input digest, all unknown hardware marked UNTESTED; no claim of host backup or device proof.

## Stage 2 · Integration 4×4
Rows **inventory / harden / verify / promotion**, columns **hardware / kernel+distro / remote AI+backend / frontend+studio**. Enumerate 16 controls covering permissioned USB/Bluetooth/media, supported OS route, remote provider trust, schema-bound MCP, art rights, timing, reproducibility and mobile proof.
- **Snapshot 2:** second source-bound 16-cell receipt, SHA-256 chained to Snapshot 1. Integrity hashes are not backup/restore evidence or signatures.

## Upgrade target; no execution
- First **observe the exact Ubuntu host's OS version** and prove recoverability. Canonical enabled 24.04 LTS → 26.04.1 LTS on 2026-09-29. This is a *conditional* target, not a claim that any owner's host is currently on 24.04.
- Inspect disk, power, apt/dpkg consistency, firmware/third-party drivers, PPAs, network owner, SSH/console rescue, service compatibility, and **restored offline snapshot**.
- Raspberry Pi OS major version is a separate image/recovery lane; Pico is firmware; Samsung OTA stays OEM-only; Codespaces is an image rebuild, never host kernel control.
- Hold a **single-use, exact-host CAST** with `milestoneId`, `taskId`, `sourceRef`, host identifier stored privately, target OS, expiry, nonce, operator and recovery receipt. A bare word `cast` without satisfied gates is insufficient.
- After separate CAST approval and successful preflight, the owner performs Canonical's interactive `sudo do-release-upgrade` on that exact Ubuntu host, not via ChatGPT/GitHub Actions. Never run unattended bootloader/partition prompts.

## Two current source-only snapshots
- Snapshot 1 SHA-256: `c02a656261575535ee54b13e3a78cfe5b4915b30e0983ab0f4d4004bc3941f4f`.
- Snapshot 2 SHA-256: `22ef2d56f81fc793aaf4a1ea03f5b46aab7b65474d2b1fccfd9b26ecca9ff8c8`.
- Blocked CAST envelope SHA-256: `8234e0c9ef9a67165aa971e69c505889acad3bdda3c11028b9ad9c84a7415abe`.
- Tests on the candidate local package: **6/6** contract/negative tests plus Python compile and shell syntax validation. These do not attest physical hardware.
- Nothing signed, deployed, merged, upgraded, flashed, billed, or published.

## Reuse existing sources
- PR #460: `manual/bootToCastMachineRecoveryLadder20261030.md`, `manual/hardware4x4VendorReductionCast20261030.md`, `manual/networkKernel4x4Hardening20261030.md`.
- Existing main: `doctrine/currentSourceTruthV3.json`, `AGENTS.md`.
- Existing draft PRs #420 / #445 / #448 / #451 / #452 / #453 remain donor/candidate only.
- Upstream: https://ubuntu.com/server/docs/how-to-upgrade-your-release/ and https://lists.ubuntu.com/archives/ubuntu-announce/2026-September/000328.html ; https://www.raspberrypi.com/documentation/computers/os.html

**NEXT:** real owner-invoked read-only host inventory → private restore test → exact-source compatibility tests → two refreshed signed-or-durable snapshots → scoped CAST authorization. Public release and Crown remain STOP.

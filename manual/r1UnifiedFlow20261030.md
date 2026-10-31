# R1 / One unit, one flow / hex audit ladder
**Source-only candidate on draft PR #463.** Run in Termux, desktop Python, or the exact-source GitHub workflow. No new workflow file, package manager, root service, kernel module, GRUB writer, new AI agent or production authority.

## Reuse before invention
R1 is a thin **controller**, not a new policy authority. It composes:
1. `tools/escalationKernel.py`: five domain profiles, existing four zero-based tiers 0–3, `hear→resolve→act→verify`.
2. `tools/crownEscalationMatrix.py`: established **16 + 64 + 256 = 336** source/evidence slots with actual STOP gates.
3. `tools/rootlessCast36Audit.py`: existing 36 Samsung / Python / SQL / AI source contracts.
4. `tools/mediaStudioAudit.py`: the vendor-reduced native Web event, WebP, VLC boundary contracts.
R1's own lightweight 16 source booleans and **4×4×8×16 = 2,048** addressable planning matrix do not mean all permutations were exercised. It deterministically proposes 256 unique matrix addresses. **Exactly zero matrix/device/firmware/model benchmarking cases** are executed by the planner, apart from the named deterministic source checks and existing Crown source assessment.

## One procedure, dual direction
`hear` accepts source identity and scope, `resolve` checks canonical source and existing doctrine, `act` **only evaluates bounded local source evidence**, and `verify` emits a fail-closed receipt and the next *proposed* zero-based escalation tier. If source evidence fails, the existing escalation kernel proposes moving from tier 0 to 1, but does **not** dispatch workers. If source evidence passes, remain tier 0 and Crown STOP because device proof, owner CAST, signer and release acceptance remain independent.

Use the hex depth ladder: `0x00, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x100` = `0, 2, 4, 8, 16, 32, 64, 128, 256`. Depth is a coverage planning intensity, **not permission to mutate or additional work falsely marked complete**. Above `0x10`, new host/network/device or human evidence is required before any actual deeper execution.

## Linux/firmware/Android reality
The firmware and kernel belong to the host OS, not to a Python script or SQLite schema. On Linux `--inspect-host` optionally probes coarse *presence* of EFI and GRUB directories, without reading boot configs, kernel parameters, machine IDs, or executing `grub-install`, `update-grub`, `efibootmgr`, `sudo`, `su`, `dd` or reboot. On stock unrooted Android/Termux **GRUB does not apply** and nothing modifies Android boot partitions or device firmware. SQL remains SQLite in the app user-data sandbox.

## Use now
On a checked-out PR #463 candidate:
```bash
# Single source-only entry point. No package installations:
python3 -m tools.r1UnifiedFlow --source-ref "$(git rev-parse HEAD)" --depth 0x10
# Opt-in coarse host metadata, still read-only:
python3 -m tools.r1UnifiedFlow --source-ref "$(git rev-parse HEAD)" --depth 0x10 --inspect-host
# Request a deeper *plan*, not 256 invisible tests:
python3 -m tools.r1UnifiedFlow --source-ref "$(git rev-parse HEAD)" --depth 0x100
# Existing rootless launcher:
bash tools/termuxRootlessCast.sh audit
```
The CI workflow stores a sanitized source receipt under its existing ephemeral artifact; it never performs `--inspect-host` in a shared runner.

## Human-centered modes and minimal interactions
Machine↔machine: typed read-only source and receipt exchange. Human↔machine: tablet command and human-readable stop reason. Human↔human: explicit issue/PR review and source-linked artifact receipts. Creative studio↔device: original assets and rights-cleared derivatives, no raw biometric data upload. The owner handles only true privileged/physical/rights blockers; AI stays advisory.

**Not built:** firmware-level orchestration, universal bootloader support, native Samsung APK, GRUB edits, kernel driver installs, private Google Drive sync, provider benchmark scores, 3D/game runtime demonstration. None are asserted green. Owner's distinct signed Android beta lane is preserved.

**Crown STOP.**

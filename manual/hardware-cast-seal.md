# LuHm-OS | Hardware CAST Bridge seal

**Purpose:** Close the source-level hardware design without altering real devices, inventing a universal firmware, or expanding the architecture. The exact source is a draft PR only. A green source gate is *not* a physical kernel, VM boot, Samsung installation, or owner promotion.

## One consolidated 4×4

`doctrine/hardwareCastSealV1.json` and `tools/hardwareCastSeal.py` reconcile existing, authoritative work rather than replacing it:

| Four lanes | R0 sanity | R1 hard audit | R2 source tests | R3 runtime/owner seal |
| --- | --- | --- | --- | --- |
| Hardware identity | ISA & canonical typed hex | width, bus, firmware, rights | prior machine & hostile audit | actual host CPU/firmware/permissions |
| Kernel boundary | installed supported distro kernel | no firmware, root, bootloader or kernel mutation | prior local host audit | actual kernel/architecture receipt |
| Guest isolation | local-only QEMU/KVM candidate | deny cloud, host ports, USB/BT/GPU pass-through | source VM sizing and hostile fixture | user-approved guest image, real boot/snapshot restore |
| Evidence & release | exact Git source and two logical CAST timelines | quarantine and owner's final release gate | independent file bundle digest, CI | observed execution, authorization and rollback |

This is **16 scoped source proof cells**, not 16 hypervisors, agents or running kernels. All matrix entries remain "CANDIDATE_ONLY" in the source contract. `SOURCE_READY_RUNTIME_HOLD` means all four existing **source audits** agree, not that R3 has been executed.

## Exact-source and source integrity

The seal reads *fixed, allowlisted* source auditors: `tools/localOpenVmKernelGate.py`, `tools/machineFourArchitectureAudit.py`, `tools/hostileModForgeAudit.py`, and `tools/brandVmSealAudit.py`. It rejects changes to the auditor allowlist, any false host-proven flags, missing anchors, altered 4×4 cells, current company-worker quarantine, or user-permission rules.

The bundle digest is SHA-256 over ordered canonical file names, lengths, and bytes. It is useful for repeatability but **not** a publisher signature. A supplied 40-character Git `sourceRef` only passes *shape validation*; GitHub Actions checks the actual checked-out commit with `git rev-parse HEAD` and passes that value into the seal. A branch update after CI requires new exact-source CI and must not inherit the old pass.

## Host setup for the first real guest

Preserve Linux distribution-supported kernel and the machine's firmware. Prefer an owner-controlled local x86-64 or Arm64 Debian/Ubuntu/Pi Linux machine. QEMU with KVM can accelerate a suitable guest, subject to `/dev/kvm` availability and user permissions. A `qemu:///session` libvirt profile is only a future option, not guaranteed usable on all systems. No hypervisor is automatically installed or booted.

The first optional **local-only** probe is already staged:

```sh
python3 tools/localOpenVmKernelGate.py probe --local-only
```

It runs on the machine where the command is executed, **not** necessarily the user's Samsung tablet. It checks nonidentifying OS/kernel/architecture, `/dev/kvm` permissions, QEMU binary presence and a user-session socket. This is not a boot receipt. The source-only seal requires no probe.

## Five real blockers kept visible

1. Owner-host actual kernel and CPU/architecture receipt.
2. KVM acceleration or QEMU/TCG mode tested on that host.
3. Rights-cleared guest image and accepted CPU/RAM/disk resource budget.
4. Actual isolated guest boot and snapshot/rollback proof.
5. Owner approval tied to exact Git source/scope.

No firmware flash, microcode, bootloader, root/kernel update, cloud account, paid inference or automatic remote bridge is necessary to start the first local test. Android remains a thin client; its own device-specific virtualization cannot be presumed. Existing GitHub and ChatGPT remain acknowledged proprietary exceptions; Render's historical web service is not a VM.

## Validation

From the repository checkout:

```sh
python3 tools/hardwareCastSeal.py
python3 -m unittest discover -s tests -p 'testHardwareCastSeal.py' -v
```

GitHub Actions: `.github/workflows/hardware-cast-seal.yml` verifies exact checkout SHA and the composite source gate; the larger offline bridge also runs this focused test. Read-only proposed MCP source tool: `luhm_hardware_cast_seal`. The connected ChatGPT plugin must be separately updated before that tool can appear in chat.

**Final statement:** Source-layer hardware architecture **ready for owner host acceptance** after a clean exact-head CI receipt. **Physical hardware layer is not sealed** until real execution proof and approval. The source remains draft; company agent quarantine and main-branch protections remain intact.

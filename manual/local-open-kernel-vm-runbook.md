# LuHm-OS | Local open-source kernel + VM operating profile

**Decision:** The supported Debian/Ubuntu/Raspberry Pi Linux **host kernel remains unchanged**. Run the heavy creative workload in an **owner-controlled, unprivileged local guest** when the physical machine supports it. Keep the Samsung tablet as the regular Android thin-client, not as a bootloader-unlocked experiment. Existing ChatGPT and GitHub are **optional proprietary interfaces**, not mandatory compute vendors for a local project. Render is a *historical* user-authorized hosted bridge and must not become a new default dependency. No new provider account, expense, or cloud execution is authorized by this document.

## The practical small setup

| Component | Default | Actual state |
| --- | --- | --- |
| Physical kernel | Distribution-supported mainline-derived Linux kernel, no patch or flash | No owner-machine probe yet |
| Hypervisor | Kernel KVM if the host exposes permitted `/dev/kvm` | Unverified |
| Guest | QEMU/libvirt **user session** (`qemu:///session`), not root/system-wide by default | Proposed, not booted |
| Fallback | QEMU TCG in a small fixture, or ordinary Linux app without a VM | Performance unknown |
| Guest network | **Disabled** until owner explicitly approves a specific need | No guest created |
| VM devices | No camera, microphone, USB, Bluetooth, GPU, raw disk or host ports by default | No pass-through configured |
| Local applications | Git (local repository), Python, Node, SQLite, FFmpeg, Godot, Blender, GIMP, R | Source-staged, not installed or measured in guest |
| ChatGPT cockpit | Existing read-only in-chat MCP bridge, opt-in remote UI | Independent of local VM boot |
| Remote providers | No default paid inference or rendering, no automatic fallback | Existing external services not removed |

An actual VM requires a **real Linux host** and a **rights-cleared Linux guest image**. QEMU and libvirt are open-source components, but their dependencies, guest software and some hardware firmware files have individual licenses. KVM is a feature of the supported Linux kernel, not a reason to recompile, flash or replace it.

## Four-by-four CAST operating cells

The machine is divided into `hostKernel`, `isolatedGuest`, `offlineStudio`, `optionalRemote` crossed with `source`, `capability`, `isolatedFixture`, `runtimeOwnerProof`. These sixteen entries are evidence checkpoints, **not sixteen agents or live virtual machines**. No evidence cell begins GREEN.

The current implementation is `doctrine/localOpenVmKernelProfileV1.json` and `tools/localOpenVmKernelGate.py`. It is an audited **capability and owner-review planner**, not a service that silently installs packages or starts guests.

## Read-only local checks

From the checked-out Git tree, using Python 3.11+:

```sh
# Safe anywhere: audits source contracts, no host inspection
python3 tools/localOpenVmKernelGate.py audit

# OPTIONAL, on an authorized Linux PC / Pi host only: read local kernel
# version, architecture, whether /dev/kvm is accessible, and if QEMU exists.
# No hostname, IP, MAC, serial, kernel command line, or secrets returned.
python3 tools/localOpenVmKernelGate.py probe --local-only

# Planning only. Numbers here are examples, not observed device memory.
python3 tools/localOpenVmKernelGate.py plan \
  --source-ref <EXACT_CURRENT_GIT_SHA40> \
  --arch x86_64 --host-ram-mib 8192 --host-cpus 4 \
  --kvm-claimed no
```

**Do not run the opt-in probe on arbitrary remote hosts or assume Samsung supports a full Linux VM.** Native Android AVF/pKVM is privileged and hardware/OS dependent. An unrooted Samsung may use only its normal Android app/WebView, or communicate through a separately approved private LAN gateway to a Linux host. There is **no Android bootloader unlock step** in this LuHm plan.

The probe reports observations from the machine where Python actually executes. A GitHub Actions probe would see GitHub's runner, **not** the Professor's computer or phone. It does not claim virtualization is working merely because `/dev/kvm` exists or because QEMU is installed.

## Only after a real host and owner approval

Use the Linux distribution's own documented packages and updates. On Debian a reviewed minimal QEMU/KVM installation can use `qemu-system`, `libvirt`, and optionally `virtinst`; package identifiers vary by release. Decide whether to use unprivileged `qemu:///session` after checking /dev/kvm permissions and libvirt user socket, rather than blindly modifying group membership or enabling privileged system services. Use a separately validated source and digest for an owner-supplied guest image; leave network and hardware pass-through disabled for the first boot. Cap guest CPUs and RAM below the host's actual available resources, leaving at least 1 GiB for the host.

The first genuine promotion receipt must show **host architecture + actual kernel**, **guest image provenance**, **isolated boot**, **rollback/snapshot**, **bounded resources**, and **the Professor's authorization**. Only then may the source status turn from proposal to a tested local runtime; CI alone is not that proof.

A heavier animation/rendering job can stay on the owner-controlled local host or its guest. GPU pass-through to a VM is **not** automatically possible and would require a separate machine-specific permission and driver compatibility check.

## Proprietary service policy

The source-of-truth repository is presently GitHub, the user's UI is ChatGPT, and an older web harness exists on Render. Those are **explicit existing exceptions**, not evidence that proprietary remote execution is necessary. Keep all original creative assets in user-owned local storage and local Git where possible. No secrets, private media, plugin tokens or billing credentials go in the repository, guest base image or browser.

Before enabling a paid or proprietary service, require a named missing capability that open-source local tools cannot reasonably cover, an explicit owner decision, clear storage/retention terms and a cost ceiling. No generic automatic cloud fallback.

## References

- Debian KVM: https://wiki.debian.org/KVM
- Debian QEMU: https://wiki.debian.org/QEMU
- Kernel KVM: https://www.kernel.org/doc/html/latest/virt/kvm/index.html
- Android AVF: https://source.android.com/docs/core/virtualization

**Current CAST status:** Source-only profile. No production kernel setting changed. No guest created. No new remote provider activated. The existing company-agent quarantine and draft PR release gates remain intact.

# CAST Four Core: GPU · CPU · Memory · Firmware

**Owner:** Professor. **Scope:** game and creative studio compute only. This is a source-only **stacked draft** on PR #472, not a new software platform or server. Existing public browser/MCP/provider integrations remain separately governed by their own Canon, but they are *not part of the compute image*.

## Why this trims the stack

The prior broad Codespaces image includes **34 declared apt package names** and supports optional NGINX, MariaDB, and Certbot. It also has an optional private FFmpeg service startup. That model stays untouched for historical compatibility.

New opt-in `.devcontainer/Dockerfile.compute` declares exactly **11** first-level apt package names and the existing pinned, SHA-256-verified **Godot 4.7.2** download. It contains Python 3 + venv, Git, Blender, FFmpeg and a minimal display-runtime library set. It has **no Node/npm interpreter, GIMP, NGINX, Apache, MariaDB, Postgres, mail server, DNS server, Certbot, EXPOSE ports or auto-started network worker**. It runs as unprivileged `studio`. This is a source recipe; build, apt solver dependency closure, actual runtime, FOSS/codec licensing and GPU availability **have not been proven**. Package count counts declared names, not installed transitive dependencies, maintained upstream organizations, or actual vendors.

## GPU/CPU/memory/firmware 4×4

| Dimension | Identify | Bound | Probe | Verify |
| --- | --- | --- | --- | --- |
| **GPU** | check only if a render node is present | never load a new OEM driver | read-only `/dev/dri/renderD128` existence hint | actual Vulkan/OpenGL/Blender GPU execution **unknown** |
| **CPU** | visible logical count and affinity | no more than four **advisory** app workers | no threads launched | cgroup CPU quota/physical cores **unknown** |
| **Memory** | optional `/sys/fs/cgroup/memory.max` cgroup v2 hint | min(64MiB, one-quarter of known cgroup max), **advisory** | only read 64 bytes; no stress allocation | memory usage/bandwidth and device page size **unknown** |
| **Firmware** | optional `/sys/firmware/efi` directory hint | stock OEM policy preserved | do not inspect or change firmware bits | UEFI/GRUB/Android AVB attestation **unknown** |

The `0x00..0x0F` labels are **logical source-index coordinates**, not real register addresses, firmware offsets or memory-mapped I/O. Do not confuse a Linux runner's `/dev/dri` availability with physical GPU performance. The presence of `/sys/firmware/efi` does not prove GRUB is installed. Android uses OEM boot chain and vendor GPU drivers; a Samsung APK needs no `apt` packages. A Codespaces container cannot install host drivers or change provider-managed firmware.

## Reproduction and safety

```bash
python3 -m unittest discover -s tests -p 'testComputeFourCoreAudit.py' -v
python3 tools/computeFourCoreAudit.py --probe-runner
```

The workflow checks out exact PR head, runs the source and negative controls, then reads only generic hints on that **GitHub runner**. No user/home data, serial numbers, MAC addresses, private firmware variables, browser credentials, secrets, device ROM, network topology, services, kernel or clock controls are read or changed. No image build occurs in this PR, so do not claim one.

Actual next gate: build the optional image in an isolated authorized environment; verify installed packages and licenses, Godot import and Blender-to-GLB export, cap in-process memory use and run native GPU discovery with real vendor-neutral APIs. Only then consider the smallest platform-specific optimized setting.

**Law:** AI proposes. Policy authorizes. CI proves. Human promotes. CROWN STOP.

## Selectable, not an implicit replacement

A Codespaces-compatible opt-in configuration exists at `.devcontainer/compute/devcontainer.json`. Choose that named **Four-Core Compute Studio** configuration when creating an appropriate remote development environment. It references `../Dockerfile.compute`, uses unprivileged user `studio`, has **zero forwarded ports**, and runs only non-server binary version checks on creation. It does **not** launch the former media service on start. The original default `.devcontainer/devcontainer.json` is intentionally unchanged until a genuine lean image build and studio runtime proof are available; do not claim this profile is active on any device or instance merely because the configuration exists.


## Machine boundary priority audit: bytes / packets / registry / SQL

The added `tools/castMachineByteAudit.py` and `tests/testCastMachineByteAudit.py` run inside the **existing** Premonition Vendor Footprint Gate. They do not install a new runtime or alter the four-core kernel/GPU/driver boundary.

**4×4 escalation remains:** GPU, CPU, memory, firmware × identify, bound, probe, verify. The independent application/SQL audit is a *crosswalk*, not 16 physically proven hardware checks. Hex `0x00..0x0F` values are logical source indexes only.

| Priority | Blocked evidence (not an observed defect) | Next smallest test |
| --- | --- | --- |
| **P0** | Real Samsung boot/OEM driver binding and actual Linux kernel/driver identity unverified | Read vendor-approved, device-scoped capabilities and exact driver/OS versions; do not flash or modprobe |
| **P1** | GPU availability and real frame time unverified | Godot + Blender local render smoke, captured GPU API/capability receipt |
| **P2** | Memory pressure, actual packet p95 and device transport unverified | Bounded application bytes and memory telemetry on a consented physical device |
| **P3** | CPU thermal, cgroup quota and sustained device baseline unverified | Repeatable device benchmark against a baseline, no governor write |

The P0..P3 values are **review ordering**, not CPU scheduler priorities or a claim of measured incident severity. The synthetic queue has **separate** values 0..3 (3 means urgent), a 32-item cap, stable sequence ordering and a 2,000,000,000 ns aging interval to keep older items from starving. It does not change OS scheduling policy.

### Exact boundaries

1. **Text:** NFC-normalized UTF-8, maximum 4,096 *bytes* per synthetic message; multi-byte characters make codepoint count insufficient for allocation estimates.
2. **Framing:** Four-byte network-order unsigned *application* length followed by bytes. This is **not an IP/TCP packet**, network MTU, DMA descriptor, physical page size or kernel message format. Oversize, truncated, extra-byte and malformed UTF-8 cases fail closed.
3. **Identity:** SHA-256 hashes the payload and four existing canonical source JSON files; it detects unintended byte changes but is **not authentication, signed code, a trusted driver certificate or permission to run code**.
4. **Storage:** An **in-memory SQLite STRICT** table stores bounded integer sequence/priority/wait/payload byte count and exact lowercase hex digest. Prepared inserts and explicit ordering demonstrate typed receipts without starting MariaDB, Postgres, or a public SQL service.
5. **Registry:** The four-item allowlist is a project **source-contract registry**, not the Windows Registry, `/proc` device-tree enumeration, npm package registry or host driver index. No registry install/write occurs.
6. **Kernel:** CPU affinity and cgroup limits are runner hints, not real Samsung evidence. Actual bootloader, driver binding, firmware and GPU claims remain blocked until independently observed.

### Verify the draft

```bash
python3 -m unittest discover -s tests -p 'testCastMachineByteAudit.py' -v
python3 tools/castMachineByteAudit.py
```

CI verifies exact-head source and preserves **CROWN STOP**. The proposed 4 KiB payload ceiling is a deliberately bounded test fixture, not a performance optimum. Promote to 8×8 only after paired runtime/device evidence; use 16×16 only for independently reviewed workload combinations. No blind merge, production kernel tuning, USB/PCI driver binding, signing, or public release follows from a green source test.

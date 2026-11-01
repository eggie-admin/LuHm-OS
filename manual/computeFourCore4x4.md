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

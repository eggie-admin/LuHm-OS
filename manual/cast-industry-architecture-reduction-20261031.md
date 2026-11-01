# CAST Industry Architecture Reduction | 2026-10-31
**Authority:** Professor · **Branch:** existing draft PR #473 stacked on #472 and #471 · **Status:** SOURCE RESEARCH ONLY / CROWN STOP.
**Intent:** Cross-platform studio and AI-assisted game workflow. This is **not** a request to install a kernel, modify GRUB, edit partitions, change Samsung AVB, activate agents or subscribe to an AI provider.

## Guiding choice: one contract, platform-owned lower layers
Keep high-level source + manifest + bounded performance receipts shared. Compile and test a distinct native adapter for each supported device. Do **not** assume x86 hardware and ARM SoCs expose the same firmware, GPU, page size, ABI, power governor, ISA extension, or bootloader.

| Family | ABI/CPU | OS and hardware handoff | Retain / refuse |
| --- | --- | --- | --- |
| Apple | Native arm64; optional x86_64 universal slice for compatible Intel Macs | XNU, Metal, native signing | Retain native arm64 and Metal; avoid a permanent Intel translation dependency. Apple's September 2026 Rosetta notice requires migration planning. |
| Android (Samsung) | arm64-v8a primary target; x86_64 only where emulator/device warrants | Android framework → HAL → vendor modules → Android kernel/GKI | Retain OEM AVB/Knox, SELinux, SDK/HAL; no PC GRUB or distro apt on Samsung. Check 16-KiB native page compatibility with actual AAB/APK/ELF and test device. |
| Linux | x86_64 + aarch64 via proper distro toolchains | Distro kernel/DRM/Vulkan; optional opt-in headless container | Prefer upstream interfaces, distro-supported LTS kernel and distro package pin. Never claim container kernel/UEFI equals device hardware. |
| Google compute | Host CPU architecture depends on VM/instance; TPU is accelerator not CPU ISA | Provider-managed Linux VM + TPU runtime | Learn capability detection; do not require cloud TPU or paid APIs for local demo. |

**No false equivalence:** Apple silicon is not the same as arbitrary ARM Android, Android kernel is not a vanilla Ubuntu mainline kernel, x86_64 Linux is not guaranteed to have a GPU, and a TPU MXU is not a CPU cache or GPU.

## Four layers × four functions (logical labels only)
4×4 platform/dimension crosswalk: `0x00..0x0F` spans Apple, Android, Linux, Google compute × ABI, kernel, accelerator, delivery. It does **not** assign registers, physical addresses, PCI identifiers, device-tree nodes, ISA instructions or JVM bytecodes.

Common AI function ordering is **route → reason → execute → verify**:
- **Route:** bounded text/byte count, classify intent; low reasoning where representative evaluations prove enough.
- **Reason:** task planning, source comparison, dependency resolution; medium/high only when measured task value justifies latency.
- **Execute:** only approved existing connectors, Python tooling, deterministic SQL; never AI self-approval or arbitrary shell.
- **Verify:** exact Git SHA, SHA-256 payload digest, provenance, tests, negative fixtures, human release gate.

Treat `SHA-256` as integrity, not signature or permission. Keep `UTF-8 bytes`, network framing, Android ELF page alignment, `sysconf` page size, CPU cache line, IO chunk and logical hexadecimal address in different namespaces. String lengths must be validated in bytes. A four-byte app frame header is **not** TCP/IP MTU.

## Data and compute: choose one minimum path
Retain Python 3 stdlib toolchain, in-memory SQLite STRICT, typed JSON manifests, GitHub source and Actions CI, Godot runtime and Blender/FFmpeg asset forge. Use a local SQLite file **only when a real persistence requirement arises**, with rollback, backup and schema version receipts. PostgreSQL and MariaDB are not dependencies for a playable demo.

The existing optional `Dockerfile.compute` declares 11 **first-level** apt packages and a pinned Godot binary; the old default Codespaces profile declares 34. Neither figure is the installed transitive-dependency count. Do not replace a tested development environment until an **actual isolated Docker build**, exact apt closure, license inventory, GPU-capability test and Godot/Blender/FFmpeg smoke demonstrate equivalence. Any reduction claims are *source declarations*, not measured disk or memory savings.

### Baseline lifecycle watch (observed 2026-10-31)
| Software | Upstream support/EOL | Decision |
| --- | --- | --- |
| Python 3.10 | EOL 2026-10-01 | No new baseline |
| Python 3.14 | bugfix supported; projected EOL 2030-10 | Conservative candidate |
| Python 3.15 | released 2026-10-09; projected EOL 2031-10 | Testing candidate |
| Node 22 | maintenance; EOL 2027-04-30 | Migration watch |
| Node 24 | maintenance; EOL 2028-04-30 | Transition candidate |
| Node 26 | active LTS since 2026-10-28; EOL 2029-04-30 | Test, **do not automatically upgrade** |
| Linux upstream LTS 5.10/5.15 | projected Dec 2026 EOL | Research distro/vendor backport policy before flagging actual host as unsupported |
| Linux upstream LTS 6.12/6.18 | projected Dec 2028 EOL | Research distro support and exact hardware before use |
| Ubuntu 26.04 LTS | standard support through May 2031 | Candidate; continue runner on known supported base until migration gate |
| PostgreSQL 14 | EOL scheduled 2026-11-12 | Do not introduce new Postgres 14; local SQLite remains preferred |

These are **upstream dates**, not an inventory of installed binaries. The manifest's end-of-month EOL placeholders for month-only upstream projections are used for classification, not a commitment of an exact day. Never auto-delete a dependent package or vendor firmware solely due to an upstream EOL table.

## Boot, rescue and no-code vendor choices
| Tool | Industry lesson | Our action |
| --- | --- | --- |
| GitHub Actions | Existing declarative YAML CI already does exact-head source and negative tests. | **Keep** as the single CI coordinator; don't add an alternative no-code server. |
| n8n | Visual low-/no-code workflows, **fair-code** licensing and server deployment surface. | **Study only**; no automatic dependency, no assumption of Apache-2. |
| GNU GRUB 2.14 | PC/Linux bootloader and boot-recovery reference. | **Read-only**. Not Android AVB, not a generic authorization layer. |
| GParted Live | Rescue partition editor; current Live images target amd64/x86-64. | **Offline rescue only**, pre-verified backup and explicit owner approval before disk writes. |
| Damn Small Linux 2024 | Low-spec x86 study: minimal apps, Fluxbox/JWM and small dependencies. | **Legacy lab reference**, not a universal modern ARM studio base. |
| Mainline Linux kernel | Upstream driver, MM, scheduling, CPUFreq and ABI reference. | **Study read-only**; production device uses vendor/distribution supported kernel. |
| R statistics | Compare paired benchmark runs, median/p95, confidence intervals and significance. | **Optional offline analysis** of CSV/JSON receipts, not a mandatory runtime or a means of tuning kernel signals. |
| perf | CPU hardware counters and cache miss profiles. | Only with approved permissions; do not change `perf_event_paranoid` or grant CAP_PERFMON just to run source audits. |
| Python tracemalloc | User-space allocation evidence. | Use for profiling a measured Python hotspot; it doesn't measure total GPU or native memory. |
| Godot profiler / Perfetto / Tracy | Frame time, draw and runtime tracing. | Use the engine's own profiler on a real device before proposing shader or memory optimizations. |
| ONNX Runtime EPs | Backend adapters for CPU, CoreML, NNAPI, CUDA and others. | **Evaluate later** only if offline inference becomes an actual requirement. No vendor installed solely for capability completeness. |

## Benchmark ladder, always measured before tuned
1. **Zero / source-only:** Verify schema, ABI targets, package pins, SHA-256, SQL strict types, input encoding and release-gate authority.
2. **2×2 minimal runtime:** Run exact benchmark on one supported Linux x86-64 environment and one Android ARM64 device, comparing CPU and memory only; record device/OS provenance and effective page size.
3. **4×4 four-core runtime:** GPU/CPU/memory/firmware × identify/bound/probe/verify. For GPU, real frame-time and driver API; for CPU, benchmark wall-time and quota; for RAM, RSS/peak and allocation; for firmware, OEM-reported boot and signing chain only.
4. **8×8 evidence:** Add cache-miss counters **where permitted**, app transport p50/p95/p99, storage SQL `EXPLAIN QUERY PLAN`, asset import and encode latencies, thermal repeatability; do not inflate 8×8 into unverified "workers".
5. **16×16 promotion:** Compare measurements per supported ABI and stage, isolate regressions, require signed artifact provenance and actual mobile installation receipts. No automatic public deployment.

Retain mean/median, p95/p99, max RSS and errors and include sample size, duration, hardware identity and confidence/variance evidence. Do not choose fastest SHA microbench input-size as an optimal cache line, a universal packet size, a kernel governor or a GPU workgroup size.

## Official quick-start/reference index
- Apple silicon port/universal app: https://developer.apple.com/documentation/apple-silicon/building-a-universal-macos-binary
- Apple Rosetta transition notice: https://developer.apple.com/news/?id=w5ngl9k2
- Android architecture: https://source.android.com/docs/core/architecture
- Android NDK ABI matrix: https://developer.android.com/ndk/guides/abis
- Android 16-KiB native page check: https://developer.android.com/guide/practices/page-sizes
- Google Cloud TPU architecture: https://docs.cloud.google.com/tpu/docs/system-architecture-tpu-vm
- Linux architecture manuals: https://docs.kernel.org/arch/index.html
- Linux kernel version policy: https://www.kernel.org/releases.html
- CPUFreq reference: https://docs.kernel.org/admin-guide/pm/cpufreq.html
- Perf permissions: https://docs.kernel.org/admin-guide/perf-security.html
- GParted Live/manual: https://gparted.org/livecd.php
- GNU GRUB Manual 2.14: https://www.gnu.org/software/grub/manual/grub/
- Damn Small Linux official project: https://www.damnsmalllinux.org/
- Python supported versions: https://devguide.python.org/versions/
- Node release schedule: https://github.com/nodejs/Release
- SQLite STRICT: https://www.sqlite.org/stricttables.html
- PostgreSQL release support: https://www.postgresql.org/support/versioning/
- R rank and paired tests: https://stat.ethz.ch/R-manual/R-devel/library/stats/html/wilcox.test.html
- Python tracemalloc: https://docs.python.org/3/library/tracemalloc.html
- ONNX execution providers: https://onnxruntime.ai/docs/execution-providers/

## Run this source-only gate
```bash
python3 -m unittest discover -s tests -p 'testCastIndustryArchitectureAudit.py' -v
python3 tools/castIndustryArchitectureAudit.py
```

The gate is hooked into the **existing** `Premonition Vendor Footprint Gate`. It checks exact schema, 4×4 axes, logical hex addresses, expired-baseline policy, trusted source URL shapes and protected boot/no-code boundaries. It does **not** fetch or install dependencies, confirm live device versions, benchmark a physical machine, resize disks or check firmware signatures.

**Promotion:** testing evidence → proposed review → private beta with signed APK and real-device checks → owner-signed public release. **CROWN STOP.**

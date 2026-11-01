# Processor and byte ceiling CAST, stacked 4×4

**Status:** Proposed, based on hardware/vendor branch PR #471 at commit `094a30c70f847414a37f1f246b5c2cd7393f5b7c`. This PR adds a read-only microbenchmark to the existing vendor-footprint gate. It **does not** change a bootloader, BIOS, GRUB config, firmware, CPU frequency, RAM timings, kernel module, NIC buffer, Linux `sysctl`, physical Samsung tablet, or public server.

## 4×4 source-index contract

| Layer | Identify | Bound | Measure | Verify |
|---|---|---|---|---|
| Firmware / boot | Separate PC BIOS/UEFI/optional GRUB from Samsung OEM AVB/Knox | preserve owner boot policy | actual boot tests **unknown** | source crosswalk only |
| Kernel / drivers | CPU/page and device **facts where observed** | no driver/governor changes | Linux runner accessible CPU counts | host hardware not attested |
| Hardware networking | existing `networkSpineV1`, IPv4/IPv6 policy | no firewall, NIC or public route writes | network throughput **not** measured | IPv6 prefixes not auth |
| Processor / memory | runner logical CPU, affinity and page-size hints | synthetic input ≤ `0x100000`, proposed concurrency ≤ 4 | SHA-256 streaming on three bounded sizes | exact data digest, scope and honest receipt |

All 16 cells are *symbolic* `castProcessorRuntimeFourByFourV1` route labels, not real memory addresses, offsets, IRQ values, kernel flags or CPU frequency multipliers. The previously separate hardware 4×4, orchestra 4×4, and SQL streams have independent namespaces.

The program uses **4 KiB (`0x001000`), 64 KiB (`0x010000`), 1 MiB (`0x100000`)** of synthetic bytes in three repeats for each sample. It measures SHA-256 throughput with a monotonic clock and selects the fastest observed input size **advisory only**. It is a tiny CPU/hash benchmark, *not* a reliable memory bandwidth, disk/network throughput, thermal throttling, cache line, sustained power or exact core-frequency test. There are no automatic performance thresholds, no overclocking and no scheduler or governor mutations.

The CI runner's `os.cpu_count()` may report the host rather than container quota. Where available `os.sched_getaffinity(0)` narrows the apparent CPUs, but **cgroup quota and actual physical cores remain unknown**. `os.sysconf("SC_PAGE_SIZE")` may report a process page size; it is not a claim about hardware cache lines or optimal application block size. Proposed 4-worker ceiling does not start any workers.

The measured runner result does **not** benchmark the Samsung Lite or prove a 4- or 16-KiB Android native library page-size requirement. Same-source Android signing, actual running device and UI responsiveness remain separate gates.

## Boot and permission boundaries

GRUB is one possible PC/Linux bootloader, not an Android privilege or a compulsory Debian component. A Codespaces container uses a provider-controlled host kernel and cannot assert the host's UEFI, GRUB boot menu, or real on-board NIC. Android Verified Boot is OEM-controlled. Linux CPUFreq interface and governor are privileged platform controls, not something a source-only pipeline can tune by guessing.

Official reference: GNU GRUB Manual (https://www.gnu.org/software/grub/manual/grub/); Linux CPUFreq policy (https://docs.kernel.org/admin-guide/pm/cpufreq.html); Android Verified Boot (https://source.android.com/docs/security/features/verifiedboot).

## Reproduction

```bash
python3 -m unittest discover -s tests -p 'testProcessorHexCeilingBench.py' -v
python3 tools/processorHexCeilingBench.py --measure --output /tmp/processor-hex-receipt.json
```

Output is a synthetic/runner-only JSON receipt. The workflow checks out the exact candidate, retains existing npm build and vendor size budget, saves a short-lived CI artifact, and never changes persistent host settings or runs a paid provider.

**Law:** AI proposes. Policy authorizes. CI proves. Human promotes. CROWN STOP.

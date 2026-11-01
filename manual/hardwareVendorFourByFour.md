# LuHm-OS CAST: northbridge, southbridge, chipset, firmware and minimum vendor packages

**Date:** 2026-10-31. **Status:** read-only source model on candidate, not observed physical hardware. Base protected main `f0cb6ee54066b490c0e80efc2c96200fec76ee2d`.

## Architecture truth and legacy translation

| Hardware situation | Actual architecture | Boot boundary | Driver and package scope |
|---|---|---|---|
| Legacy PC | Memory-controller Northbridge + peripheral Southbridge on older boards | Legacy BIOS, or UEFI depending on device | Identify chipset and PCI/USB bridges from observed enumerations; add compatibility packages only when a supported target actually requires them |
| Modern desktop | Integrated CPU memory controller; Intel PCH on many PCs, or another SoC/platform arrangement | UEFI/firmware where supported | PCI/USB modalias, actual driver, kernel version, signed firmware and distro package binding require separate receipts |
| Stock Samsung Android | ARM SoC. **Do not invent a separate PC Northbridge/Southbridge or BIOS.** | Samsung hardware trust, Knox and Android Verified Boot | Android application permissions and OEM-provided vendor/kernel interfaces; do not swap firmware or load arbitrary Linux modules |
| GitHub Codespaces/Linux container | Virtualized platform hosted by provider, not a physical chipset inventory | Provider-managed boot, no owner-host UEFI access | Ubuntu `apt` userland packages are *not* kernel drivers and do not change the host kernel |

Official references: Intel motherboard guide (legacy and PCH): https://www.intel.com/content/www/us/en/gaming/resources/how-to-choose-a-motherboard.html ; Samsung Trusted Boot: https://docs.samsungknox.com/admin/fundamentals/whitepaper/samsung-knox-mobile-security/system-security/trusted-boot/ ; Android AVB: https://source.android.com/docs/security/features/verifiedboot ; Debian dpkg query: https://manpages.debian.org/unstable/dpkg/dpkg-query.1.en.html.

## The hardware 4×4 map

Four **types of environment** × four **questions**: topology, boot trust, kernel driver/domain, and packages. All 16 entries are mapped to original Canon source locations and remain `SOURCE_MODEL_ONLY`, *not 16 actual devices tested*. Hex addresses `0x00..0x0F` exist in the **hardwareVendorFourByFourV1** index namespace only, not actual I/O/firmware register offsets, kernel flags or driver PCI identifiers.

## Minimum package selection (this does not run apt)

`tools/hardwareVendorMinimum.py` reads the existing `.devcontainer/Dockerfile` **as text only** and compares its 34 declared apt package identifiers with five separate proposed profiles. This does not change the image, current package database, UEFI configuration, BIOS firmware, protected Android partition or hardware drivers.

- `samsungCockpit`: **zero** Ubuntu/Debian apt packages; OS vendor-supplied Android runtime and permissions only.
- `linuxHeadless`: 4 selected declarations: `ca-certificates`, `git`, `python3`, `python3-venv`. Actual use may demand more based on proven feature needs; this is a source-level minimum, not a complete build.
- `linuxWebBuild`: inherit headless declarations + `build-essential`, `pkg-config`, `nodejs`, `npm`; build-only, not Android runtime.
- `linuxStudio`: inherit web build + `ffmpeg`, `blender`, `gimp`, `xvfb`, selected presentation libraries; **no Nginx/MariaDB server** by default.
- `existingCodespace`: all 34 declarations from the existing Dockerfile; preserved as an *existing* broad development environment, **not** proclaimed the minimum.

Keep the actual vendor count as small as possible, but do not equate an individual apt package with a separate hardware manufacturer. Debian/Ubuntu package dependency closure requires a real `apt` solver on the selected distribution; this tool verifies declarations only and never promises those profiles are independently bootable/installable. Future narrow actual runtime proofs will confirm imports, engine versions, codecs, kernel device permissions and FOSS licenses before proposing a Dockerfile split.

## Canon and mutation rules

Hardware drivers, BIOS/UEFI and Android firmware stay OEM-managed and read-only. Prefer documented supported upstream kernel/device interfaces. **Blender is GPL, Linux kernel is GPL-family**, and their distribution terms must be reviewed independently; "open source" does not mean "everything Apache-2." Distro package provenance must include exact package name/version/architecture/source and license details, never a hex string guess.

Use existing `doctrine/vendorReductionV1.json`, `doctrine/machineToHumanWizardV1.json`, `doctrine/storageTopologyV1.json` and company agent quarantine. Source policy **cannot** prove a physical Samsung, firmware chip, BIOS version, Linux module binding or installed apt packages.

Audit:
```bash
python3 -m unittest discover -s tests -p 'testHardwareVendorMinimum.py' -v
python3 tools/hardwareVendorMinimum.py --profile samsungCockpit
python3 tools/hardwareVendorMinimum.py --profile linuxStudio
```

**Law:** AI proposes. Policy authorizes. CI proves. Human promotes. CROWN STOP.

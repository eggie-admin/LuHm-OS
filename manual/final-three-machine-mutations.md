# LuHm-OS | Final three 4×4 machine mutations

**Status:** source-only draft in GitHub. Zero firmware flashes, Android boot image builds, live AI agents, provider credentials, Nintendo assets or kernel mutations. This is the last *architecture-planning* pass, not a supported new Linux distribution.

## 1. Retro tile/text hexadecimal lane

The original codec `tools/retroTileTextCodec.py` supports 8×8 **NES-style 2-bpp planar tiles (16 bytes)** and **SNES-style 4-bpp planar tiles (32 bytes)**, exact round-trip pixel conversion, original 4×4 (16 tile) maps and a restricted text-to-glyph lookup. Pixel data is caller-owned/synthetic and index values are exact. No palettes are invented or inferred, and the text format is an original LuHm lookup table, **not** an actual Nintendo game's character encoding. The 4×4 map is a LuHm planning representation, **not** a hardware-native nametable, cartridge file or licensed sprite library.

Outputs are a SHA-256 digest per tile, a sheet digest, and typed hexadecimal for map/glyph metadata; no commercial ROM, copyrighted sprite sheet or input image bytes are returned. The Godot/RPG conversion remains a separate approved importer task. Nintendo-era technique means structured bitplanes, stable indexes and memory discipline, not rights to Nintendo game content.

References: https://www.nesdev.org/wiki/CHR and https://snes.nesdev.org/wiki/Tiles

## 2. Portable Linux/Android target recipes, not one BIOS

`tools/portableOsRecipeAudit.py` defines **four independent targets × four evidence layers**:

| Target | Correct host architecture | Proposed release tooling | Important boundary |
| --- | --- | --- | --- |
| Debian | Multi-architecture Linux | Reviewed `apt` package candidate | Must obey per-package licenses and Debian brand policy |
| Ubuntu | Multi-architecture Linux | Reviewed `apt` package candidate | Modified redistributions require correct Canonical trademark treatment |
| Android GKI | Proposed arm64 phone lane | Android SDK/Gradle, not `apt` | Android Common Kernel/GKI KMI and vendor modules remain device-specific |
| Raspberry Pi | Proposed arm64 Linux device | Reviewed `apt` package candidate | Board firmware and boot chain are separately owned and model-specific |

The model includes `bootOwnership`, `kernelSeparation`, `devicePermissions`, and `packageAndLicense`, yielding sixteen **unverified** machine-profile cells. A Debian/Ubuntu-based **application bundle or curated package set** is the sane first deliverable, not a new bootable Debian/Ubuntu derivative. `LumoOS/LuHm-OS` is the user's own proposed brand, not an official recognized Ubuntu flavor, Linux kernel port or Debian project.

Android GKI is based on upstream Linux LTS plus Android-specific kernel changes; the KMI separates generic kernel code from vendor modules for supported devices. **A unified firmware manifest is possible; a universal, safe, flashable BIOS across Samsung/PC/Pi is not**. No `apt`, kernel configuration, image build or real device permission occurs.

References: https://source.android.google.cn/docs/core/architecture/kernel and https://www.debian.org/derivatives/index.html and https://ubuntu.com/legal/intellectual-property-policy

## 3. Open R synthetic mathematical tuning

`tools/rSyntheticTuning.R` uses **base R only**, needs no CRAN package downloads, and considers at most sixteen integer parameters on a synthetic quadratic loss `(parameter-target)^2 + 0.1 * parameter^2`. The Python twin `tools/rSyntheticTuningGate.py` independently computes the same test case and validates the *actual stdout* of a separate Rscript execution. Source checks alone never claim R executed; the dedicated CI action reports R/Python parity if the R job passes.

This creates a learning and mathematical **candidate-weight** lane for a future agent planner, not a credential brute-force system. No shell command generation, unbounded search, dangerous stress/voltage tuning, live kernel writes, AI model training or hardware benchmark is authorized. R itself is GPL-2 | GPL-3; using `Rscript` as a separate executable doesn't automatically relabel the LuHm repository's current GPLv3 source as Apache-2.0.

Official R licensing and scripting references: https://www.r-project.org/Licenses/ and https://search.r-project.org/R/refmans/utils/html/Rscript.html

## Three source mutations, shared CAST authority

`doctrine/finalThreeMachineMutationsV1.json` binds three proposed mutations with four checks each. All conform to the existing four typed data lanes, the two-track Professor↔Lum and Lum↔orchestration presentation, source SHA locks, hard STOPs and owner approval gates. The composite `tools/finalThreeMachineGate.py` verifies **three 4×4 matrices = 48 proposal cells**, not 48 active workers.

The draft harness registers source-only `luhm_final_three_machine_status` and `luhm_synthetic_r_tuning_plan`, but no installed plugin mount or live second conversation is proven. The company-wide agent quarantine remains in effect and cannot be lifted by an R fit or hexadecimal identifier.

Local commands from repository root:

```sh
python tools/retroTileTextCodec.py
python tools/portableOsRecipeAudit.py
python tools/rSyntheticTuningGate.py --audit
python tools/finalThreeMachineGate.py
python -m unittest discover -s tests -p 'testRetroTileTextCodec.py' -v
python -m unittest discover -s tests -p 'testPortableOsRecipeAudit.py' -v
python -m unittest discover -s tests -p 'testRSyntheticTuningGate.py' -v
python -m unittest discover -s tests -p 'testFinalThreeMachineGate.py' -v
Rscript tools/rSyntheticTuning.R --self-test
Rscript tools/rSyntheticTuning.R --self-test | python tools/rSyntheticTuningGate.py --verify-stdin
```

The focused GitHub workflow `.github/workflows/final-three-machine-mutations.yml` executes the Python tests and (after installing R) verifies **actual base-R and Python synthetic parity**. No host mutation or release is performed. Real device evidence, rights clearances and explicit Professor approval remain required for any production CAST promotion.

# LuHm-OS Machine Forge | CPU-to-HPC source-only architecture pass

**State:** Draft GitHub source, no boot image, firmware flash, hardware connection or accelerator benchmark.

## Four families crossed with four machine layers

| Family | CPU / ISA | Firmware model | Memory and device system | AI / accelerator |
|---|---|---|---|---|
| x86-64 | Intel/AMD; specific CPU extensions differ | UEFI, EDK II/OVMF, coreboot candidates; Intel FSP restricted binary | DDR, PCIe, USB; NUMA model-specific | CPU default, OpenVINO/ROCm only if device proven |
| Arm64 | Samsung/Qualcomm/Apple/Ampere/Raspberry Pi variants | TF-A where applicable; vendor-controlled phone boot chains | LPDDR/DDR, SoC interconnect, device tree/ACPI | CPU default; vendor APIs after permission |
| RISC-V RV64 | ISA + ratified extensions per processor | OpenSBI, board-specific U-Boot/EDK II | board-specific RAM and buses | CPU default; vector/AI support unverified |
| POWER ppc64le | IBM/OpenPOWER | Hostboot, OPAL/skiboot, BMC | server RAM, NUMA, accelerators per node | HPC candidate only |

The **four audited layers** are `isaCpu`, `firmwareBoot`, `memoryIo`, and `acceleratorAi`: 16 cells, none physically proven. ISA family names are not interchangeable BIOS vendors. More architectures can be considered later only with new reviews and tests.

## Typed hexadecimal and sorting weights

The machine source contract `doctrine/machineFourArchitectureForgeV1.json` preserves each numeric value's **kind, width, meaning and byte-order warning**. USB/PCI vendor/product IDs use four lowercase hexadecimal digits; CPUID leaves eight; IPS record offsets six; semantic GUIDs 32; Git SHA-1 IDs 40; SHA-256 digests 64.

`kind:fixedWidthHex` can be sorted numerically *within one type* without losing leading zeroes. Do not compare PCI and USB IDs as the same device key. Do not infer firmware ABI endianness from a CPU's name. UEFI GUID text and GUID binary storage use different layout rules. Memory capacities are integers in **decimal bytes**; Node.js accepts them as decimal strings to avoid rounding above 2^53.

Source contract declares prospective evidence weights **16 source / 8 licensing / 4 device-match / 2 runtime / 1 rollback**. Those are a future evidence-ranking rubric, **not real performance scores or permission**. Claims without independent receipts remain unverified.

## Firmware and license walls

EDK II has a mainly BSD-2-Clause-Patent code base with exceptions; coreboot distinguishes open code and vendor binaries. Intel FSP is a binary silicon-initialization interface, not Intel source code. Arm TF-A is BSD-3-Clause, RISC-V OpenSBI BSD-2-Clause with notices, and OpenPOWER skiboot has Apache-2.0 source. Board-specific update capsules, bootloader images, silicon patches, drivers and private OEM sources remain subject to their own owner/device/license checks.

LuHm's repository root is **GPLv3**. New Apache-2.0 components require independent authorship and component notices; external GPL and licensed vendor code cannot be blanket-relicensed.

`fwupd` and LVFS emphasize firmware signatures, hardware manufacturer IDs and update controls. **LuHm does not download OEM BIOSes, apply firmware patches or issue updates**. Neither a matching hex code nor a Git checksum is signing authority.

## Separate IPS patching lane

`tools/machineFourArchitectureAudit.py` validates synthetic homebrew IPS patch headers (`PATCH`, 24-bit offsets, literal/RLE entries, `EOF`) in memory with strict bounds. It reports only offset/count/hash metadata. It does not open or modify a ROM, firmware image or real file. BPS and PPF are documented **future research lanes**, not implemented.

Use rights-approved original homebrew material for later offline translation experiments. Delisted software does not automatically grant reuse or publication rights.

## Portable architecture, not a universal kernel

GitHub retains exact source; Python and a private npm module perform deterministic normalization; SQL holds typed identifiers and metadata. The mobile app stays lightweight. A potential server or supercomputer worker would require per-architecture builds, observed RAM/NUMA topology, actual GPU/NPU provider capabilities and real performance receipts. No future architecture is marked supported merely because it is listed.

Test source:
```sh
python tools/machineFourArchitectureAudit.py
python -m unittest discover -s tests -p 'testMachineFourArchitectureAudit.py' -v
npm test --prefix packages/luhm-canon-registry
```

References: https://github.com/tianocore/edk2 · https://doc.coreboot.org/ · https://github.com/ARM-software/arm-trusted-firmware · https://github.com/riscv-software-src/opensbi · https://github.com/open-power/skiboot · https://lvfs.readthedocs.io/en/latest/security.html

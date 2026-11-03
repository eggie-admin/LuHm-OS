# LuHm-OS firmware archaeology: Odin, Heimdall, Doom9, Apple restore
Status: RESEARCH_PROPOSAL_ONLY; no flash, unlock, bypass, deployment or production mutation.
Purpose: learn firmware file formats, verified boot, recovery and driver abstraction to design safe hardware adapters.

## Evidence and limits
- Heimdall upstream (MIT): https://github.com/Benjamin-Dobell/Heimdall ; describes Samsung Loke/Odin 3 protocol over USB via libusb, PIT mapping, Linux/macOS/Windows. Historical device support is not proof of current Samsung tablet compatibility.
- Samsung Odin: proprietary service/firmware-flashing tool; distinguish signed firmware provenance, model/region/bootloader revision, BL/AP/CP/CSC package structure. Do not redistribute proprietary firmware or tool binaries.
- Doom9 archive: https://forum.doom9.org/archive/index.html ; verified subject areas are video capture, codecs, AviSynth, VapourSynth, VirtualDub and FFmpeg. It is NOT established as an authoritative Samsung/iPhone firmware unlocking forum. Borrow its reproducible media tooling practices for studio only.
- Apple Platform Security: https://help.apple.com/pdf/security/en_US/apple-platform-security-guide.pdf ; DFU/Recovery restores rely on Apple-signed firmware and secure boot. Activation Lock and passcode security are not bypass objectives. Historical iPhone unlocking techniques are context only, not an operational target.
- Device-specific compatibility and official OEM documentation required before any hands-on recovery.

## Four-by-four research matrix
Rows: Samsung Odin/Heimdall; Apple DFU/IPSW; Linux UEFI/fwupd; media/binary tooling.
Columns: boot trust/signatures; partition/container/hex format; transport/driver; restore/rollback.
Record source URL, license, date, device/OS scope, verification, uncertainty, and non-destructive test receipt per cell.

## Read-only binary laboratory
1. Use only openly licensed synthetic fixtures or user-owned legally obtained images; hash SHA256 and record byte length.
2. Inspect magic bytes, endianness, offset bounds, checksums, compression, archive manifest, signature metadata without altering partitions.
3. Parse PIT-like layouts in synthetic fixtures only; validate overflow, truncation, duplicate partitions and alignment.
4. Model iOS IPSW archive and signed-manifest structure conceptually; do not imply user-replaceable Apple boot components.
5. Produce a typed JSON device-capability manifest; no unique hardware IDs, private art or credentials.
6. Build read-only adapters for Android properties, Linux sysfs/udev, and approved user-space USB metadata. Do not require root or flashing.
7. Test degraded capability paths: unavailable GPU, no firmware metadata, unsupported chipset, unplugged USB, low RAM.
8. Keep the real firmware/OEM driver chain intact; hardware abstraction means application independence, not physically removing vendor dependencies.

## Escalation
0: Canon/source/consent; 2x2: boot+binary+transport+recovery; 4x4: 16 documented cells; 8x8: model/driver compatibility and recovery simulations; 16x16: fault injection only in sandbox.
CAST Bridge requires tested adapter, provenance receipts, exact SHA, rollback and owner review. Crown STOP.

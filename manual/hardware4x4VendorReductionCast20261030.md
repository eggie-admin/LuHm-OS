# Hardware 4x4 vendor reduction / CAST candidate
Baseline parent: a808031070f57295b82999a58c679f3bff6542ee. Scope: source-only, no hardware writes.

| Layer | Samsung Lite | Antenna/phone proxy | Raspberry Pi | Local/remote Linux |
|---|---|---|---|---|
| Boot/firmware | Android build, verified boot, vendor patch | modem/baseband version, regulatory boundary | board, EEPROM, boot order | UEFI/GRUB/VM image |
| Kernel/drivers | stock Android kernel, HAL | Bluetooth/Wi-Fi/USB transport | distro kernel, firmware, DT overlays | kernel, udev, modules |
| Device interfaces | camera/mic/Bluetooth enumeration | permissioned link health | USB, camera, ALSA, BT | ALSA/PipeWire, V4L2, network |
| Runtime/receipts | Gradle client and capability JSON | proxy API and latency receipts | headless service, SQLite | Flask/API, systemd, SQL |

## Reduction policy
Prefer existing kernel and OS interfaces rather than introducing vendor SDKs. Preserve OEM proprietary boundaries; do not copy firmware or claim Apache-2.0 licensing. Use standard V4L2, ALSA/PipeWire, BlueZ, sysfs/udev, SQLite and HTTP JSON where supported. Each dependency removal requires evidence of no lost hardware functionality, measured before/after size and startup latency, and a rollback plan. Never remove bootloader, driver, radio or security update packages on a live device without explicit device-specific plan.

## Evidence schema
For each cell record platform, exact source SHA, hardware model, OS/firmware versions, interface IDs (redacted), vendor/driver source and license, permission scope, read-only test command, expected outcome, actual outcome, elapsed_ms, peak_rss_kib, and unknown reason. Keep unknown distinct from fail.

## Candidate test plan
- Synthetic JSON schema tests for 16 cells and missing-evidence rejection.
- Linux read-only `uname -r`, `lsusb`, `lsblk`, `systemctl --failed`, `ip -brief link`, `v4l2-ctl --list-devices` where installed; no changes.
- Pi: `cat /proc/device-tree/model` and `vcgencmd bootloader_version` where supported, no EEPROM updates.
- Android: owner-approved read-only settings/ADB build properties; no adb shell mutations.
- Offline mock proxy disconnect/reconnect and SQL transaction rollback.
- No unattended firmware flashing, kernel upgrade, pairing, network reconfiguration, cloud charges, signing, publishing or Crown promotion.

## References
https://source.android.com/docs/security/features/verifiedboot
https://developer.android.com/guide/topics/connectivity/bluetooth
https://www.raspberrypi.com/documentation/computers/raspberry-pi.html
https://www.kernel.org/doc/html/latest/userspace-api/media/v4l/v4l2.html
https://www.bluez.org/
https://www.alsa-project.org/wiki/Main_Page
https://www.sqlite.org/docs.html

## CAST gate
This is a proposed evidence contract, not an operational hardware certification. Gate stays blocked until actual device receipts, license provenance, benchmark comparison, independent review, and signed release artifacts.

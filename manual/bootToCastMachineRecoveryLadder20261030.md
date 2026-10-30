# LuHm-OS local/remote/AI/hardware boot-to-CAST diagnostic ladder
Date: 2026-10-30. Source base: 360381ef34ff8e38f3f3b4cee6241121f2fbb27b. This is a source-only operator checklist, NOT a deployment receipt.

## Platform-specific boot truth
- x86 UEFI/BIOS Linux: inspect firmware boot entries, ESP, GRUB (if installed), initramfs, kernel cmdline, filesystem UUIDs and systemd. GParted is an optional offline partition editor, not a boot dependency. Never repartition automatically.
- Raspberry Pi: inspect model/revision, EEPROM bootloader (model-dependent), firmware/config.txt, cmdline.txt, rootfs, kernel, power, USB and networking. Do not assume GRUB or GParted is present.
- Samsung Android: inspect model, One UI/Android build, bootloader lock state, vendor firmware and Android Verified Boot. No rooting, flashing, partitioning or OTA operations without device-specific approval and backup.
- Remote VM: inspect provider boot console, image, attached volume, rescue/rollback path and managed TLS. No cloud provisioning or billable calls from this checklist.

## 4×4 machine matrix
Rows: boot; OS; services; storage. Columns: local; remote; AI; hardware. Every cell must record: exact host/device ID (redacted in public receipts), source SHA, version, owner, evidence path, pass/fail/unknown, rollback.
- Boot: GRUB/UEFI; VM console; agent startup gate; Pi EEPROM/Android bootloader.
- OS: kernel/systemd; remote OS; isolated model runtime; vendor drivers.
- Services: apt/npm/Flask; API/TLS/proxy; Lum disabled-by-default orchestration; USB/Bluetooth/camera/mic.
- Storage: partition/filesystem; remote backup; SQL agent receipts; physical disk and flash wear.

## 4×4 delivery matrix
Rows: source; build; security; performance. Columns: local; remote; AI; hardware.
- Source: exact Git SHA and SBOM, immutable manifests, provenance, firmware provenance.
- Build: offline host smoke test, remote image dry-run, mocked agent contract, Android/Java/Gradle artifacts.
- Security: least privilege, TLS and firewall, no model tool escalation, verified boot and rollback.
- Performance: boot time/peak RSS, API p95, mock agent latency, camera/mic/antenna throughput with device authorization.

## Read-only operator commands (run only on the intended host)
```sh
uname -a
cat /etc/os-release
systemctl --failed --no-pager
lsblk -o NAME,SIZE,FSTYPE,MOUNTPOINTS
findmnt /
ip -brief address
ss -lnt
python3 --version
node --version
npm --version
java -version
dpkg-query -W -f='${binary:Package} ${Version}\n' 2>/dev/null | head -80
```
Do not execute host commands via a cloud agent or on a user's device without separate permission and confirmed target. Commands can expose identifying information; redact receipts.

## SQL machine-human boundary
Propose SQLite-first schema: device_capability, firmware_observation, service_health, job_request, job_receipt, audit_event, schema_migration. All observations timestamped with source and trust level. Require foreign keys, transaction rollback, migration dry-runs, integrity_check, backup restore, and no secrets in logs. No live DB migration authorized by this document.

## Orchestration boundary
One local coordinator with mock adapters and capability-scoped workers; Lum roles remain inactive. No autonomous shell, paid cloud, device flash, key access, publishing or Crown promotion. Separate proposal, human approval, execution and verification.

## Readiness gates
1. Repo source inventory (APT/npm/Python/Gradle/SQL/network/firmware references) complete.
2. Dependency license files and third-party notices verified; existing GPL preserved. New Apache-2.0-only modules must have ownership evidence.
3. Offline reproducible builds, unit and negative tests, and exact-SHA CI receipts.
4. Owner-authorized device observations for Samsung Lite, antenna proxy, Pi and remote host.
5. Signed artifacts, rollback test, independent review and explicit promotion decision.

## Documentation
- Debian admin: https://www.debian.org/doc/manuals/debian-reference/
- GRUB: https://www.gnu.org/software/grub/manual/grub/
- GParted: https://gparted.org/documentation.php
- systemd: https://www.freedesktop.org/software/systemd/man/latest/
- Raspberry Pi boot: https://www.raspberrypi.com/documentation/computers/raspberry-pi.html
- Android Verified Boot: https://source.android.com/docs/security/features/verifiedboot
- Android build: https://developer.android.com/build
- Netplan: https://netplan.readthedocs.io/
- npm ci: https://docs.npmjs.com/cli/commands/npm-ci/
- Flask: https://flask.palletsprojects.com/
- SQLite: https://www.sqlite.org/docs.html

Next smallest safe action: source-only inventory and synthetic SQL/firmware fixtures, then PR CI. No claims of firmware readiness or deployment until device-specific receipts exist.

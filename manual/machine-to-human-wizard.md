# LuHm-OS: Project Premonition | Machine-to-human wizard

**Scope:** Mutation ② of the final five-part architecture sequence. Status is a **read-only source candidate**, not a Samsung provisioning procedure.

## Four ordered layers
1. **Machine:** identify architecture, operating-system kernel, memory-page size and logical CPU count; optionally list redacted Linux block devices.
2. **Vendor:** classify Samsung Android/other Android/Linux/Windows/macOS, preserve vendor security boundaries and identify unknown boot evidence.
3. **Services:** plan a minimum set of tools (Python, SQLite, npm, MariaDB, NGINX, DNSmasq, Godot, Blender) only where needed. No package installation is performed.
4. **Human:** show the smallest next action and propose optional authenticated remote escalation. No background daemon, storage writes or bootloader changes.

## Operator use

```bash
python3 tools/machineToHumanWizard.py --json
```

On a controlled **Linux desktop**, `--include-disks` optionally reads a redacted `lsblk` listing. It never opens a block device or formats partitions. On Android, `--include-disks` is ignored and only allowlisted non-sensitive `getprop` values are read when available. Hardware properties that Android does not expose to an unprivileged app remain unknown.

For CI and rehearsal use a JSON fixture:
```bash
python3 tools/machineToHumanWizard.py --fixture /path/to/synthetic-host.json --json
```
Fixture mode is explicitly marked as synthetic, not physical hardware proof.

## Why GParted and Rufus are separate operator tools
- **GParted** is a Linux disk/partition editor; operations such as repartitioning and resizing can be destructive. [Official GParted manual](https://gparted.org/display-doc.php?name=help-manual), [GParted Live](https://gparted.org/livecd.php).
- **Rufus** is a Windows bootable USB creation tool. Target USB drives are reformatted. [Official Rufus FAQ](https://github.com/pbatard/rufus/wiki/FAQ), [Ubuntu's Rufus instructions](https://ubuntu.com/desktop/docs/en/latest/how-to/create-a-bootable-usb-stick/).
- **Samsung Android** retains its vendor/kernel/Knox verified-boot chain; external x86 media and partition tools are not a way to install a custom Android kernel. [Android Verified Boot documentation](https://source.android.com/docs/security/features/verifiedboot).

**Never treat GParted or Rufus as implicit end-user APK dependencies.** If actual disk or boot media changes are requested later, use a separate, explicitly approved workflow with drive verification, backup, rollback, supported host, physical evidence and human confirmation.

The wizard does not invoke either program and never uses `sudo`, destructive file operations, device flashing, public ports, or third-party installation. It is designed to prevent unnecessary Termux and machine-layer experimentation while we focus on the artist-first game and video application.

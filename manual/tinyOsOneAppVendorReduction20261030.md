# Tiny-OS to one-app vendor reduction: source evidence matrix
Date: 2026-10-30. Source-only candidate. No live hosts, builds, SDKs or networking mutated.

## 4x4 research ladder
| Platform | Official docs / quickstart | Upstream source to inspect | License boundary | First safe proof |
|---|---|---|---|---|
| Debian minimal | https://www.debian.org/doc/ | https://salsa.debian.org/apt-team/apt ; https://git.kernel.org/ | Mixed GPL and package-level licenses | offline dpkg/apt inventory |
| Alpine | https://docs.alpinelinux.org/ | https://gitlab.alpinelinux.org/alpine/aports | Mixed; musl MIT, BusyBox GPLv2 | isolated image footprint |
| Buildroot | https://buildroot.org/docs.html | https://gitlab.com/buildroot.org/buildroot | Buildroot GPLv2; packages independent | disposable QEMU image |
| Yocto/Poky | https://docs.yoctoproject.org/ | https://git.yoctoproject.org/poky | Recipe/package-specific | reproducible sandbox build |

## Four implementation surfaces
1. Local garage Linux/Pi: kernel, boot, GRUB/GParted recovery, network manager, Python 3, SQLite, studio tools.
2. Samsung Android: stock kernel/OEM firmware; supported Android SDK adapters only, no root assumption.
3. Remote: smallest maintained Linux VM, TLS, one reverse proxy, bounded API and rollback.
4. Browser/mobile: standards-first offline HTML/JS, Firefox/Chromium/WebView, platform-specific packaging.

## One AI, one app contract
Canonical identity: eggie-admin/LuHm-OS. One human-authorized coordinator (Lum), one bounded mini-agent lane initially, then 1->2->4 only with proven queue ownership, cancellation, idempotency and receipts. All actions require typed JSON schema, explicit capability, exact source SHA, SQL transaction receipt and no self-approval. Base44/Base64 are encodings, never security boundaries.

## Four languages
Python3: stdlib API and audit where practical.
SQL: SQLite STRICT with migrations and foreign keys; never a public SQL admin.
JavaScript: actual import graph and lockfile; prefer browser-native APIs before duplicate libraries.
Java/Kotlin: Android adapter only when SDK needs it; no Tomcat by default.

## Vendor rip checklist
For each candidate: official manual, upstream repository and tag, historical import/patch provenance, SPDX and NOTICE obligations, transitive dependencies, real usage evidence, safe alternative, offline test, rollback and performance receipt. Never copy WordPress/phpMyAdmin code without specific compatible license and attribution review. Apache-2.0 preference is not blanket relicensing; existing LuHm GPL-3.0-only remains.

## Kernel and networking boundary
GRUB and GParted apply to suitable PC/Linux recovery workflows, not Android boot chains. Netplan only on hosts where it owns configuration; require console fallback and staged rollback. apt is the package manager; aptitude, Synaptic and tasksel are optional frontends/workflows, not mandatory extra layers.

## 16-step controlled pass
inventory -> pin SHA -> collect docs -> inspect upstream tag -> scan imports -> classify vendor -> check license -> check CVEs -> map platform -> map schema -> isolate adapter -> negative tests -> benchmark -> rollback rehearsal -> independent review -> release decision.
Repeat across four platforms, not as 500^4 concurrent mutations.

## Explicit STOP
No main merge, OS image flashing, network apply, live SQL migration, remote agent activation, plugin publication or production deployment from this research packet. All need exact-artifact evidence and separately verified release gates.

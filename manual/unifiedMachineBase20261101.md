# One-machine LuHm base: inventory → scoped services → studio → client

**Status: PROPOSED SOURCE ONLY.** This extends machine draft PR #487 on
`main` anchor `f0cb6ee54066b490c0e80efc2c96200fec76ee2d`. Do not
merge blindly with other machine/CI/SQL proposals (#477-#486, #490, #491).
The current devcontainer is a heavy **studio**; it is not the Android runtime,
a Raspberry Pi boot image, a secure production VM or a replacement kernel.

## Four profiles, one architecture

| Profile | Minimum | Opt-in | Explicitly not required |
| --- | --- | --- | --- |
| Linux headless | Distro-supported kernel, Python 3 stdlib, SQLite for metadata | FFmpeg worker, reviewed proxy | MariaDB, Apache, Certbot, GParted, Java/Gradle |
| Linux studio | Headless base, npm/JS build lane and FFmpeg | Blender, Godot, MariaDB via local UNIX socket, proxy | GParted and Certbot as hidden background services |
| Raspberry Pi desktop | Supported Pi OS/kernel/firmware, HTML/JS and Python/SQLite | Small FFmpeg local worker | Privileged database server, autopartition, cloud signup |
| Android/Samsung client | Local static HTML/JS assets in the existing signed app | *None enabled by default* | Python daemon, SQL server, browser proxy, desktop disk tools |

The Android **build** independently uses Java/Kotlin/Gradle and npm to
package static assets; the APK does not run Node, Gradle, MariaDB or NGINX.
Keep Java/Kotlin pinned to the existing Android Gradle plugin and test exact
compile/ABI/signer when a release candidate exists. Optional AI/model routing
is the already-existing capability-first API spine. It is not an unguarded
daemon and is **not** activated by defining the source profile.

## What the requested mutations actually mean

- **Apache httpd → NGINX** means choosing a different server product and
  reviewing virtual-host routing, `mod_*` features, access control, proxy
  headers, TLS, HTTP/2, MCP streaming, redirects and rollback. No automated
  regex config translation; use at most one proxy on a proven host. The
  project has existing Render-managed TLS and may not need *either* proxy.
  Canon `networkSpineV1.json` records an Apache host preference, while the
  devcontainer has an optional unstarted NGINX. Resolve by host/route receipts,
  not by installing both.
- **MySQL → MariaDB** is a database migration between related but diverged
  products. Existing source uses socket-only MariaDB for optional Linux
  studio work, whereas machine receipts can use SQLite in memory.
  Before any live migration, verify exact source/target versions, authentication
  plugins, JSON data type/semantics, SQL mode, collations, stored routines,
  backup/restore and rollback. Never connect to a production database for a
  speculative "translation."
- **GParted** is an operator-controlled disk recovery utility only. Disk
  selection, offline backup, partition-resize preview and physical approval
  must precede any actual write. It is never a startup dependency.
- **Certbot** is an ACME client for an approved origin one operates. It can
  modify Apache/NGINX config; it is not needed for Render-managed TLS.
  Existing `certbotWorkspaceSymlinkAudit.py` reads path metadata without
  opening keys, issuing certificates or proving renewal.
- **GNU/Linux kernel, BIOS/UEFI, Raspberry Pi firmware and Android
  vendor boot** are separate authorities. No hexadecimal register editing,
  firmware flashing, GRUB changes or root browser sandbox bypass.

## One deterministic orchestration chain

`inventory → sanityCheck → test → propose → [operator live change] →
[owner sign/deploy/CAST]`

The first four steps are eligible for bounded, existing GitHub CI source
automation. They do not start server daemons or execute external AI workers.
The final two steps are deliberately **not** automatically promoted. No
unlimited recursive retries, secret-bearing logs or unapproved bots.

**Reusable toolchain already present:**
- Python 3: `tools/machineToHumanWizard.py`, `tools/unifiedMachineBaseAudit.py`.
- SQL: SQLite stdlib in-memory source receipt; `tools/typedSqlStub.py`
  remains separate and is not replaced.
- JavaScript/npm: `frontEnd/package-lock.json`, static cockpit and
  exact-version frontend audits, build-time only.
- Java/Gradle: `androidWeb3Plugin/build.gradle.kts`, Android package gate only.
- Creative tools: separate Godot, Blender and FFmpeg source/CI and runtime gates.
- AI/role names: `doctrine/luhmAiControlPlaneV1.json`, company quarantine
  still applied. Names alone do not prove agents running.
- Proxy/TLS: `doctrine/networkSpineV1.json`, managed-host TLS first.

## Reproducible read-only checks

From the exact checked-out commit:

```bash
python3 -m unittest discover -s tests -p 'testUnifiedMachineBaseAudit.py' -v
python3 tools/unifiedMachineBaseAudit.py --profile linuxHeadless
python3 tools/unifiedMachineBaseAudit.py --profile linuxStudio
python3 tools/unifiedMachineBaseAudit.py --profile raspberryPiDesktop
python3 tools/unifiedMachineBaseAudit.py --profile androidClient
```

The existing machine-to-human GitHub workflow runs these tests and emits a
temporary per-profile evidence packet. This checks the source and executes
an **in-memory synthetic SQLite hash test**, not an on-disk database, real
MySQL/MariaDB translation, Java/Gradle compilation, a real NGINX proxy,
certificates, disk edits or model inference. Local CI success must be
rechecked at the final exact candidate SHA.

## Remaining physical gates

A validated Docker image (pinned by digest), actual boot/kernel/GPU and
Raspberry Pi kiosk proof, authenticated browser-to-backend call, real
Java/Gradle Android build, MariaDB compatibility rehearsal if needed, HTTPS
host provenance, owner signing and Samsung/Google Play installation evidence
are independent. Only perform operations that the current user authorized,
and keep `CROWN STOP` until the proper signed exact-artifact release gate.

## Primary upstream guides

- Apache HTTP Server docs: https://httpd.apache.org/docs/2.4/
- NGINX architecture: https://blog.nginx.org/nginx-architecture
- MariaDB migration and compatibility: https://mariadb.com/docs/server/server-management/install-and-upgrade-mariadb/migrating-to-mariadb/moving-from-mysql
- Certbot plugin safety: https://eff-certbot.readthedocs.io/en/stable/using.html
- GParted manual: https://gparted.org/display-doc.php?name=help-manual

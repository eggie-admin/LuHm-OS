# LuHm OS Termux + Ollama + X11 Headless Hardening

Status: **GREEN policy candidate / runtime proof pending**

Authority: **Professor**

Source law: **AI proposes. Policy authorizes. CI proves. Human promotes.**

## 1. Boundary

Termux is a separate operator/service plane. It is **not** an execution bridge inside the LuHm OS Android APK. The Android runtime remains native Godot and keeps its current release boundary.

Hard rules:

- no root login
- no `root-repo`
- no SELinux disabling
- no public service bind
- no remote shell execution
- no secrets in source, logs, screenshots, CI artifacts, or doctrine
- no AI-initiated package upgrades or service enablement
- no hidden background GUI dependency
- consequential mutations require Professor Crown approval

## 2. Headless first

The enterprise baseline is headless.

1. Run the read-only operator doctor.
2. Start Ollama on `127.0.0.1:11434` only.
3. Start optional Crown-approved user services only when needed.
4. Start VNC only when a visual operator console is explicitly requested.

The system must continue functioning with VNC stopped.

## 3. Ollama

Ollama's local API does not provide local authentication. Therefore the security control is the trust boundary itself: loopback only.

Required baseline:

- `OLLAMA_HOST=127.0.0.1:11434`
- local models by default
- cloud models disabled by policy unless separately approved
- API keys never stored in repository files
- model pulls require human approval because they are large mutable downloads
- no reverse proxy, tunnel, wildcard bind, or LAN exposure in this lane
- default model keep-alive is short to reduce mobile memory pressure

## 4. X11 and VNC

Preferred enterprise baseline: TigerVNC from the Termux X11 repository.

Required baseline:

- display `:1`
- TCP endpoint `127.0.0.1:5901`
- `-localhost yes`
- authentication required
- password file private to the Termux user
- VNC starts on demand and stops when the operator is finished

Termux:X11 nightly may be useful for development, but it is not the enterprise baseline here. Any procedure requiring SELinux to be disabled is rejected by LuHm OS doctrine.

## 5. Termux app source

Never mix Termux app/plugin sources or signatures.

Preferred enterprise baseline:

- stable F-Droid source, or
- stable GitHub source

The Google Play branch is treated as **experimental**. If it is already installed, do not rip it out automatically. Probe it, inventory it, snapshot state, then migrate only through a separate Professor-approved change.

## 6. Security updates

No blind unattended `pkg upgrade`.

The sane update path is:

1. **Inventory**
   - `termux-info`
   - package manifest
   - configured apt repositories
   - Ollama version
   - active listeners
   - runit service state
2. **Snapshot**
   - package manifest
   - `$PREFIX/etc`
   - LuHm operator configs
   - service definitions
3. **Refresh metadata**
   - update repository metadata only
4. **Review**
   - list upgradable packages
   - review security-sensitive packages first
   - inspect upstream release notes when a daemon or runtime changes
5. **Crown gate**
   - Professor approves the upgrade set
6. **Apply**
   - perform package upgrade
7. **Verify**
   - operator doctor
   - Ollama loopback API smoke test
   - listener audit
   - VNC localhost audit if GUI is active
   - runit service check
8. **Seal**
   - record exact versions and hashes
   - preserve the receipt in doctrine

Automatic activity may check health and inventory. Automatic activity may **not** apply upgrades, change package repositories, enable services, migrate Termux sources, pull models, or expose ports.

## 7. Service supervision

`termux-services` / runit is the preferred supervisor when a persistent headless service is intentionally enabled.

Rules:

- service definitions live in the Termux operator plane, not the APK
- services default disabled
- enabling a service is a Crown-gated mutation
- no permanent wake lock by default
- logs remain local and private
- a sleeping Android process is not treated as proof of service failure

## 8. Runtime evidence gate

The hardening policy is not runtime GREEN until device evidence proves:

- Termux source/version
- exact package manifest
- no enabled root repository
- Ollama version
- Ollama listener is loopback only
- Ollama local API responds
- no unexpected public listener
- TigerVNC listener is loopback only when active
- VNC auth material exists with private permissions
- SELinux remains enforcing when observable
- service state is documented
- upgrade delta is documented
- post-update smoke tests pass

## 9. Operator scripts

- `operator/termux/luhm-termux-doctor.sh` - read-only health and listener audit
- `operator/termux/luhm-headless-ollama.sh` - foreground loopback-only Ollama launcher
- `operator/termux/luhm-vnc-start.sh` - on-demand localhost-only TigerVNC launcher
- `operator/termux/luhm-update-plan.sh` - inventory and update-plan generator; never upgrades packages

## 10. Status law

Policy GREEN does not mean runtime GREEN.

- **GREEN policy**: static doctrine and CI contract pass.
- **AMBER runtime**: device evidence is missing or incomplete.
- **GREEN runtime**: listeners, versions, service state, update receipt, and post-update smoke tests are all proven.

No policy file can self-promote the full LuHm OS release.

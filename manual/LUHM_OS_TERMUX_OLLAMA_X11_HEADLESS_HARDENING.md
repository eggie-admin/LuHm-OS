# KAI 9000 Termux + Ollama + X11 Headless Hardening

Status: **GREEN source policy / runtime proof pending**

Authority: **Professor**

Source law: **AI proposes. Policy authorizes. CI or deterministic probes prove. Human promotes.**

> Correction: this hardening lane belongs to **KAI 9000**, not the LuHm OS native Android runtime. The branch `hardening/termux-ollama-x11-headless-20260926` is quarantined and must **not** be merged into LuHm OS by implication.

## 1. Boundary

Termux is the KAI 9000 control plane. Ollama is its local inference lane. TigerVNC/X11 is an optional operator console. LuHm OS native Android remains a separate Godot runtime and receives no Termux execution bridge from this work.

Hard rules:

- no root login
- no `root-repo`
- no SELinux disabling
- no public Ollama, VNC or websockify bind
- no remote shell execution
- no secrets in source, logs, screenshots, CI artifacts or doctrine
- no AI-initiated package upgrades, source migration, model pulls or service enablement
- no hidden GUI dependency
- consequential mutations require Professor Crown approval

## 2. Headless first

The KAI baseline is headless.

1. Run the read-only Witching Hour doctor.
2. Take a local rollback snapshot after the first probe.
3. Start Ollama on `127.0.0.1:11434` only when requested.
4. Start optional Crown-approved KAI services.
5. Start TigerVNC only when a visual operator console is explicitly requested.
6. Re-run the doctor and seal evidence.

KAI core services must not depend on VNC.

## 3. Ollama

Required baseline:

- `OLLAMA_HOST=127.0.0.1:11434`
- headless operation without GUI
- local models by default
- no reverse proxy, tunnel, wildcard or LAN bind in this lane
- model pulls remain human-approved
- short default keep-alive for mobile memory pressure
- API/model inventory included in the runtime receipt

## 4. TigerVNC / X11

Preferred operator lane: TigerVNC from the Termux X11 repository.

Required baseline:

- display `:1`
- TCP endpoint `127.0.0.1:5901`
- `-localhost yes`
- private VNC password material
- starts on demand and stops when finished
- GUI failure must not break KAI headless services

Any path requiring SELinux to be disabled is rejected.

## 5. Termux source

Never mix Termux app/plugin signing sources.

Preferred enterprise baseline:

- stable F-Droid source, or
- stable GitHub source

An already-installed Google Play build is probed first and treated as experimental. No automatic removal or migration is authorized.

## 6. Security updates

No blind unattended package upgrades.

Sequence:

1. inventory
2. snapshot
3. refresh metadata only after Crown approval
4. review proposed upgrades
5. Crown gate
6. apply approved updates manually
7. restart only affected services
8. verify Ollama/VNC loopback boundaries and KAI health
9. record hashes and versions
10. seal

The Witching Hour update-plan tool never applies package upgrades.

## 7. Agent mesh

- **Lum**: boss/orchestrator
- **Kiri**: context and doctrine
- **Tetsu**: build and service contracts
- **Momo**: research and dependency freshness
- **Shiori**: conditional sanity/drift critic
- **Kugi**: deterministic executor only, never reinterprets scope

Max helper parallelism is 3. Recursive recruitment is off.

## 8. Ten-pass hard audit

1. source authority
2. project scope
3. runtime separation
4. Termux package/source identity
5. network binding
6. privilege boundary
7. headless service health
8. update and rollback
9. receipts and hashes
10. seal and save

Runtime GREEN requires no remaining unknowns, loopback Ollama proof, loopback VNC proof when active, non-root operation, rollback snapshot, KAI health receipts and sealed hashes.

## 9. Witching Hour local forge

The forge is under `kai9000/witching-hour/`.

```bash
bash forge.sh audit
bash forge.sh snapshot --crown
bash forge.sh ollama --crown
bash forge.sh vnc --crown
bash forge.sh update-plan
bash forge.sh play
```

The GitHub workflow may package and statically audit this forge. It cannot prove the phone's live Termux state.

## 10. Status law

- **GREEN source**: doctrine, scripts and GitHub forge build pass.
- **AMBER runtime**: device evidence is missing or incomplete.
- **GREEN runtime**: deterministic Termux probes prove all ten runtime gates.

A GREEN runtime receipt still does not merge, publish or promote anything. Human promotion remains separate.

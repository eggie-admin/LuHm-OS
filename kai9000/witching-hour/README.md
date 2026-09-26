# KAI 9000 Witching Hour Forge

This is the quarantined, local-first KAI 9000 Termux forge. It is **not** the LuHm OS native Android runtime and must not be merged into that runtime by implication.

## Doctrine

- Professor is Crown and final authority.
- Lum coordinates Kiri, Tetsu and Momo. Shiori is the conditional critic. Kugi is deterministic execution only.
- Termux is the control plane.
- Ollama is headless-first and loopback-only at `127.0.0.1:11434`.
- TigerVNC is optional, on-demand and localhost-only on display `:1` / `127.0.0.1:5901`.
- No root login, no SELinux disable, no public bind, no unattended major upgrade, no source migration, no embedded secrets.
- The local doctor may collect evidence and write receipts. It may not promote itself.

## Local forge

From the extracted GitHub artifact or a checkout of the quarantine branch:

```bash
bash forge.sh audit
```

That first pass is read-only apart from writing private local receipts under `$HOME/.local/state/kai9000`.

After the first probe, make a local rollback snapshot:

```bash
bash forge.sh snapshot --crown
```

Start the headless inference lane only when desired:

```bash
bash forge.sh ollama --crown
```

Start the optional GUI operator lane only when desired:

```bash
bash forge.sh vnc --crown
```

Generate an update plan without applying upgrades:

```bash
bash forge.sh update-plan
```

For the assisted toy/operator menu:

```bash
bash forge.sh play
```

## GREEN law

The GitHub forge can become **GREEN_SOURCE** when static policy and package assembly pass. Runtime stays **AMBER** until the Termux device receipt proves package/source identity, loopback listeners, Ollama API health, optional VNC boundary, non-root operation, rollback snapshot, KAI health and evidence hashes.

A deterministic runtime GREEN receipt is evidence, not self-promotion. Human promotion remains separate.

# Crown Cathedral 512 → 1024 → 1536 → 2048: Canon candidate

## Scope

Professor requested full Crown Cathedral continuation in bounded 512-scenario escalations. This stacked candidate builds on draft PR #512 and reuses the existing HEX-64 Insanus source-model engine; it does not duplicate its 2,048 cases. Each milestone is cumulative and recomputes all earlier scenarios from the same exact git SHA. A failed milestone prevents further advancement.

| Checkpoint | New scenario IDs | Added families | Cumulative |
| --- | --- | --- | ---: |
| 0x200 | 0x000..0x1FF | sanityCheck, audit, ingest, mutation | 512 |
| 0x400 | 0x200..0x3FF | test, apply, continue, deploy | 1,024 |
| 0x600 | 0x400..0x5FF | sourceIdentity, sandboxPrivilege, sqliteIsolation, binaryStorage | 1,536 |
| 0x800 | 0x600..0x7FF | vendorBudget, agentQuarantine, rollback, crownGate | 2,048 |

There are 16 families × 128 evidence/tier/authority cases. These are deterministic policy-decision assertions, NOT independent runtime tests, devices, source files inspected, security audits, or proof of production readiness. The existing HEX64 engine records 64 bytes per case, 128 KiB total. The new tool verifies every record's identity, field packing, SHA-256, allowed decision, stage/tier, no reserved-byte payload, and source-bound cumulative chunk hashes. A digest demonstrates integrity comparison, not authentication.

## Hard-audit companions

The exact-head GitHub CI workflow also runs the existing:
- 200-control system hard audit
- 16-cell machine loop and negative tests
- Titan 500 (200 system + 120 artist-first + 180 inventory/syntax controls)
- 15-agent quarantine and escalation source checks

These audits overlap. Do not sum their counts as distinct independent checks. Titan500 may surface known GAP and UNVERIFIED states, which remain open. Neither a model pass nor source CI proves Cloudflare build success, authenticated Google API use, Render deploy parity, actual Samsung/Godot gameplay, public art rights, APK signing, backup restore, private SQL migration, or live independent agents.

## Reproduce on exact source

    export LUHM_SOURCE_REF="$(git rev-parse HEAD)"
    for target in 512 1024 1536 2048; do
      python3 tools/crownCathedral512EscalationAudit.py \
        --source-ref "$LUHM_SOURCE_REF" --target "$target" \
        --output "build/crownCathedral512/checkpoint-$target.json"
    done

Stop immediately at a RED result. A new SHA resets all milestones. Other open branches (including #515–#523) remain separate candidates and must not be silently merged. This proposal is stacked on #512 so source reconciliation is explicit.

## Authority stop

Professor authorizes the research and candidate source-audit escalation. Source tests remain AMBER_SOURCE_ONLY and Crown STOP because Canon still requires exact-source promotion evidence, vendor/IAM/billing proof where applicable, live host/device proof, rights, and release signing. No cloud/DNS/SQL mutation, no paid provider calls, no production deployment, no public release, no agent unquarantine and no protected main merge in this workflow. Missing evidence remains UNKNOWN; never self-approve.

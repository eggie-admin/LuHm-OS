# Hex64 Insanus 2048: proposed CAST audit

## Scope and truth labels

A deterministic **policy-scenario audit** for LuHm-OS: Project Premonition.
It **does not** mean 2,048 independent unit tests, files inspected, code
paths exercised, CI jobs, devices tested or production controls verified.

This source-only proposal derives its authority from:

- doctrine/currentSourceTruthV3.json
- doctrine/everlastingCovenantV1.json
- doctrine/escalationKernelV1.json
- doctrine/companyWideOperationalQuarantineV1.json
- doctrine/soloStudioOperatingProfileV1.json
- doctrine/crownCathedralWebglCastV1.json
- tools/premonitionTitan500Audit.py (separate existing 500 audit, not re-run or replaced)

## Geometry

- One machine record is **0x40 = 64 bytes**, packed little endian.
- **0x10 = 16 distinct guardrail families** (stage IDs 0x0..0xF).
- **0x80 = 128 scenario combinations per family**.
- Total: **0x800 = 2,048 scenario assertions**.
- Evidence class uses 3 bits (8 states), escalation tier uses 2 bits
  (4 tiers), and authority class uses 2 bits (4 types).
- This is an exhaustive 8 x 4 x 4 **decision table in each family**.
- Total binary receipt length: **0x20000 = 131,072 bytes (128 KiB)**.

| Byte offset | Length | Field |
| --- | ---: | --- |
| 0x00 | 4 | ASCII LH64 |
| 0x04 | 1 | schema version |
| 0x05 | 1 | stage 0x0..0xF |
| 0x06 | 1 | operational tier 0..3 |
| 0x07 | 1 | model decision enum |
| 0x08 | 2 | case ID 0..127 |
| 0x0A | 2 | evidence/authority flags |
| 0x0C | 4 | global sequence 0..2047 |
| 0x10 | 4 | assertion-pass flag |
| 0x14 | 32 | SHA-256 of canonical JSON scenario + source ref |
| 0x34 | 12 | reserved (zero) |

Hashing provides integrity comparison, **not authentication or proof of external execution**.

## Stage families

0x0 sanityCheck; 0x1 audit; 0x2 ingest; 0x3 mutation;
0x4 test; 0x5 apply; 0x6 continue; 0x7 deploy;
0x8 source identity; 0x9 sandbox privilege; 0xA SQLite isolation;
0xB binary storage; 0xC vendor/budget; 0xD agent quarantine;
0xE rollback; 0xF Crown stop.

These are a *source-model verification grid* around the existing
eight-step covenant, not permission to execute every step.

## Continuation loop: stop conditions first

The four-beat interaction remains **hear -> resolve -> act -> verify**.
The four existing operational tiers remain 0..3; hex stage numbers
are audit family identifiers, not 16 new authorization levels.

    IF sourceRef changed OR scope changed:
        discard old GREEN; restart at sanityCheck
    ELSE IF evidence is RED, UNKNOWN, STALE, MISSING, CONFLICT:
        HOLD and identify smallest repairable blocker
    ELSE IF company quarantine applies to a requested worker:
        HOLD worker activation; continue independent read-only work
    ELSE IF operation is an authorized, reversible proposed-source task:
        act once -> verify exact head -> receipt -> continue
    ELSE IF a physical device, asset right, host mount, secret,
            signing identity, production deployment or public Crown
            is required without independently matching evidence:
        HOLD that boundary; retain safe candidate
    ELSE:
        close the smallest proved task, de-escalate tier when possible

When a deterministic failure is repairable: patch **one cause only**,
get a new sourceRef, repeat the covenant from sanityCheck. A tier increase
changes audit depth, never permission. At tier 3 with a blocker, hold.

### Root/admin/enterprise policy

- Root/admin are allowed for **isolated, ephemeral, offline test
  environments** if actually needed; sandbox authorization is not
  GitHub write permission or a provider IAM grant.
- Repo changes use the connected scoped GitHub capability and an exact
  task/source/scope envelope, not a root bypass.
- Public source with no stored sensitive personal data can still contain
  protected dependencies, compromised workflows and unlicensed media.
- Prefer local in-memory SQLite with parameter binding and rollback;
  never run this matrix against a live database.
- Never infer that a successful source-model check released workers,
  passed Samsung tests, signed an APK, published an app, or conferred Crown.
- No new provider spend, workflow, agent process or persistent server.

## Run / receipt

From a full Git checkout at the reviewed source ref:

    python3 -m unittest discover -s tests -p testHex64Insanus2048Audit.py -v
    python3 tools/hex64Insanus2048Audit.py --output-dir build/hex64Insanus2048

The runner emits a JSON scenario ledger and exactly 128 KiB of binary
records, with source SHA and explicit NOT-PROVEN runtime boundaries.
Outputs in build/ are generated receipts, not source changes.

Expected output on a compatible repo is SOURCE_MODEL_PASS only.
CI success at the exact PR head is a distinct required receipt before
source promotion. Existing Titan 500, WebGL build, vendor audit and
Samsung/Android tests must be run separately as applicable.

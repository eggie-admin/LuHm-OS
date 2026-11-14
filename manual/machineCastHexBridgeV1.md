# LuHm-OS CAST Bridge | hexadecimal AI JSON to machine SQL

**Status:** review-only, branch candidate. This document does NOT deploy a new
ChatGPT App, upgrade a real device, install phpMyAdmin, connect to production SQL,
change a Cloudflare domain, activate agents, authorize CAST, or modify GitHub main.

## The actual command layers

| Layer | Meaning | Contract |
| --- | --- | --- |
| Human | `CAST` | ASCII text, four letters |
| Wire notation | `0x43415354` | four ASCII bytes `43 41 53 54`, not an executable |
| Compact LuHm opcode | `0xC1` | newly proposed exact-case ID, **intent only** |
| Existing audit grid | `0x00..0x3F` per surface | 64 CAST coordinates, NOT opcode namespace |
| jQuery | `$.fn.luhmHexCastBridge` | explicit optional adapter, event only |
| JavaScript core | `buildLuHmHexCastManifest()` | bounded AI JSON payload |
| Python validation | `tools/machineCastHexBridge.py` | independently rechecks schema, source and transition |
| Machine SQL | `castOpcodeRegistry`, `aiManifestReceipt`, `castIntentReceipt` | source-bound candidate receipts, no dispatch |
| Production boundary | independent owner-authored CAST | never inferred from hexadecimal, JSON or SQL |

Existing project identities remain separate and case-sensitive:
public **LuHm-OS**, internal `luhmOs`, legacy package `LuHmOS`,
existing `$.fn.luhmCockpit` and `$.fn.luhmParallax`.
The new `$.fn.luhmHexCastBridge` is **opt-in**, does not auto-register
or replace existing plugins, and emits the existing
`luhm:cast:intent` event only. It has **no network fetch, SQL, eval,
shell or release authority**.

**Encoding is not authorization.** There is no hardware opcode or firmware
instruction corresponding to LuHm `0xC1`. A malicious model cannot invent
`0xC2` or change `LuHm-OS` casing to change its permissions.

## AI JSON manifest

The bridge uses the already existing
`doctrine/aiTaskManifestV2.template.json` fields, with only an additive
`machineBridge` subsection. Proposed strict
JSON Schema Draft 2020-12:
`doctrine/machineCastHexManifestV1.schema.json`.

Example is **synthetic**. The 40-digit `sourceRef` below is NOT a current
repository checkout and MUST fail an actual source-binding comparison:

```json
{
  "schema": "luhmOs.aiTaskManifest.v2",
  "status": "SOURCE_CANDIDATE",
  "providerId": "luhmOsLocal",
  "capabilityId": "machineCastBridge",
  "taskId": "machineCastReview",
  "sourceRef": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "scopeId": "machineSql",
  "inputRefs": [],
  "requiredOutputSchema": "luhmOs.machineCastHexBridgeReceipt.v1",
  "budget": {"maxRequests":1,"maxParallel":1,"maxPasses":1},
  "stopConditions":["scopeComplete","evidenceConflict","sourceMismatch","budgetExhausted"],
  "authority":{"mutation":false,"green":false,"crown":false},
  "responseRequired":["providerId","taskId","sourceRef","scopeId","responseId","outputRefs","claims","timestamp"],
  "machineBridge":{
    "schema":"luhmOs.machineCastHexBridgeIntent.v1",
    "displayName":"LuHm-OS",
    "asciiHex":"43415354","opcode":"0xC1","mode":"inspectCandidate",
    "fromStage":"castProposed","stage":"castBridge",
    "beat":"hear","tier":"technologyFastPath",
    "dispatchAuthorized":false,"machineSqlWritable":false
  }
}
```

The Python validator requires the externally supplied **exact checked-out
sourceRef** and reuses `tools/fnCastMatrix.py` to confirm the
`castProposed → castBridge` stage is legal. It invokes that existing
compiler with `voiceAccepted=False`. The resulting status is
`HOLD_SEPARATE_PROFESSOR_CAST`, not a CAST command or build.

The strict validator rejects:
wrong/mixed-case hex, alias collisions, nonexistent stages,
nonmatching source SHA, malformed task/scope names, unbounded budgets,
unexpected keys, duplicate JSON object keys, NaN, injected paths,
external input references, self-approved Crown/green/mutation flags,
and any attempt to permit dispatch or SQL writes.

## SQL architecture | capture facts, not the world

Use **one normalized machine metadata registry** with foreign keys,
indexed provenance and digest references. It should not become a
monolithic table of arbitrary untyped JSON or a private hardware-identifiers
warehouse. It is not a replacement for Git source, device firmware
or a binary file server.

The **existing machine schema** has
`sourceRevision`, `machineIdentity`, `deviceRecord`, `firmwareRecord`,
`namespaceRegistry`, `machineApi`, `artifactPointer`,
`evidenceReceipt` and `auditCoordinate`. The new additive schema has
`machineComponent`, `machineComponentLink`, `castOpcodeRegistry`,
`aiManifestReceipt`, and `castIntentReceipt`.

The proposed 29 component categories are CPU, GPU, memory, OS, kernel,
BIOS, UEFI, bootloader, firmware, driver, storage, filesystem, partition,
network, DNS, certificate, process, service, package, library, plugin,
API, model, runtime, container, VM, display, sensor, and media.

Only **pseudonymous, scoped machine keys** belong in the shared SQL layer.
Never import IMEI, real MAC address, disk serial, raw hardware ID, private
file content, SSH/TLS private keys, OAuth tokens, passwords, model weights,
private Drive IDs or original protected artwork into a public repo or
chat transport. A future authorized private machine collector must record
consent, collection scope, observed time, evidence and retention separately.

`machineComponentLink` describes permitted dependency relationships
between typed components. Public devices, firmware and service metadata
that are UNKNOWN should remain explicitly UNKNOWN.
SQL foreign keys, CHECKs, bounded JSON and test receipts cannot prove
that a real machine is healthy or that its firmware was verified.

### Why the existing typed four-lane SQL cannot simply be pasted in

`host/api/typedLanesV1.sql` already defines its own
`artifactPointer`, `aiManifestStream`, and scoped `streamEvent`.
The new machine registry also defines `artifactPointer` with
a different column contract. Directly combining the DDL would collide.
A real **single operational SQL DB** must reconcile these names through
a versioned migration, preserve legacy stream events and artifact references,
and prove read-back parity before any cutover. For now, GitHub stays the
Canonical source DB, SQLite is the disposable machine registry prototype,
and MariaDB/phpMyAdmin remains private review-only.

Never store "SQL source truth" without knowing which **authority dimension**
is meant:
- GitHub `main`: normative source code and versioned Canon.
- SQL after approved migration: current machine metadata/evidence projection.
- Google Drive: durable binary originals and artifacts.
- ChatGPT: conversation/working context, not operational SQL authority.
- Device: locally observed current firmware/runtime state, if separately proved.

## 512 escalation and verification

The existing `doctrine/machineSqlHex512EscalationV1.json` indexes
**8 domains × 4 CAST stages × 4 interaction beats × 4 tiers = 512**
SQL audit coordinates. It does NOT create 512 workers, 512 API requests,
or 512 distinct physical hardware tests. `0xC1` is outside the
`0x00..0x3F` coordinate range.

Re-run against the exact candidate branch with no database daemon:

```bash
python3 tools/machineSqlHex512Audit.py
python3 tools/machineCastHexBridge.py --self-test
node --test frontEnd/tests/machineCastHexBridge.test.mjs
SOURCE_REF="$(git rev-parse HEAD)"
node frontEnd/tools/emit-machine-hex-manifest.mjs "$SOURCE_REF" > /tmp/luhm-cast-hex.json
python3 tools/machineCastHexBridge.py --source-ref "$SOURCE_REF" \
  --manifest-file /tmp/luhm-cast-hex.json --synthetic-sql
```

These tests write only synthetic, disposable SQLite state; the emitted
`/tmp` file is a synthetic test fixture and not a durable database or
production receipt. phpMyAdmin and MariaDB do not run. The production
source-to-machine bridge, private admin auth, collector privilege,
dual-read legacy SQL migration, live firmware verification and the
ChatGPT host mount remain separately gated.

**Current authority boundary:** agent quarantine intact, Crown STOP,
no autonomous CAST, production SQL write or firmware operation.

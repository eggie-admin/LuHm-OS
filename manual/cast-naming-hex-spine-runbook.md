# LuHm-OS CAST Bridge | Four-by-four naming, hexadecimal identity and npm registry

**Scope:** exact GitHub source only. The Professor talks to Lum in the first thread; the second proposed mesh timeline uses the *same task/source/scope identity* and source-registered names. No independent chat thread or agent execution is created by this module.

## Four identity layers

| Name role | Canonical camelHump | Vowel-ripped alias | Explicit shorthand | Reversible UTF-8 hex |
| --- | --- | --- | --- | --- |
| Lum | `lum` | `lm` | `lu` | `6c756d` |
| Lum ↔ orchestration | `lumMesh` | `lmMsh` | `lmesh` | `6c756d4d657368` |
| Belldandy | `belldandySecretary` | `blldndyScrtry` | `bs` | `62656c6c64616e6479536563726574617279` |
| CAST | `castBridge` | `cstBrdg` | `cb` | `63617374427269646765` |
| Git commit source field | `sourceRef` | `srcRf` | `sr` | `736f75726365526566` |

**Source:** `doctrine/castIdentityHexRegistryV1.json`. The registered aliases are *explicit choices*, not an algorithmic vowel stripper. We caught a natural collision: `lm` fits the vowel-ripped name of Lum and might otherwise be the shorthand for Lum's mesh. `lmesh` resolves the conflict. Unknown or conflicting names are **VERIFY/STOP**. The canonical name and full human meaning are always recoverable by help.

The byte-hex layer represents the canonical identifier's original UTF-8 bytes exactly, using lowercase hexadecimal. It does not compress the string or serve as SHA-256, cryptographic proof, encryption, a publisher signature or permission. Git commits keep their independent exact 40-character source SHA identity; artifact evidence remains 64-character SHA-256. Hex may be decoded to a valid canonical name only if it matches a registered identity.

## The 4×4 composition

Each typed data lane crosses four identity representations:

- `numericStream`: tier, step sequence and bounded numeric evidence.
- `textStream`: canonical task/source/scope, registered alias, filename pointers and digests. The canonical name is never discarded.
- `booleanStream`: true/false/UNKNOWN, where unknown cannot self-promote.
- `aiManifestStream`: bounded candidate roles, commands and stop conditions, never executable authority.

The *other* 4×4 projection already staged in `doctrine/castTwoThreadBridgeV1.json` is four escalation tiers R0–R3 crossed with the four typed lanes. These are two views of the same data, not a 4×4×4 swarm of running agents. The eight ordered Canon states stay unchanged.

## System variable registration

Exactly eight allowed `LUHM_*` variable names are pinned to `doctrine/hostileModForge4x4V1.json` (`LUHM_STAGE`, display, rendering, input, USB, Bluetooth, debug and vendor mode). JavaScript's `planSystemVariables` merges proposed values with the existing allowlisted defaults. It never reads or changes `process.env`, starts X11, binds a device or touches a cloud host. A request to read USB/Bluetooth returns HOLD until the real OS permission and owner receipt exist. Unrecognized environment or loader flags, including `LD_PRELOAD` and `DISPLAY`, are rejected.

## JavaScript, npm, Python and SQL

`packages/luhm-canon-registry` is a **private, dependency-free ESM npm package** (source-only). It imports the GitHub Canon JSON from the repository root, validates collisions, supports read-only `help`, `list`, and `audit` commands, and exports a strict UTF-8/hex codec and validation functions. As it currently refers to a Canon JSON outside the package, it cannot be treated as a ready-to-publish standalone npm artifact. No `npm publish`, `npm install` or network action is needed for CI.

`host/api/luhmIdentityRegistry.py` independently enforces the same Canon: SHA, alias collision, help-map and typed-lane consistency. `host/api/luhmCastTwoThreadBridge.py` includes an `identitySpine` projection in two-thread plans. Read-only MCP **source definitions** `luhm_cast_identity_help` and `luhm_cast_identity_status` use the Python registry. Actual installed private Site plugin availability remains unverified.

**SQL migration policy:** the existing source-locked `host/api/typedLanesV1.sql` is not modified. The full canonical name, scope and source remain in its typed metadata and receipt paths. This layer adds no privileged schema, live migrations, binary art storage, secret tables or SQL ports.

## Local source tests

From the repository root:

```sh
python -m unittest discover -s tests -p 'testCastIdentityRegistry.py' -v
python -m unittest discover -s tests -p 'testCastTwoThreadBridge.py' -v
npm test --prefix packages/luhm-canon-registry
node packages/luhm-canon-registry/bin/cli.mjs help bs
node packages/luhm-canon-registry/bin/cli.mjs audit
```

The GitHub CAST CI gate runs both Python and JavaScript tests. It validates live file identity **within that checked-out Git tree**, but cannot attest a deployed Samsung/iOS app, updated ChatGPT Site backend, actual SQL host, active mesh worker, GitHub Release or CAST smoke. Company worker quarantine, no-auto-publish and Professor-only promotion remain in force. Apache-2.0 licensing for independently owned components is a review target; the repository's actual root `LICENSE` remains GPLv3.

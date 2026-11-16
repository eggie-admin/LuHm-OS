# @luhm-os/canon-registry (private source candidate)

Small, dependency-free ESM library used *inside the LuHm-OS GitHub repository* to map human-facing role meanings to one canonical `camelHump` ID, explicitly registered vowel-ripped alias, shorthand and reversible lower-case UTF-8 hex representation. It shares `doctrine/castIdentityHexRegistryV1.json` with Python, MCP and CAST.

The package is deliberately `private: true`, **not published** and depends on a Canon file outside the package directory. It is **not a standalone npm registry distribution** without a future approved packaging design. The LuHm-OS root license is GPLv3; this module is **not automatically Apache-2.0 relicensed**.

From the repository root:

```sh
npm test --prefix packages/luhm-canon-registry
node packages/luhm-canon-registry/bin/cli.mjs help bs
node packages/luhm-canon-registry/bin/cli.mjs help 62656c6c64616e6479536563726574617279
node packages/luhm-canon-registry/bin/cli.mjs audit
```

Expected `bs` resolution is **`belldandySecretary`**, with full human meaning and aliases. Unknown names return VERIFY, never execute. `lm` is Lum's explicitly registered vowel alias, whereas `lmesh` is the two-thread mesh shorthand; this split prevents a real alias collision.

The 4×4 matrix represents **four identity layers × four existing typed SQL lanes** (`numericStream`, `textStream`, `booleanStream`, `aiManifestStream`). The CAST escalation tiers R0–R3 remain orthogonal. SQL keeps canonical names and hashes; hex cannot grant permission, replace the Git source SHA, or act as encryption.

Environment variables are **proposals**, not live `process.env` mutations. `planSystemVariables({...})` checks only the eight `LUHM_*` keys already defined in `doctrine/hostileModForge4x4V1.json`. A proposed Bluetooth/USB value of `readOnly` still returns HOLD pending OS/device/owner consent. No command execution, database access, file import, network, npm publishing, autonomous workers or ChatGPT plugin installation occurs.

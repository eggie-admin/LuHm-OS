# LuHm-OS game-layer CAST | Astra/Astro hardening handoff

**State:** SOURCE_CANDIDATE / Professor Crown STOP. **Not** an automated Astra job, live ChatGPT plugin update, or a deployed game.

## Source and rollback

- Source authority: `eggie-admin/LuHm-OS`, draft PR #537, branch `candidate/machine-sql-hex512-20261107`.
- Pre-infrastructure rollback: `snapshot/pre-final-mutation-20261107-5eb8388e`, exact commit `5eb8388e7309cef4c90ff5fb8a854bbc11907acf`.
- Post-integration snapshot is created **only after the exact-head CI audit**. See GitHub PR for the final snapshot commit.
- Do not merge to `main`, install plugin, alter private DNS or publish game assets without Professor's final review.

## Single source game stack

1. GitHub source Canon, existing SQLite schema `host/api/machineRegistrySqliteV1.sql`. Use `tools/gameLayerSqlFixture.py` to populate **disposable in-memory** registry with 19 source components, 17 dependency edges, 19 asset digests, 512 held logical coordinates and original companion / mod research metadata. No production database connection, credentials, external asset bytes, or new database.
2. NPM frontEnd `package.json` + locked jQuery 3.7.1 dependency. Tests include `npm run test:game-layers`; no new npm dependency.
3. HTML/CSS/JavaScript `frontEnd/prototypes/gameLayerConsole/` provides a **real responsive source-console demo** with three original adult characters and seven deterministic relationship actions. It imports existing `companionAtelier/relationshipCore.mjs`. Open over an HTTP static server rooted at repository root; `file://` module fetches are not guaranteed.
4. The portable `plugins/luhm-os/plugin.json` still describes the separate manual-upload read-only ChatGPT plugin. The installed owner-private Site backend and MCP Apps widget are separate from GitHub source, with host mount/input proof still pending.
5. Godot 4 `project.godot` and `scenes/CompanionModLab.tscn` already load `scripts/game/companionModLab.gd` and the original companion profiles/rules. The web console is *not* a Godot engine running inside ChatGPT.
6. The existing `game/demo/modInspirationCatalogV1.json` lists Nexus mod references, adult costume/animation inspiration, and open asset candidates. It is a **research index**, not bundled binary donor data. Preserve existing source metadata; no claim that Cubism is installed or a third-party rig is imported.
7. CAST `0xC1` remains an **intent-only** bridge. SQL receipts cannot approve mutation, execution, plugin deployment, or Crown.

## Astra/Astro final video-game hardening queue

Perform in a separate human-invoked session, not automatically:

- Verify exact candidate SHA and green CI; independently run `python3 tools/gameLayerSqlFixture.py --source-ref <exact 40 hex>`, `npm ci --ignore-scripts && npm run check`, and existing Godot 4.7 headless smoke. Inspect SQL foreign keys and negative cases.
- Test 1048 responsive vector brand with 320px portrait mobile viewport, Samsung DeX, keyboard, touch, accessibility, reduced motion. Run actual browser WebGL / WebGPU capability checks if a renderer is introduced; never infer 3D rendering from HTML.
- For next art phase, create **owned or separately cleared** rigged `glTF 2.0 / GLB` and animation metadata, skeletal blend shapes, mobile LOD and texture budgets, deterministic character poses and camera orbits. Validate imports in Godot 4 and real Samsung hardware.
- Decide actual supported ChatGPT MCP App source, with tool invocation and client-rendered interactive widget evidence. Keep plugin backend updates and Site publishing as separately verified host actions.
- Evaluate game loop: save and restore, bounded state, input sanitization, asset-locality, node memory, draw calls, shader compatibility, character animations, motion accessibility, CPU/GPU budgets, target FPS on target hardware.
- Perform threat review: no untrusted mod execution, no sensitive user files in source, no private keys in SQL or client, local DB only, no live DNS/SSL changes, no arbitrary commands from in-chat or JSON.
- Obtain the Professor's final approval for any merge, installation, release, or external asset publication; report source-green distinct from real-device and in-chat host proof.

## Useful commands

```sh
python3 tools/gameLayerSqlFixture.py --self-test
python3 tools/machineSqlHex512Audit.py
python3 tools/localDualStackGatewayAudit.py
python3 tools/brandHexVectorAudit.py
node --test frontEnd/tests/gameLayerConsole.test.mjs
node --test frontEnd/tests/machineCastHexBridge.test.mjs
cd frontEnd && npm ci --ignore-scripts && npm run check
```

**Final gating:** `CROWN STOP`. Astra is a handoff target for the next explicit human-invoked hardening pass. Nothing runs in the background.

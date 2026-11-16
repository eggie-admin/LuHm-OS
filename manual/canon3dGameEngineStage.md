# Canon 3D game engine hardening candidate (October 21, 2026)

This branch preserves the deployed three-world First Night Circuit gameplay, Godot 4 Web export, procedural art fallbacks, and all source/canon boundaries.

## Verified source facts
- Godot 4.7 gameplay is already implemented in `scripts/main.gd` and `scripts/game/*`; no replacement engine is claimed.
- Character identities are sourced from `game/canon/CHARACTER_CANON_V1.json`; quest continuity from `game/story/firstNightQuest.json`.
- `media/goddess3d-production-matrix-v1.json` records a private Lum rig candidate and three missing reconciled goddess 3D bodies.
- No approved public game-ready GLB models are in the current GitHub tree. The private Godot Drive vault and its rights-unverified assets are not a public CDN.
- All four manifest entries are visibly unapproved; environments retain procedural geometry.

## Implementation
- `canonRuntimeAssetsV1.json` explicitly enumerates four character slots and three canonical worlds.
- `canonAssetRegistry.gd` mounts ONLY locally packaged, approved and import-proven scene resources under `res://assets/approved3d/`. It never fetches external URLs.
- `canonAssetBuildAudit.py` fails the public build for unauthorized binaries, missing manifests, path traversal, SHA mismatch, unknown licenses, improper approvals, unsafe symlinks, or oversized assets.
- GitHub Actions performs source tests; the existing Render Godot build runs the audit before any export.
- The already working Lum private rig path and goddess rehearsal flow are unchanged. A future approved character may be wired into a visual avatar via a separate verified import test.

## To use a model in public
1. Preserve the original and evidence in private Drive. Record rights/redistribution proof and visual review separately.
2. Produce a Godot 4.7 import-tested, properly rigged, optimized derivative and take its SHA-256.
3. On a candidate branch only, add the approved GLB/TSCSN to `assets/approved3d/`, replace the manifest entry with `runtimeImportProven`, `publicAllowed=true`, `importProven=true`, approved license and named human approval, exact SHA.
4. Run asset gate, Godot import/smoke tests and visual comparison. Obtain Professor release approval before public promotion. Never equate an audit passing with the actual identity/animation review.

**Do not add private Drive IDs, unapproved third-party game models, donor binaries, secrets or private original media to this public repository.** The new engine gate adds no agents, provider API calls, paid Render resources, publishing permissions or autonomous deployments. Current live Render remains rollback.
